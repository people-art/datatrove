'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { GradientCard } from '@/components/ui/gradient-card';
import { ProgressHeader } from '@/components/preview/ProgressHeader';
import { MetricsGrid } from '@/components/preview/MetricsGrid';
import { ArrowLeft, Download, Loader2, FileText } from 'lucide-react';
import { benchmarkApi, downloadFile } from '@/lib/api';
import type { BenchmarkJob } from '@/types';

interface PreviewPageProps {
  params: {
    jobId: string;
  };
}

export default function PreviewPage({ params }: PreviewPageProps) {
  const router = useRouter();

  // Poll benchmark job status
  const { data: job, isLoading, error } = useQuery({
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-lg text-foreground/70">Loading preview...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-danger">
            <FileText className="h-12 w-12 mx-auto mb-4" />
          </div>
          <h2 className="text-xl font-semibold">Failed to load preview</h2>
          <p className="text-foreground/60 mb-6">Unable to retrieve benchmark results</p>
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
    <div className="min-h-screen">
      <div className="container py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/new">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Form
                </Button>
              </Link>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-semibold tracking-tight">
                    Dataset Preview
                  </h1>
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-sm font-medium rounded-full">
                    Local Preview
                  </span>
                </div>
                <p className="text-lg text-foreground/70">
                  Review quality metrics and sample data before ordering
                </p>
              </div>
            </div>

            <div className="text-right text-sm text-foreground/50">
              <div>Job ID: {params.jobId.slice(0, 8)}...</div>
              <div className="text-xs">
                Created {new Date(job.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Progress Header */}
            <ProgressHeader
              status={job.status}
              progress={job.progress?.pct || 0}
              jobId={params.jobId}
            />

            {/* Metrics Grid */}
            {isReady && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.2 }}
              >
                <MetricsGrid
                  metrics={{
                    coverage: job.progress?.coverage || 0,
                    quality_pass_rate: job.progress?.quality_rate || 0,
                    docs_kept: job.progress?.docs_kept || 0,
                    docs_read: job.progress?.docs_read || 0,
                    tokens: job.progress?.tokens || 0,
                    pii_rate: job.progress?.pii_rate || 0,
                    domain_relevance_score: job.progress?.relevance_score || 0,
                  }}
                />
              </motion.div>
            )}

            {/* Sample Download */}
            {isReady && job.sample_url && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.4 }}
              >
                <GradientCard>
                  <div className="text-center space-y-4">
                    <div className="flex items-center justify-center gap-2">
                      <Download className="h-5 w-5 text-primary" />
                      <h3 className="text-lg font-semibold">Download Sample</h3>
                    </div>

                    <p className="text-foreground/70 max-w-md mx-auto">
                      Preview your dataset with a 1MB sample containing real filtered content.
                      This sample includes watermarks for verification purposes only.
                    </p>

                    <div className="flex items-center justify-center gap-4 text-sm text-foreground/60">
                      <span>• 100 sample documents</span>
                      <span>• JSONL format</span>
                      <span>• Gzipped for size</span>
                    </div>

                    <Button onClick={handleDownloadSample} size="lg">
                      <Download className="h-4 w-4 mr-2" />
                      Download Sample (1MB)
                    </Button>
                  </div>
                </GradientCard>
              </motion.div>
            )}

            {/* Error State */}
            {hasError && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <GradientCard>
                  <div className="text-center space-y-4">
                    <div className="text-danger">
                      <FileText className="h-12 w-12 mx-auto mb-4" />
                    </div>
                    <h3 className="text-lg font-semibold text-danger">Processing Failed</h3>
                    <p className="text-foreground/70">
                      {job.error_message || 'An error occurred during benchmark processing.'}
                    </p>
                    <div className="flex gap-3 justify-center">
                      <Button onClick={() => window.location.reload()}>
                        Retry
                      </Button>
                      <Button variant="outline" onClick={() => router.push('/new')}>
                        Start Over
                      </Button>
                    </div>
                  </div>
                </GradientCard>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Job Summary */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <GradientCard>
                <div className="space-y-4">
                  <h3 className="font-semibold">Job Summary</h3>

                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-foreground/70">Domain:</span>
                      <span className="font-medium">{job.domain}</span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-foreground/70">Keywords:</span>
                      <span className="font-medium">{job.keywords.length}</span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-foreground/70">Languages:</span>
                      <span className="font-medium">{job.languages.join(', ')}</span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-foreground/70">Quality:</span>
                      <span className="font-medium capitalize">{job.quality_tier}</span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-foreground/70">Time Range:</span>
                      <span className="font-medium text-xs">
                        {job.time_range_start} to {job.time_range_end}
                      </span>
                    </div>
                  </div>
                </div>
              </GradientCard>
            </motion.div>

            {/* CTA */}
            {isReady && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.6 }}
              >
                <GradientCard>
                  <div className="text-center space-y-4">
                    <h3 className="font-semibold">Ready to Proceed?</h3>
                    <p className="text-sm text-foreground/70">
                      Start full production processing and get your complete dataset delivered to HuggingFace.
                    </p>
                    <Button onClick={handleConfirmOrder} size="lg" className="w-full">
                      Confirm Order & Pay
                    </Button>
                    <p className="text-xs text-foreground/50">
                      You won't be charged until you confirm payment
                    </p>
                  </div>
                </GradientCard>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
