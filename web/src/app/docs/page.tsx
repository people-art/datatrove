"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Code, FileText, CheckCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GradientCard } from "@/components/ui/gradient-card";
import { useI18n } from "@/lib/i18n";

export default function DocsPage() {
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
            {t('docs_title')}
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl mx-auto leading-relaxed">
            {t('docs_subtitle')}
          </p>
        </motion.div>
      </div>

      {/* Process Flow */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4 mb-16">
        {t('docs_flow').map((step, index) => (
          <motion.div
            key={step.step}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <GradientCard className="h-full">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-xl font-bold text-primary">{step.step}</span>
                </div>
                <h3 className="text-lg font-semibold mb-3">{step.title}</h3>
                <p className="text-sm text-foreground/70 leading-relaxed">{step.body}</p>
              </div>

              {index < t('docs_flow').length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                  <ArrowRight className="w-8 h-8 text-primary/30" />
                </div>
              )}
            </GradientCard>
          </motion.div>
        ))}
      </div>

      {/* API Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="mb-16"
      >
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">{t('docs_api_title')}</h2>
          <p className="text-lg text-foreground/70">
            Complete API documentation for programmatic access
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <GradientCard>
            <div className="flex items-start gap-4">
              <Code className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-3">Core Endpoints</h3>
                <div className="space-y-2">
                  {t('docs_api_items').slice(0, 4).map((item, index) => (
                    <div key={index} className="text-sm text-foreground/80 font-mono bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </GradientCard>

          <GradientCard>
            <div className="flex items-start gap-4">
              <FileText className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-3">Additional APIs</h3>
                <div className="space-y-2">
                  {t('docs_api_items').slice(4).map((item, index) => (
                    <div key={index + 4} className="text-sm text-foreground/80 font-mono bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </GradientCard>
        </div>
      </motion.div>

      {/* Notes Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="mb-16"
      >
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-8">
          <h3 className="text-xl font-semibold mb-6 text-center">Key Technical Details</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {t('docs_notes').map((note, index) => (
              <div key={index} className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-foreground/80">{note}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.0 }}
        className="text-center"
      >
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">
            Ready to start building?
          </h2>
          <p className="text-lg text-foreground/70 mb-8">
            Create your first benchmark and see how FineData works in practice.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/new">
                <Clock className="w-4 h-4 mr-2" />
                Start Benchmark
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/features">
                Learn More
              </Link>
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
