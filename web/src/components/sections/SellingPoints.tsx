"use client";

import { motion } from "framer-motion";
import { Brain, Zap, Shield } from "lucide-react";
import { GradientCard } from "@/components/ui/gradient-card";

const points = [
  {
    icon: Brain,
    title: "AI-Powered",
    description: "Advanced machine learning algorithms ensure dataset quality and relevance for your specific domain.",
  },
  {
    icon: Zap,
    title: "Massive Scale",
    description: "Process billions of web pages with our distributed computing infrastructure for comprehensive coverage.",
  },
  {
    icon: Shield,
    title: "Privacy & Security",
    description: "Enterprise-grade data protection with PII removal, content sanitization, and secure delivery.",
  },
];

export function SellingPoints() {
  return (
    <section className="py-16 md:py-24" id="features">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Why Choose FineData?
          </h2>
          <p className="mt-4 text-lg text-foreground/70 max-w-2xl mx-auto">
            Built for researchers, ML engineers, and organizations that demand quality and scale.
          </p>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-3">
          {points.map((point, index) => (
            <motion.div
              key={point.title}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <GradientCard>
                <div className="text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                    <point.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{point.title}</h3>
                  <p className="text-foreground/70">{point.description}</p>
                </div>
              </GradientCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
