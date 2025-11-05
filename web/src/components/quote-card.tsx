import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency } from '@/lib/api';
import type { QuoteData } from '@/types';

interface QuoteCardProps {
  quote: QuoteData | null;
  loading?: boolean;
}

export function QuoteCard({ quote, loading }: QuoteCardProps) {
  if (loading) {
    return (
      <Card className="w-80">
        <CardHeader>
          <CardTitle className="text-lg">Estimated Price</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-6 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!quote) {
    return (
      <Card className="w-80">
        <CardHeader>
          <CardTitle className="text-lg">Estimated Price</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">Complete the form to see pricing</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-80">
      <CardHeader>
        <CardTitle className="text-lg">Estimated Price</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between">
          <span>Subtotal</span>
          <span>{formatCurrency(quote.subtotal, quote.currency)}</span>
        </div>
        <div className="flex justify-between">
          <span>Tax</span>
          <span>{formatCurrency(quote.tax, quote.currency)}</span>
        </div>
        <div className="border-t pt-2">
          <div className="flex justify-between font-semibold text-lg">
            <span>Total</span>
            <span>{formatCurrency(quote.total, quote.currency)}</span>
          </div>
        </div>
        {quote.pricing_notes && (
          <p className="text-xs text-gray-500 mt-2">{quote.pricing_notes}</p>
        )}
      </CardContent>
    </Card>
  );
}
