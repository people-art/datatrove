import { Metadata } from 'next';
import { useI18n } from '@/lib/i18n';
import { GradientCard } from '@/components/ui/gradient-card';
import { Badge } from '@/components/ui/badge';

export const metadata: Metadata = {
  title: 'Features - FineData',
  description: 'Learn about FineData\'s AI-powered data processing, enterprise-grade privacy, and massive web-scale coverage.',
};

export default function FeaturesPage() {
  // Note: Since this is a server component, we can't use useI18n hook directly
  // We'll use static content for now, but in a real app you'd pass translations as props
  const features = {
    title: "Why FineData",
    subtitle: "Purpose-built for AI teams, researchers, and enterprises that demand clean, controllable, and scalable training data.",
    blocks: [
      {
        title: "AI-Powered Filtering",
        body: "Ontology-driven keyword expansion, LLM-assisted scoring, and multi-stage quality filters ensure your dataset matches your exact domain and intent."
      },
      {
        title: "Massive Web-Scale Coverage",
        body: "Leverage Common Crawl and battle-tested pipelines to process billions of pages with deterministic, reproducible configurations."
      },
      {
        title: "Enterprise-Grade Privacy",
        body: "PII detection, HIPAA-ready patterns for medical content, and strict sanitization keep your datasets safe and compliant."
      },
      {
        title: "Custom Domains in Days",
        body: "Support any niche domain: finance, medical, robotics, law, education, energy, security, and internal ontologies."
      },
      {
        title: "Transparent Metrics",
        body: "Every run ships with coverage, dedup ratio, language mix, toxicity and PII rates, plus domain relevance reports."
      },
      {
        title: "Private Delivery on Hugging Face",
        body: "Datasets are delivered as private Hugging Face repositories or S3 buckets with fine-grained access control."
      }
    ]
  };

  return (
    <div className="min-h-screen py-16">
      <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            {features.title}
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl mx-auto">
            {features.subtitle}
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-16">
          {features.blocks.slice(0, 3).map((feature, index) => (
            <GradientCard key={index} className="h-full">
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4 text-primary">
                  {feature.title}
                </h3>
                <p className="text-foreground/70 leading-relaxed">
                  {feature.body}
                </p>
              </div>
            </GradientCard>
          ))}
        </div>

        {/* Secondary Features Grid */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.blocks.slice(3).map((feature, index) => (
            <GradientCard key={index + 3} className="h-full">
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4 text-primary">
                  {feature.title}
                </h3>
                <p className="text-foreground/70 leading-relaxed">
                  {feature.body}
                </p>
              </div>
            </GradientCard>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center mt-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/10 rounded-full text-accent text-sm font-medium mb-6">
            <Badge variant="secondary">Ready to get started?</Badge>
          </div>
          <h2 className="text-2xl font-bold mb-4">
            Transform your AI training data today
          </h2>
          <p className="text-foreground/70 mb-8 max-w-2xl mx-auto">
            Join leading AI teams who trust FineData for their critical data processing needs.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/new"
              className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
            >
              Create Dataset
            </a>
            <a
              href="/docs"
              className="inline-flex items-center px-6 py-3 border border-border rounded-lg font-medium hover:bg-accent transition-colors"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}