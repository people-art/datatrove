"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Sparkles, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GradientCard } from "@/components/ui/gradient-card";
import { EmailField } from "@/components/ui/email-field";
import { KeywordInput } from "./KeywordInput";
import { PriceCard } from "./PriceCard";
import { StickyFooterCta } from "./StickyFooterCta";
import { useQuote, useCreateBenchmarkJob } from "@/hooks/use-api";
import { useI18n } from "@/lib/i18n";
import { getErrorMessage, getErrorSuggestion, getTraceId } from "@/lib/fetcher";
import { debounce } from "@/lib/utils";

const LANGUAGE_OPTIONS = [
  'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Portuguese'
];

const QUALITY_TIERS = [
  {
    value: 'basic',
    label: 'Basic',
    description: 'Standard filtering, ~70% quality',
    price: 'Most affordable option for basic research'
  },
  {
    value: 'standard',
    label: 'Standard',
    description: 'Enhanced filtering, ~85% quality',
    price: 'Balanced quality and cost for most use cases'
  },
  {
    value: 'premium',
    label: 'Premium',
    description: 'LLM-assisted filtering, ~95% quality',
    price: 'Highest quality for production AI models'
  }
];

const DOMAIN_EXAMPLES = [
  'artificial intelligence', 'climate change', 'quantum computing', 'renewable energy',
  'medical research', 'financial markets', 'education technology', 'autonomous vehicles'
];

const SCALE_OPTIONS = [
  { value: '', label: 'Auto-detect', description: 'Let us estimate based on your domain' },
  { value: '100000', label: '100k docs (~500k tokens)', description: 'Small research datasets' },
  { value: '1000000', label: '1M docs (~5M tokens)', description: 'Medium research projects' },
  { value: '10000000', label: '10M docs (~50M tokens)', description: 'Production-ready datasets' },
];

interface DomainFormProps {
  onSubmit?: (formData: any) => void;
}

