"use client";

import { motion } from "framer-motion";
import { FileText, Search, CreditCard, Download } from "lucide-react";
import { GradientCard } from "@/components/ui/gradient-card";

const steps = [
  {
    icon: FileText,
    title: "Configure Dataset",
    description: "Specify your domain, keywords, languages, and quality requirements. Get instant pricing estimates.",
  },
  {
    icon: Search,
    title: "Preview & Validate",
    description: "Run a 1M-page benchmark to validate quality metrics and content relevance before full processing.",
  },
  {
    icon: CreditCard,
    title: "Secure Payment",
    description: "Pay only after preview approval. Full production processing begins immediately after payment.",
  },
  {
    icon: Download,
    title: "Download Dataset",
    description: "Receive your private HuggingFace repository with sanitized, production-ready dataset.",
  },
];

export function ProcessSteps() {
  return (
    <section className="py-16 md:py-24 bg-muted/30">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-foreground/70 max-w-2xl mx-auto">
            From concept to production dataset in four simple steps.
          </p>
        </motion.div>

        {/* Desktop: Horizontal timeline */}
        <div className="hidden md:block">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute top-8 left-0 right-0 h-0.5 bg-line" />

            <div className="grid grid-cols-4 gap-8">
              {steps.map((step, index) => (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 8 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="relative"
                >
                  <GradientCard className="text-center">
                    {/* Step number */}
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-semibold">
                        {index + 1}
                      </div>
                    </div>

                    <div className="pt-4">
                      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
                        <step.icon className="h-6 w-6 text-accent" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                      <p className="text-sm text-foreground/70">{step.description}</p>
                    </div>
                  </GradientCard>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile: Vertical timeline */}
        <div className="md:hidden space-y-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="flex items-start gap-4">
                {/* Timeline line and dot */}
                <div className="flex flex-col items-center">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-semibold">
                    {index + 1}
                  </div>
                  {index < steps.length - 1 && (
                    <div className="w-0.5 h-16 bg-line mt-4" />
                  )}
                </div>

                <GradientCard className="flex-1">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 flex-shrink-0">
                      <step.icon className="h-5 w-5 text-accent" />
                    </div>
                    <div>
                      <h3 className="font-semibold mb-1">{step.title}</h3>
                      <p className="text-sm text-foreground/70">{step.description}</p>
                    </div>
                  </div>
                </GradientCard>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
