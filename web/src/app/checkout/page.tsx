'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { QuoteCard } from '@/components/quote-card';
import { ArrowLeft, Shield, CreditCard, Loader2 } from 'lucide-react';
import { orderApi, benchmarkApi } from '@/lib/api';
import type { QuoteData } from '@/types';

function CheckoutPageContent() {
  const router = useSearchParams();
  const navigation = useRouter();
  const jobId = router.get('jobId');

  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [clientSecret, setClientSecret] = useState<string>('');
  const [orderId, setOrderId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  useEffect(() => {
    if (!jobId) {
      navigation.push('/new');
      return;
    }

    initializeCheckout();
  }, [jobId]);

  const initializeCheckout = async () => {
    try {
      setLoading(true);

      // Get job data to extract required information
      const jobData = await benchmarkApi.getJob(jobId!);

      // Create quote first
      const quoteRequest = {
        domain: jobData.domain,
        keywords: jobData.keywords,
        languages: jobData.languages,
        startDate: jobData.time_range_start,
        endDate: jobData.time_range_end,
        qualityTier: jobData.quality_tier,
        estimatedScale: jobData.estimated_scale ? { docs: jobData.estimated_scale.docs } : undefined
      };

      const quoteData = await benchmarkApi.createQuote(quoteRequest);
      setQuote({
        currency: quoteData.currency,
        subtotal: (quoteData.estimate.low + quoteData.estimate.high) / 2,
        tax: ((quoteData.estimate.low + quoteData.estimate.high) / 2) * 0.08,
        total: ((quoteData.estimate.low + quoteData.estimate.high) / 2) * 1.08,
        pricing_notes: `Quote expires: ${new Date(quoteData.expiresAt).toLocaleDateString()}`,
        breakdown: {
          adjusted_price_per_million: quoteData.unit.amount
        }
      });

      // Create order with idempotency key
      const idempotencyKey = `order_${jobId}_${Date.now()}`;
      const orderData = await orderApi.createOrder({
        quoteId: quoteData.quoteId,
        jobId: jobId,
        email: jobData.email
      }, idempotencyKey);

      setClientSecret(orderData.clientSecret);
      setOrderId(orderData.orderId);

    } catch (error) {
      console.error('Failed to initialize checkout:', error);
      alert('Failed to initialize checkout. Please try again.');
      navigation.push('/new');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!agreedToTerms) {
      alert('Please agree to the terms and conditions');
      return;
    }

    setProcessing(true);

    try {
      // In a real implementation, this would use Stripe Elements
      // For development, we'll simulate the payment process

      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Redirect to order page
      navigation.push(`/order/${orderId}`);

    } catch (error) {
      console.error('Payment failed:', error);
      alert('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