export function DomainForm({ onSubmit }: DomainFormProps) {
  const { t } = useI18n();
  const router = useRouter();

  const [formData, setFormData] = useState({
    domain: '',
    keywords: [] as string[],
    languages: ['English'] as string[],
    timeRange: {
      start: '2020-01-01',
      end: new Date().toISOString().split('T')[0]
    },
    qualityTier: 'standard' as 'basic' | 'standard' | 'premium',
    estimatedScale: '',
    email: ''
  });

  const [emailValid, setEmailValid] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API hooks
  const quoteMutation = useQuote();
  const createJobMutation = useCreateBenchmarkJob();

  // Debounced quote fetching
  const fetchQuoteDebounced = debounce(async (data: typeof formData) => {
    if (!data.domain.trim() || data.keywords.length < 2) {
      return;
    }

    const quoteRequest = {
      domain: data.domain,
      keywords: data.keywords,
      languages: data.languages,
      startDate: data.timeRange.start,
      endDate: data.timeRange.end,
      qualityTier: data.qualityTier,
      estimatedScale: data.estimatedScale ? { docs: parseInt(data.estimatedScale) } : undefined,
    };

    try {
      await quoteMutation.mutateAsync(quoteRequest);
    } catch (err: any) {
      console.error('Quote fetch failed:', err);
    }
  }, 1000);

  useEffect(() => {
    fetchQuoteDebounced(formData);
  }, [formData.domain, formData.keywords, formData.languages, formData.qualityTier, formData.estimatedScale, formData.timeRange]);

  const updateFormData = (updates: Partial<typeof formData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
    setError(null);
  };

  // Form validation
  const keywordsValid = formData.keywords.length >= 2;
  const timeRangeValid = new Date(formData.timeRange.end) > new Date(formData.timeRange.start) &&
                        (new Date(formData.timeRange.end).getTime() - new Date(formData.timeRange.start).getTime()) <= (5 * 365 * 24 * 60 * 60 * 1000); // 5 years
  const isFormValid = formData.domain.trim() && keywordsValid && timeRangeValid && emailValid;

  // Email validation state
  const [emailValidating, setEmailValidating] = useState(false);
  const [emailValidation, setEmailValidation] = useState<{
    isValid: boolean;
    checks: Record<string, boolean>;
  } | null>(null);

  // Debounced email validation
  const validateEmailDebounced = debounce(async (email: string) => {
    if (!email || !/^[^@]+@[^@]+\.[^@]+$/.test(email)) {
      setEmailValidation(null);
      return;
    }

    try {
      setEmailValidating(true);
      const result = await emailApi.validateEmail(email);
      setEmailValidation({
        isValid: result.isValid,
        checks: result.checks
      });
    } catch (error) {
      console.error('Email validation failed:', error);
      setEmailValidation(null);
    } finally {
      setEmailValidating(false);
    }
  }, 500);

  // Debounced quote fetching
  const fetchQuote = debounce(async (data: DomainFormData) => {
    if (!data.domain.trim() || data.keywords.length === 0) {
      setQuote(null);
      return;
    }

    try {
      setQuoteLoading(true);

      // Convert form data to quote request format
      const quoteRequest = {
        domain: data.domain,
        keywords: data.keywords,
        languages: data.languages,
        startDate: data.timeRange.start,
        endDate: data.timeRange.end,
        qualityTier: data.qualityTier,
        estimatedScale: data.estimatedScale ? { docs: parseInt(data.estimatedScale) || undefined } : undefined,
      };

      const quoteResponse = await benchmarkApi.createQuote(quoteRequest);

      // Convert quote response to display format
      const displayQuote: QuoteData = {
        currency: quoteResponse.currency,
        estimated_tokens: 10000000, // Placeholder - would be calculated
        subtotal: (quoteResponse.estimate.low + quoteResponse.estimate.high) / 2,
        tax: ((quoteResponse.estimate.low + quoteResponse.estimate.high) / 2) * 0.08,
        total: ((quoteResponse.estimate.low + quoteResponse.estimate.high) / 2) * 1.08,
        pricing_notes: `Quote ID: ${quoteResponse.quoteId}. Estimate only. Benchmark preview is free. Final quote adjusts with actual coverage & quality.`,
        breakdown: {
          base_price_per_million: quoteResponse.unit.amount,
          language_factor: 1.0,
          domain_factor: 1.0,
          time_factor: 1.0,
          adjusted_price_per_million: quoteResponse.unit.amount,
        }
      };

      setQuote(displayQuote);
    } catch (error) {
      console.error('Failed to fetch quote:', error);
    } finally {
      setQuoteLoading(false);
    }
  }, 1000);

  useEffect(() => {
    fetchQuote(formData);
  }, [formData.domain, formData.keywords, formData.languages, formData.qualityTier, formData.estimatedScale]);

  const updateFormData = (updates: Partial<DomainFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isFormValid) return;

    try {
      const jobData = {
        domain: formData.domain,
        keywords: formData.keywords,
        languages: formData.languages,
        time_range: formData.timeRange,
        quality_tier: formData.qualityTier,
        estimated_scale: formData.estimatedScale ? parseInt(formData.estimatedScale) : undefined,
        email: formData.email
      };

      const result = await createJobMutation.mutateAsync(jobData);
      router.push(`/preview/${result.jobId}`);
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      const suggestion = getErrorSuggestion(err);
      const traceId = getTraceId(err);

      setError(`${errorMessage}${suggestion ? ` ${suggestion}` : ''}${traceId ? ` (${t('traceId')}: ${traceId})` : ''}`);
    }
  };

  const isFormValid = formData.domain.trim() &&
    formData.keywords.length >= 2 &&
    formData.email.trim() &&
    emailValidation?.isValid;

  const loadExampleKeywords = (domain: string) => {
    const examples: Record<string, string[]> = {
      'artificial intelligence': ['machine learning', 'neural networks', 'deep learning', 'AI ethics', 'computer vision'],
      'climate change': ['global warming', 'carbon emissions', 'renewable energy', 'climate policy', 'sustainability'],
      'medical research': ['clinical trials', 'drug development', 'patient care', 'medical imaging', 'biomarkers'],
      'financial markets': ['trading', 'investments', 'market analysis', 'risk management', 'portfolio optimization'],
    };

    const keywords = examples[domain.toLowerCase()] || ['research', 'analysis', 'data', 'insights'];
    updateFormData({ domain, keywords });
  };

  return (
    <>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-4">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight mb-2">
          {t('createDataset')}
        </h1>
        <p className="text-lg text-foreground/70">
          {t('generatePreview')}
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-800 dark:text-red-200">
                    {t('error')}
                  </p>
                  <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                    {error}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Domain & Topic */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <GradientCard>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">Domain & Topic</h3>
                    <p className="text-sm text-foreground/60">What area do you want to collect data about?</p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="domain" className="text-sm font-medium text-foreground/80">
                        Domain/Topic *
                      </Label>
                      <Input
                        id="domain"
                        placeholder="e.g., artificial intelligence, climate change, quantum computing"
                        value={formData.domain}
                        onChange={(e) => updateFormData({ domain: e.target.value })}
                        className="h-11 mt-1"
                      />
                      <p className="text-xs text-foreground/50 mt-2">
                        Examples: {DOMAIN_EXAMPLES.slice(0, 4).join(', ')}
                        <button
                          type="button"
                          onClick={() => setShowExamples(!showExamples)}
                          className="ml-1 text-primary hover:underline"
                        >
                          {showExamples ? 'hide' : 'show more'}
                        </button>
                      </p>

                      {showExamples && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-2 flex flex-wrap gap-2"
                        >
                          {DOMAIN_EXAMPLES.map(example => (
                            <button
                              key={example}
                              type="button"
                              onClick={() => loadExampleKeywords(example)}
                              className="text-xs px-2 py-1 rounded-md bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                            >
                              {example}
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </div>

                    <div>
                      <Label className="text-sm font-medium text-foreground/80">
                        Keywords * <span className="text-xs text-foreground/50">(at least 2)</span>
                      </Label>
                      <div className="mt-1">
                        <KeywordInput
                          value={formData.keywords}
                          onChange={(keywords) => updateFormData({ keywords })}
                          placeholder="Add relevant keywords for better filtering..."
                          maxKeywords={64}
                        />
                      </div>
                      <p className="text-xs text-foreground/50 mt-2">
                        Separate with commas or paste a list. More specific keywords = better results.
                      </p>
                    </div>
                  </div>
                </div>
              </GradientCard>
            </motion.div>

            {/* Language & Time */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.2 }}
            >
              <GradientCard>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">Language & Time Range</h3>
                    <p className="text-sm text-foreground/60">Specify the content scope for your dataset</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium text-foreground/80">Languages</Label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {LANGUAGE_OPTIONS.map(lang => (
                          <button
                            key={lang}
                            type="button"
                            onClick={() => {
                              const newLangs = formData.languages.includes(lang)
                                ? formData.languages.filter(l => l !== lang)
                                : [...formData.languages, lang];
                              updateFormData({ languages: newLangs });
                            }}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                              formData.languages.includes(lang)
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted hover:bg-muted/80 text-foreground/70'
                            }`}
                          >
                            {lang}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="start-date" className="text-sm font-medium text-foreground/80">
                          Start Date
                        </Label>
                        <Input
                          id="start-date"
                          type="date"
                          value={formData.timeRange.start}
                          onChange={(e) => updateFormData({
                            timeRange: { ...formData.timeRange, start: e.target.value }
                          })}
                          className="h-11 mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="end-date" className="text-sm font-medium text-foreground/80">
                          End Date
                        </Label>
                        <Input
                          id="end-date"
                          type="date"
                          value={formData.timeRange.end}
                          min={formData.timeRange.start}
                          onChange={(e) => updateFormData({
                            timeRange: { ...formData.timeRange, end: e.target.value }
                          })}
                          className="h-11 mt-1"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </GradientCard>
            </motion.div>

            {/* Quality & Scale */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.3 }}
            >
              <GradientCard>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">Quality & Scale</h3>
                    <p className="text-sm text-foreground/60">Choose the quality level and expected dataset size</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium text-foreground/80">Quality Tier</Label>
                      <div className="mt-2 space-y-2">
                        {QUALITY_TIERS.map(tier => (
                          <button
                            key={tier.value}
                            type="button"
                            onClick={() => updateFormData({ qualityTier: tier.value as "basic" | "standard" | "premium" })}
                            className={`w-full p-4 rounded-xl border text-left transition-all ${
                              formData.qualityTier === tier.value
                                ? 'border-primary bg-primary/5'
                                : 'border-line hover:border-primary/50'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium">{tier.label}</span>
                              {formData.qualityTier === tier.value && (
                                <Sparkles className="h-4 w-4 text-primary" />
                              )}
                            </div>
                            <p className="text-sm text-foreground/70 mb-1">{tier.description}</p>
                            <p className="text-xs text-foreground/50">{tier.price}</p>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="scale" className="text-sm font-medium text-foreground/80">
                        Estimated Scale
                      </Label>
                      <select
                        id="scale"
                        value={formData.estimatedScale}
                        onChange={(e) => updateFormData({ estimatedScale: e.target.value })}
                        className="w-full h-11 mt-1 px-3 rounded-xl border border-line bg-background text-sm focus:border-primary focus:outline-none"
                      >
                        {SCALE_OPTIONS.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label} - {option.description}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </GradientCard>
            </motion.div>

            {/* Contact */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.4 }}
            >
              <GradientCard>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">Contact Information</h3>
                    <p className="text-sm text-foreground/60">We'll send you delivery updates and dataset access</p>
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-sm font-medium text-foreground/80">
                      {t('email')} *
                    </Label>
                    <EmailField
                      value={formData.email}
                      onChange={(value) => updateFormData({ email: value })}
                      onValidationChange={setEmailValid}
                      placeholder="your.email@example.com"
                      className="mt-1"
                    />
                    <p className="text-xs text-foreground/50 mt-2">
                      We'll only use this for dataset delivery notifications.
                    </p>

                    {/* Email validation status */}
                    {emailValidating && (
                      <p className="text-xs text-foreground/70 mt-1 flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Validating email...
                      </p>
                    )}

                    {emailValidation && !emailValidating && (
                      <div className="mt-2 space-y-1">
                        {emailValidation.isValid ? (
                          <p className="text-xs text-accent flex items-center gap-1">
                            <CheckCircle className="h-3 w-3" />
                            Email looks good
                          </p>
                        ) : (
                          <p className="text-xs text-danger flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            Email validation failed
                          </p>
                        )}

                        {/* Show specific validation checks */}
                        <div className="text-xs space-y-0.5">
                          {Object.entries(emailValidation.checks).map(([check, passed]) => (
                            <div key={check} className={`flex items-center gap-1 ${passed ? 'text-accent' : 'text-danger'}`}>
                              <div className={`h-1 w-1 rounded-full ${passed ? 'bg-accent' : 'bg-danger'}`} />
                              {check.replace(/([A-Z])/g, ' $1').toLowerCase()}: {passed ? '✓' : '✗'}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </GradientCard>
            </motion.div>
          </form>
        </div>

        {/* Price Card - Desktop */}
        <div className="hidden lg:block">
          <PriceCard quote={quote} isLoading={quoteLoading} />
        </div>
      </div>

      {/* Sticky Footer CTA */}
      <StickyFooterCta
        disabled={!isFormValid || isLoading}
        onClick={() => {
          if (isFormValid && !isLoading) {
            onSubmit(formData);
          }
        }}
        label={createJobMutation.isPending ? t('processing') : t('generatePreview')}
        isVisible={true}
      />

      {/* Mobile Price Card */}
      <div className="lg:hidden mt-6">
        <PriceCard quote={quote} isLoading={quoteLoading} />
      </div>
    </>
  );
}
