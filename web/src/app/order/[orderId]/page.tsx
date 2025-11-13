'use client';

import React, { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProgressBar } from '@/components/progress-bar';
import { MetricCard } from '@/components/metric-card';
import { ArrowLeft, ExternalLink, Download, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { orderApi, formatNumber } from '@/lib/api';
import { getStatusColor, getStatusLabel } from '@/lib/utils';
import { useProduction } from '@/hooks/use-api';
import type { Order } from '@/types';

interface OrderPageProps {
  params: Promise<{
    orderId: string;
  }>;
}

const STATUS_CONFIG = {
  draft: { icon: Clock, color: 'text-gray-500' },
  benchmarking: { icon: Loader2, color: 'text-blue-500' },
  preview_ready: { icon: CheckCircle, color: 'text-green-500' },
  awaiting_payment: { icon: Clock, color: 'text-yellow-500' },
  paid: { icon: CheckCircle, color: 'text-green-500' },
  cluster_queued: { icon: Clock, color: 'text-blue-500' },
  running: { icon: Loader2, color: 'text-blue-500' },
  finalizing: { icon: Loader2, color: 'text-blue-500' },
  delivered: { icon: CheckCircle, color: 'text-green-500' },
  failed: { icon: AlertCircle, color: 'text-red-500' },
};

export default function OrderPage({ params }: OrderPageProps) {
  const router = useRouter();
  const orderId = (params as any).orderId || '';

  console.log('Order page loaded with orderId:', orderId);

  // Poll order status
  const { data: order, isLoading, error, refetch } = useQuery({
    queryKey: ['order', orderId],
    queryFn: () => orderApi.getOrder(orderId),
    enabled: !!orderId, // Only run query when orderId is available
    refetchInterval: (query) => {
      // Stop polling when delivered or failed
      const data = query.state.data;
      if (data?.status === 'delivered' || data?.status === 'failed') {
        return false;
      }
      return 5000; // Poll every 5 seconds for active orders
    },
    refetchIntervalInBackground: false,
  });

  // Poll production status
  const { data: production } = useProduction(orderId);

  const getStatusIcon = (status: string) => {
    const config = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.draft;
    const Icon = config.icon;
    return <Icon className={`h-6 w-6 ${config.color}`} />;
  };

  const formatTimelineDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading order details...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Order Not Found</h2>
          <p className="text-gray-600 mb-4">The order you're looking for doesn't exist or has been deleted.</p>
          <Link href="/new">
            <Button>Create New Order</Button>
          </Link>
        </div>
      </div>
    );
  }

  const isRunning = ['running', 'cluster_queued', 'finalizing'].includes(order.status);
  const isDelivered = order.status === 'delivered';
  const hasError = order.status === 'failed';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">Order Status</h1>
                <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-sm font-medium rounded-full">
                  Slurm Production
                </span>
              </div>
              <p className="text-gray-600">Order #{orderId}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
              {getStatusIcon(order.status)}
              {getStatusLabel(order.status)}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Order Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {order.timeline.map((event, index) => (
                  <div key={index} className="flex items-start gap-4">
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(event.label.includes('Status changed') ?
                        event.label.split('to ')[1].toLowerCase().replace(/\s+/g, '_') :
                        'draft'
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{event.label}</p>
                      <p className="text-sm text-gray-500">
                        {formatTimelineDate(event.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Production Status */}
          {production && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span>Production Status</span>
                  <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-medium rounded">
                    Slurm Cluster
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Node Activity */}
                  <div>
                    <h3 className="font-semibold mb-3">Node Activity</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-foreground/70">Active Nodes</span>
                        <span className="font-medium">
                          {production.status === 'initializing' ? 4 :
                           production.status === 'running' ? 16 :
                           production.status === 'dedup' ? 8 :
                           production.status === 'publishing' ? 2 : 0}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-foreground/70">Throughput</span>
                        <span className="font-medium">
                          {production.status === 'running' ? '~2.5K docs/sec' : '0 docs/sec'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-foreground/70">Queue Depth</span>
                        <span className="font-medium">0</span>
                      </div>
                    </div>
                  </div>

                  {/* Status & ETA */}
                  <div>
                    <h3 className="font-semibold mb-3">Current Phase</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-foreground/70">Status</span>
                        <span className="font-medium capitalize">{production.status}</span>
                      </div>
                      {production.estCompleteAt && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-foreground/70">ETA</span>
                          <span className="font-medium">
                            {new Date(production.estCompleteAt).toLocaleString()}
                          </span>
                        </div>
                      )}
                      {production.logsUrl && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-foreground/70">Logs</span>
                          <a
                            href={production.logsUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline text-sm"
                          >
                            View Logs
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Live Progress (when running) */}
          {isRunning && order.live && (
            <Card>
              <CardHeader>
                <CardTitle>Production Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <MetricCard
                    title="Documents Fetched"
                    value={formatNumber(order.live.fetched)}
                    description="Total documents collected"
                  />
                  <MetricCard
                    title="Documents Filtered"
                    value={formatNumber(order.live.filtered)}
                    description="After quality filtering"
                  />
                  <MetricCard
                    title="Documents Deduped"
                    value={formatNumber(order.live.deduped)}
                    description="After deduplication"
                  />
                  <MetricCard
                    title="Final Tokens"
                    value={formatNumber(order.live.tokens)}
                    description="Estimated final size"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  <p>Estimated completion: 2-4 hours from start</p>
                  <p>Progress updates every 5 minutes</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Delivery Section (when delivered) */}
          {isDelivered && order.delivery && (
            <Card>
              <CardHeader>
                <CardTitle className="text-green-800">Dataset Delivered!</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {order.delivery.hf_url && (
                    <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                      <div>
                        <h3 className="font-semibold text-green-800">Hugging Face Dataset</h3>
                        <p className="text-sm text-green-700">
                          Your private dataset is ready for download
                        </p>
                      </div>
                      <a
                        href={order.delivery.hf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button className="bg-green-600 hover:bg-green-700">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          Open Dataset
                        </Button>
                      </a>
                    </div>
                  )}

                  {order.delivery.dataset_card && (
                    <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                      <div>
                        <h3 className="font-semibold text-blue-800">Dataset Card</h3>
                        <p className="text-sm text-blue-700">
                          Documentation and usage instructions
                        </p>
                      </div>
                      <a
                        href={order.delivery.dataset_card}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button variant="outline">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          View Card
                        </Button>
                      </a>
                    </div>
                  )}

                  {order.delivery.invoice_url && (
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h3 className="font-semibold text-gray-800">Invoice</h3>
                        <p className="text-sm text-gray-700">
                          Download your invoice and receipt
                        </p>
                      </div>
                      <a
                        href={order.delivery.invoice_url}
                        download={`invoice-${orderId}.pdf`}
                      >
                        <Button variant="outline">
                          <Download className="h-4 w-4 mr-2" />
                          Download Invoice
                        </Button>
                      </a>
                    </div>
                  )}
                </div>

                <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                  <h3 className="font-semibold text-yellow-800 mb-2">Important Notes</h3>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    <li>• Dataset is stored in a private Hugging Face repository</li>
                    <li>• Access is restricted to your account only</li>
                    <li>• Dataset may only be used for internal training purposes</li>
                    <li>• Contact support if you need to share access with team members</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Section */}
          {hasError && order.error && (
            <Card>
              <CardHeader>
                <CardTitle className="text-red-800">Order Failed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-red-800">{order.error}</p>
                </div>
                <div className="mt-4 flex gap-3">
                  <Button onClick={() => router.push('/new')}>
                    Create New Order
                  </Button>
                  <Button variant="outline">
                    Contact Support
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Support Section */}
          <Card>
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                If you have questions about your order or need assistance,
                our support team is here to help.
              </p>
              <Button variant="outline">
                Contact Support
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
