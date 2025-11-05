'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProgressBar } from '@/components/progress-bar';
import { MetricCard } from '@/components/metric-card';
import { SampleTable } from '@/components/sample-table';
import { QuoteCard } from '@/components/quote-card';
import { ArrowLeft, Download, Loader2, TrendingUp, TrendingDown } from 'lucide-react';
import { benchmarkApi, downloadFile, formatNumber, formatFileSize } from '@/lib/api';
import type { BenchmarkJob, QuoteData } from '@/types';

interface PreviewPageProps {
  params: {
    jobId: string;
  };
}

export default function PreviewPage({ params }: PreviewPageProps) {
  const router = useRouter();
  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);

  // Poll benchmark job status
  const { data: job, isLoading, error, refetch } = useQuery({
    queryKey: ['benchmark-job', params.jobId],
    queryFn: () => benchmarkApi.getJob(params.jobId),
    refetchInterval: (query) => {
      // Stop polling when job is ready or failed
      const data = query.state.data;
      if (data?.status === 'ready' || data?.status === 'failed') {
        return false;
      }
      return 3000; // Poll every 3 seconds
    },
    refetchIntervalInBackground: false,
  });

  // Fetch quote when job becomes ready
  useEffect(() => {
    if (job?.status === 'ready' && !quote) {
      fetchQuote();
    }
  }, [job?.status]);

  const fetchQuote = async () => {
    try {
      setQuoteLoading(true);
      const quoteData = await benchmarkApi.getQuote(params.jobId);
      setQuote(quoteData);
    } catch (error) {
      console.error('Failed to fetch quote:', error);
    } finally {
      setQuoteLoading(false);
    }
  };

  const handleDownloadSample = async () => {
    if (!job?.sample_url) return;

    try {
      await downloadFile(job.sample_url, `benchmark-sample-${params.jobId}.jsonl.gz`);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download sample. Please try again.');
    }
  };

  const handleConfirmOrder = () => {
    router.push(`/checkout?jobId=${params.jobId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading preview...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load preview</p>
          <Button onClick={() => router.push('/new')}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  const isReady = job.status === 'ready';
  const hasError = job.status === 'failed';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link href="/new">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Form
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dataset Preview</h1>
              <p className="text-gray-600">Review quality metrics and sample data</p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Job ID: {params.jobId}
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Progress */}
            <Card>
              <CardHeader>
                <CardTitle>Benchmark Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <ProgressBar
                  status={job.status}
                  progress={job.progress?.pct || 0}
                />
                {job.progress && (
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Documents Read</span>
                      <div className="font-semibold">{formatNumber(job.progress.docs_read)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Documents Kept</span>
                      <div className="font-semibold">{formatNumber(job.progress.docs_kept)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Tokens</span>
                      <div className="font-semibold">{formatNumber(job.progress.tokens)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Deduplication Rate</span>
                      <div className="font-semibold">{(job.progress.dedup_rate * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                )}
                {hasError && job.error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-800 text-sm">{job.error}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Metrics - Only show when ready */}
            {isReady && job.metrics && (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <MetricCard
                    title="Coverage"
                    value={`${(job.metrics.coverage * 100).toFixed(1)}%`}
                    description="Domain relevance score"
                    trend="up"
                  />
                  <MetricCard
                    title="Quality Pass Rate"
                    value={`${(job.metrics.quality_pass_rate * 100).toFixed(1)}%`}
                    description="Content quality filters"
                    trend="up"
                  />
                  <MetricCard
                    title="PII Risk"
                    value={`${(job.metrics.pii_rate * 100).toFixed(2)}%`}
                    description="Personal info detected"
                    trend="down"
                  />
                  <MetricCard
                    title="Toxicity Risk"
                    value={`${(job.metrics.toxicity_rate * 100).toFixed(2)}%`}
                    description="Harmful content detected"
                    trend="down"
                  />
                </div>

                {/* Language & Domain Distribution */}
                <div className="grid md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Language Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(job.metrics.lang_dist)
                          .sort(([,a], [,b]) => b - a)
                          .slice(0, 5)
                          .map(([lang, count]) => (
                            <div key={lang} className="flex justify-between">
                              <span>{lang}</span>
                              <span className="font-semibold">{count.toLocaleString()}</span>
                            </div>
                          ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Domain Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(job.metrics.domain_dist)
                          .sort(([,a], [,b]) => b - a)
                          .slice(0, 5)
                          .map(([domain, count]) => (
                            <div key={domain} className="flex justify-between">
                              <span className="truncate">{domain}</span>
                              <span className="font-semibold">{count.toLocaleString()}</span>
                            </div>
                          ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Sample Data */}
                <SampleTable samples={[]} />

                {/* Download Sample */}
                {job.sample_url && (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">Sample Dataset</h3>
                          <p className="text-sm text-gray-600">
                            Download a 1M page sample for evaluation (~{formatFileSize(100 * 1024 * 1024)})
                          </p>
                        </div>
                        <Button onClick={handleDownloadSample}>
                          <Download className="h-4 w-4 mr-2" />
                          Download Sample
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Quote */}
              <QuoteCard quote={quote} loading={quoteLoading} />

              {/* Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Next Steps</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button
                    onClick={() => router.push('/new')}
                    variant="outline"
                    className="w-full"
                    disabled={!isReady && !hasError}
                  >
                    Modify Requirements
                  </Button>
                  <Button
                    onClick={handleConfirmOrder}
                    className="w-full"
                    disabled={!isReady || !quote}
                  >
                    {isReady ? 'Confirm & Pay' : 'Waiting for Preview...'}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
