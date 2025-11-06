import { Metadata } from 'next';
import { GradientCard } from '@/components/ui/gradient-card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Code, Zap, Shield, Database } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Documentation - FineData',
  description: 'Learn how FineData works, from request to private dataset delivery in four predictable steps.',
};

export default function DocsPage() {
  const docs = {
    title: "How FineData Works",
    subtitle: "From request to private dataset in four predictable steps.",
    flow: [
      {
        step: 1,
        title: "Submit Requirements",
        body: "Define your domain, keywords, languages, time range, and quality tier via the web console or API.",
        icon: Database
      },
      {
        step: 2,
        title: "Run Benchmark (1M pages)",
        body: "We execute a local preview run using the exact same pipeline configuration and return metrics plus a sample dataset.",
        icon: Zap
      },
      {
        step: 3,
        title: "Approve & Pay",
        body: "Once you're satisfied with the preview, confirm the quote and complete payment via secure card checkout.",
        icon: Shield
      },
      {
        step: 4,
        title: "Cluster Production & Delivery",
        body: "A Slurm-based cluster run processes full Common Crawl segments. When finished, you receive a private Hugging Face URL via email.",
        icon: Code
      }
    ],
    apiTitle: "API Overview",
    apiItems: [
      "POST /benchmark/quote – Get an estimated price for your config.",
      "POST /benchmark/jobs – Start a 1M-page benchmark job.",
      "GET /benchmark/jobs/{id} – Poll benchmark status and metrics.",
      "POST /orders – Create an order from a quote and job.",
      "GET /orders/{id} – Track order and payment status.",
      "GET /orders/{id}/production – View production pipeline progress.",
      "POST /email/validate – Validate email format/MX/SMTP/disposable.",
      "POST /checkout/session – Create payment session (Stripe compatible)."
    ],
    notes: [
      "All responses follow a unified error schema with code, message, suggestion, and timestamp.",
      "Idempotency keys are supported on all create operations to keep retries safe.",
      "Production runs are isolated per customer and delivered via private repositories."
    ]
  };

  return (
    <div className="min-h-screen py-16">
      <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            {docs.title}
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl mx-auto">
            {docs.subtitle}
          </p>
        </div>

        {/* Flow Steps */}
        <div className="mb-20">
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {docs.flow.map((step, index) => (
              <div key={index} className="relative">
                {/* Connector Line */}
                {index < docs.flow.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-primary to-primary/50 z-0"></div>
                )}

                <GradientCard className="relative z-10 h-full">
                  <div className="p-6 text-center">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-primary text-primary-foreground rounded-full mb-4">
                      <step.icon className="h-6 w-6" />
                    </div>

                    <div className="inline-flex items-center gap-2 mb-4">
                      <Badge variant="outline">Step {step.step}</Badge>
                    </div>

                    <h3 className="text-lg font-semibold mb-3">{step.title}</h3>
                    <p className="text-foreground/70 text-sm leading-relaxed">{step.body}</p>
                  </div>
                </GradientCard>
              </div>
            ))}
          </div>
        </div>

        {/* API Overview */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">{docs.apiTitle}</h2>

          <GradientCard>
            <div className="p-8">
              <div className="grid gap-4 md:grid-cols-2">
                {docs.apiItems.map((item, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-900">
                    <ArrowRight className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <code className="text-sm font-mono text-foreground/90">{item}</code>
                  </div>
                ))}
              </div>
            </div>
          </GradientCard>
        </div>

        {/* Technical Notes */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center mb-8">Technical Details</h2>

          <div className="grid gap-6 md:grid-cols-3">
            {docs.notes.map((note, index) => (
              <GradientCard key={index}>
                <div className="p-6">
                  <div className="flex items-start gap-3">
                    <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-sm text-foreground/80 leading-relaxed">{note}</p>
                  </div>
                </div>
              </GradientCard>
            ))}
          </div>
        </div>

        {/* Quick Start */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/10 rounded-full text-accent text-sm font-medium mb-6">
            <Badge variant="secondary">Ready to start?</Badge>
          </div>
          <h2 className="text-2xl font-bold mb-4">
            Get your first dataset in minutes
          </h2>
          <p className="text-foreground/70 mb-8 max-w-2xl mx-auto">
            Start with a free benchmark to see how FineData can transform your training data quality.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/new"
              className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
            >
              Start Benchmark
              <ArrowRight className="ml-2 h-4 w-4" />
            </a>
            <a
              href="/features"
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