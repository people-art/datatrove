import { Metadata } from 'next';
import { GradientCard } from '@/components/ui/gradient-card';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Pricing - FineData',
  description: 'Simple, transparent pricing for high-quality, domain-specific training data.',
};

export default function PricingPage() {
  const pricing = {
    title: "Simple, Transparent Pricing",
    subtitle: "Pay for high-quality, domain-specific data — no lock-in, no hidden fees.",
    cards: [
      {
        name: "Preview Benchmark",
        price: "Free",
        unit: "",
        desc: "1M-page local benchmark to validate quality before you commit.",
        items: [
          "Custom domain & keywords",
          "End-to-end pipeline simulation",
          "Quality and coverage report",
          "Sample dataset download"
        ],
        popular: false
      },
      {
        name: "Standard Production",
        price: "From $50",
        unit: "per million tokens",
        desc: "Balanced quality for most fine-tuning and RAG workloads.",
        items: [
          "Common Crawl based sourcing",
          "Multi-stage quality & PII filters",
          "Minhash deduplication",
          "Private Hugging Face delivery"
        ],
        popular: true
      },
      {
        name: "Premium Curated",
        price: "Custom",
        unit: "",
        desc: "For regulated industries and mission-critical models.",
        items: [
          "Stricter filters and LLM scoring",
          "Domain expert review options",
          "Custom ontologies & constraints",
          "SLA, support, and governance"
        ],
        popular: false
      }
    ],
    notes: [
      "Final pricing is computed from your quote: domain complexity, time range, target size, and quality tier.",
      "You always see an estimated range before payment, based on the benchmark run.",
      "Enterprise and multi-run commitments can be discounted."
    ]
  };

  return (
    <div className="min-h-screen py-16">
      <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            {pricing.title}
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl mx-auto">
            {pricing.subtitle}
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-8 md:grid-cols-3 mb-16">
          {pricing.cards.map((card, index) => (
            <GradientCard key={index} className={`relative ${card.popular ? 'ring-2 ring-primary' : ''}`}>
              {card.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground">Most Popular</Badge>
                </div>
              )}

              <div className="p-8">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2">{card.name}</h3>
                  <div className="text-4xl font-bold text-primary mb-1">
                    {card.price}
                    {card.unit && <span className="text-lg font-normal text-foreground/70"> {card.unit}</span>}
                  </div>
                  <p className="text-foreground/60">{card.desc}</p>
                </div>

                <ul className="space-y-3 mb-8">
                  {card.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-accent mt-0.5 flex-shrink-0" />
                      <span className="text-foreground/80">{item}</span>
                    </li>
                  ))}
                </ul>

                <a
                  href={card.name === "Preview Benchmark" ? "/new" : "/new"}
                  className={`block w-full text-center px-6 py-3 rounded-lg font-medium transition-colors ${
                    card.popular
                      ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  {card.name === "Preview Benchmark" ? "Start Free Benchmark" :
                   card.name === "Standard Production" ? "Get Started" : "Contact Sales"}
                </a>
              </div>
            </GradientCard>
          ))}
        </div>

        {/* Notes Section */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-2xl p-8 mb-16">
          <h2 className="text-2xl font-bold mb-6 text-center">Important Notes</h2>
          <div className="grid gap-4 md:grid-cols-1 max-w-4xl mx-auto">
            {pricing.notes.map((note, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-foreground/80">{note}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Questions?</h2>
          <p className="text-foreground/70 mb-8 max-w-2xl mx-auto">
            Have questions about pricing or need a custom solution?
            We're here to help you find the perfect data solution.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/docs"
              className="inline-flex items-center px-6 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-secondary/80 transition-colors"
            >
              View Documentation
            </a>
            <a
              href="/contact"
              className="inline-flex items-center px-6 py-3 border border-border rounded-lg font-medium hover:bg-accent transition-colors"
            >
              Contact Us
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}