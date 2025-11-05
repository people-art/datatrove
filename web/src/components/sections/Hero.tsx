"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden py-20 md:py-28">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(45,91,255,0.18),transparent_60%)]" />

      <div className="container relative">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="mx-auto max-w-4xl text-center"
        >
          <h1 className="text-4xl font-semibold tracking-tight text-foreground md:text-6xl">
            Custom Domain Datasets{" "}
            <span className="text-primary">Powered by AI</span>
          </h1>

          <p className="mt-6 text-lg text-foreground/70 max-w-2xl mx-auto">
            Generate high-quality, domain-specific datasets from billions of web pages—ready for training specialized AI models, research, and analytics.
          </p>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
            className="mt-8 flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button size="lg" asChild>
              <Link href="/new">Start Your Dataset</Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link href="#features">Learn More</Link>
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
