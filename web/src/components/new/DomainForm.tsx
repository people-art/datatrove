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
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { EmailField } from "@/components/ui/email-field";
import { KeywordInput } from "./KeywordInput";
import { PriceCard } from "./PriceCard";
import { StickyFooterCta } from "./StickyFooterCta";
import { useQuote, useCreateBenchmarkJob } from "@/hooks/use-api";
import { benchmarkApi, emailApi } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { getErrorMessage, getErrorSuggestion, getTraceId, api, API_BASE } from "@/lib/fetcher";
import { debounce } from "@/lib/utils";
import type { QuoteData, DomainFormData } from "@/types";
import type { Ontology } from "@/hooks/use-api";

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
  onSubmit: (formData: DomainFormData) => void;
}

export function DomainForm({ onSubmit, isLoading }: DomainFormProps & { isLoading?: boolean }) {
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
  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);

  // Ontology hooks - manual trigger only
  const { t, language } = useI18n();
  const [ontology, setOntology] = useState<Ontology | null>(null);
  const [ontoLoading, setOntoLoading] = useState(false);
  const [ontoError, setOntoError] = useState<string | null>(null);

  // API hooks
  const quoteMutation = useQuote();
  const createJobMutation = useCreateBenchmarkJob();


  useEffect(() => {
    fetchQuote(formData);
  }, [formData.domain, formData.keywords, formData.languages, formData.qualityTier, formData.estimatedScale, formData.timeRange]);

  // Reset email validation when email changes
  useEffect(() => {
    if (formData.email) {
      validateEmailDebounced(formData.email);
    } else {
      setEmailValid(false);
      setEmailValidation(null);
    }
  }, [formData.email]);

  const updateFormData = (updates: Partial<typeof formData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
    setError(null);
  };

  // Manual Ontology generation
  const generateOntology = async () => {
    console.log('generateOntology called with domain:', formData.domain, 'language:', language);

    if (!formData.domain.trim()) {
      console.log('Domain is empty');
      setOntoError(t("new.ontology.error_empty_domain"));
      return;
    }

    if (formData.domain.trim().length < 3) {
      console.log('Domain too short');
      setOntoError(t("new.ontology.error_domain_too_short"));
      return;
    }

    try {
      console.log('Starting ontology generation...');
      setOntoLoading(true);
      setOntoError(null);

      const params = { domain: formData.domain.trim(), locale: language };
      console.log('Making API call with params:', params);

      console.log('About to make direct fetch call...');

      // Try direct fetch without axios
      let timeoutId: NodeJS.Timeout | null = null;
      try {
        console.log('Making direct fetch call...');
        const controller = new AbortController();
        timeoutId = setTimeout(() => {
          console.log('Request timed out, aborting...');
          controller.abort();
        }, 60000); // 60 second timeout

        const response = await fetch(`${API_BASE}/benchmark/ontology/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(params),
          signal: controller.signal,
        });

        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
          console.log('Timeout cleared successfully');
        }
        console.log('Fetch response received:', response.status, response.statusText);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Fetch failed with status:', response.status, errorText);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Fetch API call successful, received data keys:', Object.keys(data));

        setOntology(data);
        console.log('Ontology state updated successfully');
        return;
      } catch (fetchError: any) {
        console.error('Direct fetch failed:', fetchError.message);
        console.error('Error name:', fetchError.name);
        console.error('Error stack:', fetchError.stack);
        // Clear timeout if it exists
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
          console.log('Timeout cleared in catch block');
        }
      }

      // If we get here, all methods failed
      throw new Error('All API call methods failed');
    } catch (error: any) {
      console.error('Ontology generation failed:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.status,
        data: error.response?.data
      });
      setOntoError(error.response?.data?.error?.message || t("new.ontology.error_generic"));
    } finally {
      setOntoLoading(false);
      console.log('Ontology loading finished');
    }
  };

  // Form validation
  const timeRangeValid = new Date(formData.timeRange.end) > new Date(formData.timeRange.start) &&
                        (new Date(formData.timeRange.end).getTime() - new Date(formData.timeRange.start).getTime()) <= (5 * 365 * 24 * 60 * 60 * 1000); // 5 years
  const isFormValid = formData.domain.trim() && timeRangeValid && emailValid;

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
      setEmailValid(false);
      return;
    }

    try {
      setEmailValidating(true);
      const result = await emailApi.validateEmail(email);
      setEmailValidation({
        isValid: result.isValid,
        checks: result.checks
      });
      setEmailValid(result.isValid);
    } catch (error) {
      console.error('Email validation failed:', error);
      setEmailValidation(null);
      setEmailValid(false);
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
        estimatedScale: data.estimatedScale && data.estimatedScale.trim() ? { docs: parseInt(data.estimatedScale) || 1000000 } : undefined,
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
        estimated_scale: formData.estimatedScale ? formData.estimatedScale.toString() : undefined,
        email: formData.email
      };

      const result = await createJobMutation.mutateAsync(jobData);

      // Track the job ID for system stats
      if (typeof window !== 'undefined') {
        const trackedJobs = JSON.parse(localStorage.getItem('tracked_jobs') || '[]');
        if (!trackedJobs.includes(result.jobId)) {
          trackedJobs.push(result.jobId);
          localStorage.setItem('tracked_jobs', JSON.stringify(trackedJobs));
        }
      }

      router.push("/dashboard");
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      const suggestion = getErrorSuggestion(err);
      const traceId = getTraceId(err);

      setError(`${errorMessage}${suggestion ? ` ${suggestion}` : ''}${traceId ? ` (${t('traceId')}: ${traceId})` : ''}`);
    }
  };

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
    <div className="space-y-8">
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(260px,1fr)] gap-6 items-start">
        {/* Left: Form */}
        <div className="space-y-4">
          {/* Domain & Topic Section */}
          <section className="rounded-2xl border border-border/60 bg-card/70 p-5 space-y-3">
            <header className="flex items-center justify-between gap-2">
              <h2 className="text-sm font-medium">领域与主题</h2>
              <span className="text-[10px] text-muted-foreground">步骤 1 / 4</span>
            </header>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  领域/主题 *
                </label>
                <input
                  type="text"
                  placeholder="例如：人工智能、气候变化、医疗研究"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                  value={formData.domain}
                  onChange={(e) => updateFormData({ domain: e.target.value })}
                />
              </div>
            </div>
          </section>

          {/* Ontology Section */}
          <OntologyCard
            ontology={ontology}
            isLoading={ontoLoading}
            isError={ontoError}
            onGenerate={generateOntology}
            hasDomain={!!formData.domain.trim() && formData.domain.trim().length >= 3}
            t={t}
          />

          {/* Languages & Time Section */}


          <section className="rounded-2xl border border-border/60 bg-card/70 p-5 space-y-3">
            <header className="flex items-center justify-between gap-2">
              <h2 className="text-sm font-medium">语言与时间范围</h2>
              <span className="text-[10px] text-muted-foreground">步骤 2 / 4</span>
            </header>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  语言
                </label>
                <select
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                  value={formData.languages[0] || ''}
                  onChange={(e) => updateFormData({ languages: [e.target.value] })}
                >
                  <option value="English">English</option>
                  <option value="Chinese">中文</option>
                  <option value="Spanish">Español</option>
                  <option value="French">Français</option>
                  <option value="German">Deutsch</option>
                </select>
              </div>
              <div className="md:col-span-2 grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                    开始日期
                  </label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                    value={formData.timeRange.start}
                    onChange={(e) => updateFormData({
                      timeRange: { ...formData.timeRange, start: e.target.value }
                    })}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                    结束日期
                  </label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                    value={formData.timeRange.end}
                    onChange={(e) => updateFormData({
                      timeRange: { ...formData.timeRange, end: e.target.value }
                    })}
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Quality & Scale Section */}


          <section className="rounded-2xl border border-border/60 bg-card/70 p-5 space-y-3">
            <header className="flex items-center justify-between gap-2">
              <h2 className="text-sm font-medium">质量与规模</h2>
              <span className="text-[10px] text-muted-foreground">步骤 3 / 4</span>
            </header>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-3 block">
                  质量等级
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'basic', label: '基础', desc: '快速处理，基本过滤' },
                    { value: 'standard', label: '标准', desc: '平衡质量与速度' },
                    { value: 'premium', label: '高级', desc: '最高质量，深度过滤' }
                  ].map((tier) => (
                    <button
                      key={tier.value}
                      onClick={() => updateFormData({ qualityTier: tier.value as any })}
                      className={`p-3 rounded-lg border text-left transition-colors ${
                        formData.qualityTier === tier.value
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <div className="font-medium text-sm">{tier.label}</div>
                      <div className="text-xs text-muted-foreground mt-1">{tier.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  预估规模 (百万 tokens)
                </label>
                <input
                  type="number"
                  placeholder="1-1000"
                  min="1"
                  max="1000"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                  value={formData.estimatedScale}
                  onChange={(e) => updateFormData({ estimatedScale: e.target.value })}
                />
              </div>
            </div>
          </section>

          {/* Email Section */}


          <section className="rounded-2xl border border-border/60 bg-card/70 p-5 space-y-3">
            <header className="flex items-center justify-between gap-2">
              <h2 className="text-sm font-medium">联系信息</h2>
              <span className="text-[10px] text-muted-foreground">步骤 4 / 4</span>
            </header>
            <div>
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                邮箱地址 *
              </label>
              <input
                type="email"
                placeholder="your.email@example.com"
                className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                value={formData.email}
                onChange={(e) => updateFormData({ email: e.target.value })}
              />
              {emailValidation && (
                <div className="mt-2 text-xs">
                  {emailValidation.isValid ? (
                    <span className="text-green-600">✓ 邮箱验证通过</span>
                  ) : (
                    <span className="text-red-600">✗ 邮箱格式无效</span>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Right: Pricing Sidebar */}
        <div className="space-y-6">
          {/* Estimated Price */}
          <div className="sticky top-24">
            <div className="rounded-2xl border border-border/60 bg-card/70 p-5 space-y-4">
              <h3 className="font-medium">预估价格</h3>

              {quote ? (
                <div className="space-y-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">
                      {quote.currency} {quote.total?.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      基于你的配置估算
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span>基础价格</span>
                      <span>{quote.currency} {quote.subtotal?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>税费 (8%)</span>
                      <span>{quote.currency} {quote.tax?.toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t text-xs text-muted-foreground">
                    {quote.pricing_notes}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-muted-foreground text-sm">
                    填写表单后显示价格预估
                  </div>
                </div>
              )}

              {/* Benchmark Status */}
              <div className="pt-4 border-t space-y-3">
                <h4 className="font-medium text-sm">Benchmark 状态</h4>
                <div className="text-xs text-muted-foreground">
                  准备运行 100 万页本地预览
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>本地预览 • 1 个节点</span>
                </div>
              </div>
            </div>

            {/* CTA Button */}
            <div className="mt-4">
              <button
                onClick={() => {
                  if (isFormValid && !isLoading) {
                    onSubmit(formData);
                  }
                }}
                disabled={!isFormValid || isLoading}
                className={`w-full py-3 px-4 rounded-lg font-medium text-sm transition-colors ${
                  isFormValid && !isLoading
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'bg-muted text-muted-foreground cursor-not-allowed'
                }`}
              >
                {isLoading ? '创建中...' : '确认并运行 Benchmark'}
              </button>
              <div className="text-xs text-muted-foreground text-center mt-2">
                无需预付费用 • Benchmark 完成后确认支付
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Ontology Card Component
function OntologyCard({ ontology, isLoading, isError, onGenerate, hasDomain, t }: {
  ontology?: Ontology | null;
  isLoading: boolean;
  isError: boolean | string;
  onGenerate: () => void;
  hasDomain: boolean;
  t: (key: string) => string;
}) {
  //console.log('OntologyCard render:', { ontology: !!ontology, isLoading, isError, hasDomain });

  return (
    <Card className="rounded-2xl border border-border/60 bg-card/70">
      <CardHeader className="flex items-center justify-between">
        <CardTitle className="text-sm font-medium">{t("new.ontology.title")}</CardTitle>
        <div className="text-xs text-muted-foreground">
          {isLoading ? t("new.ontology.generating") :
           ontology ? t("new.ontology.generated") :
           t("new.ontology.ready")}
        </div>
      </CardHeader>
      <CardContent>
        {/* Generate Button - only show when no ontology and not loading */}
        {!ontology && !isLoading && (
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground mb-4">
              {hasDomain ? t("new.ontology.ready_to_generate") : t("new.ontology.enter_domain_first")}
            </p>
            <Button
              onClick={onGenerate}
              disabled={!hasDomain || isLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {t("new.ontology.generate_button")}
            </Button>
          </div>
        )}

        {isLoading && <OntologySkeleton />}

        {isError && typeof isError === 'string' && (
          <ErrorInline
            title={t("new.ontology.error_title")}
            description={isError}
            actionLabel={t("common.retry")}
            onAction={onGenerate}
          />
        )}

        {!isLoading && ontology && (
          <>
            <p className="text-sm leading-6 text-neutral-700 mb-4">{ontology.summary}</p>
            <div className="grid md:grid-cols-3 gap-4">
              <ChipColumn title={t("new.ontology.concepts")} items={ontology.concepts} />
              <ChipColumn title={t("new.ontology.entities")} items={ontology.entities} />
              <ChipColumn title={t("new.ontology.intents")} items={ontology.intents} />
            </div>
            <div className="mt-6 grid md:grid-cols-2 gap-4">
              <ChipColumn title={t("new.ontology.positive_keywords")} items={ontology.positive_keywords} variant="success" />
              <ChipColumn title={t("new.ontology.negative_keywords")} items={ontology.negative_keywords} variant="destructive" />
            </div>
            {ontology.examples?.length ? (
              <div className="mt-6">
                <h4 className="text-sm font-medium mb-2">{t("new.ontology.examples")}</h4>
                <ul className="space-y-1 text-sm">
                  {ontology.examples.map((ex, i) => (
                    <li key={i} className="truncate">
                      {ex.url ? (
                        <a href={ex.url} className="underline underline-offset-2" target="_blank" rel="noreferrer">
                          {ex.title}
                        </a>
                      ) : (
                        ex.title
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}

function OntologySkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
      <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
      <div className="grid md:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="space-y-2">
            <div className="h-3 bg-gray-200 rounded animate-pulse"></div>
            <div className="flex flex-wrap gap-1">
              {[1, 2, 3].map(j => (
                <div key={j} className="h-6 w-16 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ChipColumn({ title, items, variant }: { title: string; items?: string[]; variant?: "success" | "destructive" }) {
  if (!items?.length) return null;
  return (
    <div>
      <h4 className="text-sm font-medium mb-2">{title}</h4>
      <div className="flex flex-wrap gap-1">
        {items.map((item, i) => (
          <span
            key={i}
            className={`inline-block px-2 py-1 text-xs rounded ${
              variant === "success" ? "bg-green-100 text-green-800" :
              variant === "destructive" ? "bg-red-100 text-red-800" :
              "bg-gray-100 text-gray-800"
            }`}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function ErrorInline({ title, actionLabel, onAction }: { title: string; actionLabel: string; onAction: () => void }) {
  return (
    <div className="text-center py-8">
      <div className="text-sm text-muted-foreground mb-2">{title}</div>
      <Button variant="outline" size="sm" onClick={onAction}>
        {actionLabel}
      </Button>
    </div>
  );
}
