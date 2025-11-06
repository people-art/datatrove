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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading checkout...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href={`/preview/${jobId}`}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Preview
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
            <p className="text-gray-600">Complete your dataset order</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Order Summary */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Dataset Generation</span>
                    <span>Based on benchmark results</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Quality Tier</span>
                    <span>Premium</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Estimated Size</span>
                    <span>~100M tokens</span>
                  </div>
                  <div className="border-t pt-4">
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Processing Time</span>
                      <span>2-4 hours</span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Delivery</span>
                      <span>Hugging Face private repo</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Payment Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Payment Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Stripe Elements would go here in production */}
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <CreditCard className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">
                      Stripe Elements integration would be implemented here
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      For development, payment is simulated
                    </p>
                  </div>

                  {/* Terms Agreement */}
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id="terms"
                      checked={agreedToTerms}
                      onChange={(e) => setAgreedToTerms(e.target.checked)}
                      className="mt-1"
                    />
                    <label htmlFor="terms" className="text-sm text-gray-700">
                      I agree to the{' '}
                      <a href="#" className="text-blue-600 hover:underline">
                        Terms of Service
                      </a>{' '}
                      and{' '}
                      <a href="#" className="text-blue-600 hover:underline">
                        Privacy Policy
                      </a>
                      . I understand that this service is for internal training use only and
                      datasets cannot be redistributed.
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quote & Payment */}
          <div className="space-y-6">
            <QuoteCard quote={quote} />

            {/* Security Notice */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-green-800">Secure Payment</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Your payment information is processed securely by Stripe.
                      We never store your card details on our servers.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Pay Button */}
            <Button
              onClick={handlePayment}
              disabled={processing || !agreedToTerms}
              className="w-full text-lg py-6"
            >
              {processing ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Processing Payment...
                </>
              ) : (
                `Pay $${quote?.total?.toFixed(2)} and Start Production`
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>}>
      <CheckoutPageContent />
    </Suspense>
  );
}
