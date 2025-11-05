'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { QuoteCard } from '@/components/quote-card';
import { KeywordInput } from '@/components/keyword-input';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { benchmarkApi } from '@/lib/api';
import { debounce } from '@/lib/utils';
import type { DomainFormData, QuoteData } from '@/types';

const LANGUAGE_OPTIONS = [
  'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Portuguese'
];

const QUALITY_TIERS = [
  { value: 'basic', label: 'Basic', description: 'Standard filtering, ~70% quality' },
  { value: 'standard', label: 'Standard', description: 'Enhanced filtering, ~85% quality' },
  { value: 'premium', label: 'Premium', description: 'LLM-assisted filtering, ~95% quality' }
];

const DOMAIN_EXAMPLES = [
  'artificial intelligence', 'climate change', 'quantum computing', 'renewable energy',
  'medical research', 'financial markets', 'education technology', 'autonomous vehicles'
];

export default function NewDatasetPage() {
  const router = useRouter();
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
  const [loading, setLoading] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);

  // Debounced quote fetching
  const fetchQuote = debounce(async (jobId: string) => {
    if (!jobId) return;
    try {
      setQuoteLoading(true);
      const quoteData = await benchmarkApi.getQuote(jobId);
      setQuote(quoteData);
    } catch (error) {
      console.error('Failed to fetch quote:', error);
    } finally {
      setQuoteLoading(false);
    }
  }, 1000);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.domain.trim() || !formData.email.trim()) {
      alert('Please fill in required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await benchmarkApi.createJob(formData);
      router.push(`/preview/${response.jobId}`);
    } catch (error) {
      console.error('Failed to create benchmark job:', error);
      alert('Failed to create benchmark job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (updates: Partial<DomainFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create New Dataset</h1>
            <p className="text-gray-600">Define your domain requirements and get a quality preview</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Form */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Domain */}
              <Card>
                <CardHeader>
                  <CardTitle>Domain & Topic</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="domain">Domain/Topic *</Label>
                    <Input
                      id="domain"
                      placeholder="e.g., artificial intelligence, climate change, quantum computing"
                      value={formData.domain}
                      onChange={(e) => updateFormData({ domain: e.target.value })}
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Examples: {DOMAIN_EXAMPLES.join(', ')}
                    </p>
                  </div>

                  <div>
                    <Label>Keywords</Label>
                    <KeywordInput
                      keywords={formData.keywords}
                      onChange={(keywords) => updateFormData({ keywords })}
                      placeholder="Add relevant keywords..."
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Language & Time */}
              <Card>
                <CardHeader>
                  <CardTitle>Language & Time Range</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Languages</Label>
                    <div className="flex flex-wrap gap-2">
                      {LANGUAGE_OPTIONS.map((lang) => (
                        <label key={lang} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.languages.includes(lang)}
                            onChange={(e) => {
                              const newLanguages = e.target.checked
                                ? [...formData.languages, lang]
                                : formData.languages.filter(l => l !== lang);
                              updateFormData({ languages: newLanguages });
                            }}
                            className="mr-2"
                          />
                          {lang}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="start-date">Start Date</Label>
                      <Input
                        id="start-date"
                        type="date"
                        value={formData.timeRange.start}
                        onChange={(e) => updateFormData({
                          timeRange: { ...formData.timeRange, start: e.target.value }
                        })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="end-date">End Date</Label>
                      <Input
                        id="end-date"
                        type="date"
                        value={formData.timeRange.end}
                        onChange={(e) => updateFormData({
                          timeRange: { ...formData.timeRange, end: e.target.value }
                        })}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quality & Scale */}
              <Card>
                <CardHeader>
                  <CardTitle>Quality & Scale</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Quality Tier</Label>
                    <div className="space-y-2">
                      {QUALITY_TIERS.map((tier) => (
                        <label key={tier.value} className="flex items-center">
                          <input
                            type="radio"
                            name="quality"
                            value={tier.value}
                            checked={formData.qualityTier === tier.value}
                            onChange={(e) => updateFormData({ qualityTier: e.target.value as any })}
                            className="mr-3"
                          />
                          <div>
                            <span className="font-medium">{tier.label}</span>
                            <span className="text-gray-500 ml-2">{tier.description}</span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="scale">Estimated Scale (optional)</Label>
                    <Input
                      id="scale"
                      placeholder="e.g., 10 million tokens, 100k documents"
                      value={formData.estimatedScale}
                      onChange={(e) => updateFormData({ estimatedScale: e.target.value })}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Contact */}
              <Card>
                <CardHeader>
                  <CardTitle>Contact Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div>
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@example.com"
                      value={formData.email}
                      onChange={(e) => updateFormData({ email: e.target.value })}
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      We'll send dataset delivery notifications to this address
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Submit */}
              <div className="flex gap-4">
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating Preview...
                    </>
                  ) : (
                    'Generate Preview (1M pages)'
                  )}
                </Button>
              </div>
            </form>
          </div>

          {/* Quote Card */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <QuoteCard quote={quote} loading={quoteLoading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
