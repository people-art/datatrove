"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GradientCard } from "@/components/ui/gradient-card";
import { KeywordInput } from "./KeywordInput";
import { PriceCard } from "./PriceCard";
import { StickyFooterCta } from "./StickyFooterCta";
import { benchmarkApi } from "@/lib/api";
import { debounce } from "@/lib/utils";
import type { DomainFormData, QuoteData } from "@/types";

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
  { value: 'small', label: 'Small (~5M tokens)', description: 'Research papers, small datasets' },
  { value: 'medium', label: 'Medium (~10M tokens)', description: 'Training smaller models' },
  { value: 'large', label: 'Large (~20M tokens)', description: 'Fine-tuning medium models' },
  { value: 'xlarge', label: 'Extra Large (~50M tokens)', description: 'Training large models' },
];

interface DomainFormProps {
  onSubmit: (formData: DomainFormData) => Promise<void>;
  isLoading: boolean;
}

export function DomainForm({ onSubmit, isLoading }: DomainFormProps) {
  const [formData, setFormData] = useState<DomainFormData>({
    domain: '',
    keywords: [],
    languages: ['English'],
    timeRange: {
      start: '2020-01-01',
      end: new Date().toISOString().split('T')[0]
    },
    qualityTier: 'standard',
    estimatedScale: '',
    email: ''
  });

  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [showExamples, setShowExamples] = useState(false);

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
    await onSubmit(formData);
  };

  const isFormValid = formData.domain.trim() && formData.keywords.length >= 2 && formData.email.trim();

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
          Create Custom Dataset
        </h1>
        <p className="text-lg text-foreground/70">
          Define your domain requirements and get a quality preview from 1M web pages
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-6">
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
                      Email Address *
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@example.com"
                      value={formData.email}
                      onChange={(e) => updateFormData({ email: e.target.value })}
                      className="h-11 mt-1"
                    />
                    <p className="text-xs text-foreground/50 mt-2">
                      We'll only use this for dataset delivery notifications.
                    </p>
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
        label={isLoading ? "Creating Preview..." : "Generate Preview (1M pages)"}
        isVisible={true}
      />

      {/* Mobile Price Card */}
      <div className="lg:hidden mt-6">
        <PriceCard quote={quote} isLoading={quoteLoading} />
      </div>
    </>
  );
}
