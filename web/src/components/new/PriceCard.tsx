"use client";

import { motion, AnimatePresence } from "framer-motion";
import { DollarSign, TrendingUp } from "lucide-react";
import { GradientCard } from "@/components/ui/gradient-card";

interface PriceCardProps {
  quote?: {
    currency: string;
    estimated_tokens: number;
    subtotal: number;
    tax: number;
    total: number;
    pricing_notes: string;
    breakdown?: {
      base_price_per_million: number;
      language_factor: number;
      domain_factor: number;
      time_factor: number;
      adjusted_price_per_million: number;
    };
  };
  isLoading?: boolean;
  className?: string;
}

export function PriceCard({ quote, isLoading, className }: PriceCardProps) {
  return (
    <div className={`sticky top-24 ${className}`}>
      <GradientCard>
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Estimated Price</h3>
          </div>

          {isLoading ? (
            <div className="space-y-4">
              <div className="h-8 bg-muted/50 rounded animate-pulse" />
              <div className="h-4 bg-muted/50 rounded animate-pulse w-3/4" />
              <div className="h-4 bg-muted/50 rounded animate-pulse w-1/2" />
            </div>
          ) : quote ? (
            <AnimatePresence mode="wait">
              <motion.div
                key={quote.total}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="space-y-4"
              >
                {/* Main Price */}
                <div className="text-center p-4 rounded-xl bg-primary/5 border border-primary/10">
                  <div className="text-3xl font-bold text-primary">
                    ${quote.total.toFixed(2)}
                  </div>
                  <div className="text-sm text-foreground/60 mt-1">
                    {quote.currency}
                  </div>
                </div>

                {/* Breakdown */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-foreground/70">Subtotal</span>
                    <span>${quote.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-foreground/70">Tax (8%)</span>
                    <span>${quote.tax.toFixed(2)}</span>
                  </div>
                  <hr className="border-line" />
                  <div className="flex justify-between font-medium">
                    <span>Total</span>
                    <span>${quote.total.toFixed(2)}</span>
                  </div>
                </div>

                {/* Token Estimate */}
                <div className="flex items-center gap-2 p-3 rounded-lg bg-accent/5 border border-accent/10">
                  <TrendingUp className="h-4 w-4 text-accent" />
                  <div className="text-sm">
                    <div className="font-medium">
                      ~{quote.estimated_tokens.toLocaleString()} tokens
                    </div>
                    <div className="text-foreground/60">
                      Estimated size
                    </div>
                  </div>
                </div>

                {/* Pricing Notes */}
                <div className="text-xs text-foreground/60 leading-relaxed">
                  {quote.pricing_notes}
                </div>
              </motion.div>
            </AnimatePresence>
          ) : (
            <div className="text-center py-8 text-foreground/50">
              <DollarSign className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Fill out the form to see pricing</p>
            </div>
          )}
        </div>
      </GradientCard>
    </div>
  );
}
