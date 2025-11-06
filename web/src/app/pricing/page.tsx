"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Check, ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GradientCard } from "@/components/ui/gradient-card";
import { useI18n } from "@/lib/i18n";

export default function PricingPage() {
  const { t } = useI18n();

  return (
    <div className="py-16 md:py-24">
      <div className="mb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            {t('pricing_title')}
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl mx-auto leading-relaxed">
            {t('pricing_subtitle')}
          </p>
        </motion.div>
      </div>

      {/* Pricing Cards */}
      <div className="grid gap-8 md:grid-cols-3 mb-16">
        {t('pricing_cards').map((plan, index) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className={index === 1 ? "md:scale-105" : ""}
          >
            <GradientCard className={`h-full ${index === 1 ? "ring-2 ring-primary/20" : ""}`}>
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-primary">{plan.price}</span>
                  {plan.unit && <span className="text-lg text-foreground/70 ml-1">{plan.unit}</span>}
                </div>
                <p className="text-foreground/70">{plan.desc}</p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-start gap-3">
                    <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-foreground/80">{item}</span>
                  </li>
                ))}
              </ul>

              <Button
                asChild
                className="w-full"
                variant={index === 1 ? "default" : "outline"}
                size="lg"
              >
                <Link href={plan.name === 'Preview Benchmark' ? "/new" : "/contact"}>
                  {plan.name === 'Preview Benchmark' ? 'Start Free' : 'Contact Sales'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
            </GradientCard>
          </motion.div>
        ))}
      </div>

      {/* Notes Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="max-w-4xl mx-auto"
      >
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-8">
          <h3 className="text-xl font-semibold mb-6 text-center">Important Notes</h3>
          <ul className="space-y-4">
            {t('pricing_notes').map((note, index) => (
              <li key={index} className="flex items-start gap-3">
                <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground/80">{note}</span>
              </li>
            ))}
          </ul>
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="text-center mt-16"
      >
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">
            Ready to build your dataset?
          </h2>
          <p className="text-lg text-foreground/70 mb-8">
            Start with a free benchmark to see exactly what quality data you can get.
          </p>
          <Button asChild size="lg">
            <Link href="/new">
              <Zap className="w-4 h-4 mr-2" />
              Start Free Benchmark
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
