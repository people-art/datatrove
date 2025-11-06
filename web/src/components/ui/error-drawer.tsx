"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, Copy, Check } from 'lucide-react';
import { Button } from './button';
import { getErrorMessage, getErrorSuggestion, getTraceId } from '@/lib/fetcher';
import { useI18n } from '@/lib/i18n';

interface ErrorDrawerProps {
  error: any;
  onClose: () => void;
  isOpen: boolean;
}

export function ErrorDrawer({ error, onClose, isOpen }: ErrorDrawerProps) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);

  const errorMessage = getErrorMessage(error);
  const suggestion = getErrorSuggestion(error);
  const traceId = getTraceId(error);

  const errorDetails = {
    message: errorMessage,
    suggestion,
    traceId,
    timestamp: new Date().toISOString(),
    userAgent: typeof window !== 'undefined' ? navigator.userAgent : 'Unknown',
    url: typeof window !== 'undefined' ? window.location.href : 'Unknown',
  };

  const copyToClipboard = async () => {
    const errorJson = JSON.stringify(errorDetails, null, 2);
    try {
      await navigator.clipboard.writeText(errorJson);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll when drawer is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white dark:bg-slate-900 shadow-xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-6 w-6 text-red-500" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  {t('error')}
                </h2>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Error Message */}
              <div>
                <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
                  Error Message
                </h3>
                <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {errorMessage}
                  </p>
                </div>
              </div>

              {/* Suggestion */}
              {suggestion && (
                <div>
                  <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
                    Suggestion
                  </h3>
                  <div className="p-3 bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      {suggestion}
                    </p>
                  </div>
                </div>
              )}

              {/* Trace ID */}
              {traceId && (
                <div>
                  <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
                    {t('traceId')}
                  </h3>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
                    <code className="text-sm text-slate-800 dark:text-slate-200 font-mono">
                      {traceId}
                    </code>
                  </div>
                </div>
              )}

              {/* Timestamp */}
              <div>
                <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
                  Timestamp
                </h3>
                <div className="p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
                  <p className="text-sm text-slate-800 dark:text-slate-200 font-mono">
                    {errorDetails.timestamp}
                  </p>
                </div>
              </div>

              {/* Technical Details */}
              <div>
                <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
                  Technical Details
                </h3>
                <div className="p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg">
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-slate-700 dark:text-slate-300">URL:</span>
                      <span className="ml-2 text-slate-600 dark:text-slate-400 font-mono text-xs break-all">
                        {errorDetails.url}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-slate-700 dark:text-slate-300">User Agent:</span>
                      <span className="ml-2 text-slate-600 dark:text-slate-400 font-mono text-xs break-all">
                        {errorDetails.userAgent}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-slate-200 dark:border-slate-700 p-6">
              <div className="flex gap-3">
                <Button
                  onClick={copyToClipboard}
                  variant="outline"
                  className="flex-1"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy Details
                    </>
                  )}
                </Button>
                <Button onClick={onClose} className="flex-1">
                  Close
                </Button>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 text-center">
                {t('contactSupport')}
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
