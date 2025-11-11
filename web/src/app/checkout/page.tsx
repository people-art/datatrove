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

      // Ensure we have at least 2 keywords (API requirement)
      let keywords = jobData.keywords || [];
      if (keywords.length < 2) {
        // Add default keywords based on domain
        const defaultKeywords = [`${jobData.domain}`, `${jobData.domain} technology`];
        keywords = [...keywords, ...defaultKeywords.slice(0, 2 - keywords.length)];
      }

      // Create quote first
      const quoteRequest = {
        domain: jobData.domain,
        keywords: keywords,
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
          base_price_per_million: quoteData.unit.amount,
          language_factor: 1.0,
          domain_factor: 1.0,
          time_factor: 1.0,
          adjusted_price_per_million: quoteData.unit.amount
        }
      });

      // Create order with idempotency key
      const idempotencyKey = `order_${jobId}_${Date.now()}`;
      const orderData = await orderApi.createOrder({
        quoteId: quoteData.quoteId,
        jobId: jobId!,
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
      // For development, call mock payment API to trigger production
      await orderApi.mockPaymentAndStartProduction(orderId);

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
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing checkout...</p>
        </div>
      </div>
    );
  }

  if (!quote) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-muted-foreground">No quote available</p>
          <Link href="/new">
            <Button className="mt-4">Create New Dataset</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href={`/preview/${jobId}`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Preview
          </Button>
        </Link>
        <h1 className="text-2xl font-semibold">Checkout</h1>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Order Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Order Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span>Dataset Processing</span>
                <span>${quote.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Tax</span>
                <span>${quote.tax.toFixed(2)}</span>
              </div>
              <div className="border-t pt-4 flex justify-between font-semibold">
                <span>Total</span>
                <span>${quote.total.toFixed(2)}</span>
              </div>
            </CardContent>
          </Card>

          {/* Terms Agreement */}
          <div className="flex items-start gap-3 p-4 border rounded-lg">
            <input
              type="checkbox"
              id="terms"
              checked={agreedToTerms}
              onChange={(e) => setAgreedToTerms(e.target.checked)}
              className="mt-1"
            />
            <label htmlFor="terms" className="text-sm">
              I agree to the{' '}
              <Link href="/terms" className="text-primary hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-primary hover:underline">
                Privacy Policy
              </Link>
            </label>
          </div>
        </div>

        {/* Payment Form */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Payment Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-8 border-2 border-dashed border-muted-foreground/25 rounded-lg text-center text-muted-foreground">
                  <CreditCard className="h-12 w-12 mx-auto mb-4" />
                  <p>Stripe payment integration</p>
                  <p className="text-sm">Coming soon in production</p>
                </div>

                <Button
                  onClick={handlePayment}
                  disabled={!agreedToTerms || processing}
                  className="w-full"
                  size="lg"
                >
                  {processing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Complete Payment - ${quote.total.toFixed(2)}
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    }>
      <CheckoutPageContent />
    </Suspense>
  );
}
