"use client";

import { useState, useEffect } from 'react';
import { Check, X, Loader2, AlertTriangle } from 'lucide-react';
import { Input } from './input';
import { useEmailValidation } from '@/hooks/use-api';
import { useI18n } from '@/lib/i18n';

export type EmailValidationState =
  | 'idle'
  | 'format_ok'
  | 'mx_checking'
  | 'mx_ok'
  | 'smtp_checking'
  | 'smtp_ok'
  | 'error'
  | 'disposable_blocked';

interface EmailFieldProps {
  value: string;
  onChange: (value: string) => void;
  onValidationChange?: (isValid: boolean) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function EmailField({
  value,
  onChange,
  onValidationChange,
  placeholder,
  disabled,
  className
}: EmailFieldProps) {
  const { t } = useI18n();
  const [validationState, setValidationState] = useState<EmailValidationState>('idle');
  const [hasBlurred, setHasBlurred] = useState(false);

  const validateMutation = useEmailValidation();

  // Basic format validation
  const isFormatValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

  // Trigger validation on blur
  const handleBlur = async () => {
    setHasBlurred(true);

    if (!value.trim()) {
      setValidationState('idle');
      onValidationChange?.(false);
      return;
    }

    if (!isFormatValid) {
      setValidationState('error');
      onValidationChange?.(false);
      return;
    }

    setValidationState('format_ok');

    try {
      // Start MX check
      setValidationState('mx_checking');

      const result = await validateMutation.mutateAsync(value);

      if (result.checks.disposable_domain) {
        setValidationState('disposable_blocked');
        onValidationChange?.(false);
        return;
      }

      if (!result.checks.mx_records) {
        setValidationState('error');
        onValidationChange?.(false);
        return;
      }

      setValidationState('mx_ok');

      // Check SMTP if MX is OK
      if (result.checks.smtp_connection) {
        setValidationState('smtp_checking');
        setTimeout(() => setValidationState('smtp_ok'), 500);
      }

      onValidationChange?.(result.isValid);

    } catch (error) {
      setValidationState('error');
      onValidationChange?.(false);
    }
  };

  const handleChange = (newValue: string) => {
    onChange(newValue);

    // Reset validation state when typing
    if (hasBlurred && validationState !== 'idle') {
      setValidationState('idle');
      onValidationChange?.(false);
    }
  };

  const getValidationIcon = () => {
    switch (validationState) {
      case 'format_ok':
      case 'mx_ok':
      case 'smtp_ok':
        return <Check className="h-4 w-4 text-green-500" />;
      case 'mx_checking':
      case 'smtp_checking':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'error':
      case 'disposable_blocked':
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getValidationMessage = () => {
    switch (validationState) {
      case 'format_ok':
        return t('formatOK');
      case 'mx_checking':
        return t('mxChecking');
      case 'mx_ok':
        return t('mxOK');
      case 'smtp_checking':
        return t('smtpChecking');
      case 'smtp_ok':
        return t('smtpOK');
      case 'disposable_blocked':
        return t('disposableBlocked');
      case 'error':
        return 'Invalid email address';
      default:
        return '';
    }
  };

  const isValid = validationState === 'mx_ok' || validationState === 'smtp_ok';

  return (
    <div className={className}>
      <div className="relative">
        <Input
          type="email"
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          className={`pr-10 ${
            hasBlurred && !isValid && validationState !== 'idle'
              ? 'border-red-500 focus:border-red-500'
              : hasBlurred && isValid
              ? 'border-green-500 focus:border-green-500'
              : ''
          }`}
          aria-describedby={hasBlurred ? "email-validation" : undefined}
        />
        {hasBlurred && validationState !== 'idle' && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            {getValidationIcon()}
          </div>
        )}
      </div>

      {hasBlurred && validationState !== 'idle' && getValidationMessage() && (
        <p
          id="email-validation"
          className={`mt-1 text-sm ${
            isValid
              ? 'text-green-600 dark:text-green-400'
              : validationState === 'disposable_blocked'
              ? 'text-orange-600 dark:text-orange-400'
              : 'text-red-600 dark:text-red-400'
          }`}
        >
          {getValidationMessage()}
        </p>
      )}
    </div>
  );
}
