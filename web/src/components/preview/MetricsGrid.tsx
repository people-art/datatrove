"use client";

import { motion } from "framer-motion";
import {
  Target,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  FileText,
  Shield,
  TrendingUp,
  TrendingDown
} from "lucide-react";
import { GradientCard } from "@/components/ui/gradient-card";

interface MetricsGridProps {
  metrics: {
    coverage?: number;
    quality_pass_rate?: number;
    docs_kept?: number;
    docs_read?: number;
    tokens?: number;
    pii_rate?: number;
    avg_doc_length?: number;
    domain_relevance_score?: number;
  };
  isLoading?: boolean;
}

const metricConfigs = [
  {
    key: 'coverage',
    label: 'Coverage',
    icon: Target,
    description: 'Percentage of relevant content found',
    format: (value: number) => `${(value * 100).toFixed(1)}%`,
    getColor: (value: number) => value > 0.8 ? 'text-accent' : value > 0.5 ? 'text-warning' : 'text-danger',
    getBgColor: (value: number) => value > 0.8 ? 'bg-accent/10' : value > 0.5 ? 'bg-warning/10' : 'bg-danger/10',
  },
  {
    key: 'quality_pass_rate',
    label: 'Quality Rate',
    icon: CheckCircle,
    description: 'Content passing quality filters',
    format: (value: number) => `${(value * 100).toFixed(1)}%`,
    getColor: (value: number) => value > 0.8 ? 'text-accent' : value > 0.6 ? 'text-warning' : 'text-danger',
    getBgColor: (value: number) => value > 0.8 ? 'bg-accent/10' : value > 0.6 ? 'bg-warning/10' : 'bg-danger/10',
  },
  {
    key: 'docs_kept',
    label: 'Documents',
    icon: FileText,
    description: 'High-quality documents retained',
    format: (value: number) => value.toLocaleString(),
    getColor: () => 'text-primary',
    getBgColor: () => 'bg-primary/10',
  },
  {
    key: 'tokens',
    label: 'Tokens',
    icon: BarChart3,
    description: 'Estimated token count',
    format: (value: number) => value.toLocaleString(),
    getColor: () => 'text-primary',
    getBgColor: () => 'bg-primary/10',
  },
];

const riskMetrics = [
  {
    key: 'pii_rate',
    label: 'PII Risk',
    icon: Shield,
    description: 'Potential personally identifiable information',
    format: (value: number) => `${(value * 100).toFixed(2)}%`,
    getColor: (value: number) => value < 0.01 ? 'text-accent' : value < 0.05 ? 'text-warning' : 'text-danger',
    getBgColor: (value: number) => value < 0.01 ? 'bg-accent/10' : value < 0.05 ? 'bg-warning/10' : 'bg-danger/10',
    getIcon: (value: number) => value < 0.01 ? CheckCircle : value < 0.05 ? AlertTriangle : AlertTriangle,
  },
  {
    key: 'domain_relevance_score',
    label: 'Relevance',
    icon: Target,
    description: 'How well content matches your domain',
    format: (value: number) => `${(value * 100).toFixed(1)}%`,
    getColor: (value: number) => value > 0.8 ? 'text-accent' : value > 0.6 ? 'text-warning' : 'text-danger',
    getBgColor: (value: number) => value > 0.8 ? 'bg-accent/10' : value > 0.6 ? 'bg-warning/10' : 'bg-danger/10',
  },
];

export function MetricsGrid({ metrics, isLoading }: MetricsGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-32 bg-muted/50 rounded-2xl" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Main Metrics */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Quality Metrics</h3>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {metricConfigs.map((config, index) => {
            const value = metrics[config.key as keyof typeof metrics];
            const Icon = config.icon;
            const color = config.getColor(value as number);
            const bgColor = config.getBgColor(value as number);

            return (
              <motion.div
                key={config.key}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
              >
                <GradientCard>
                  <div className="text-center space-y-3">
                    <div className={`mx-auto w-12 h-12 rounded-xl ${bgColor} flex items-center justify-center`}>
                      <Icon className={`h-6 w-6 ${color}`} />
                    </div>

                    <div>
                      <div className={`text-2xl font-bold ${color}`}>
                        {value !== undefined ? config.format(value as number) : '--'}
                      </div>
                      <div className="text-sm font-medium text-foreground/80">
                        {config.label}
                      </div>
                    </div>

                    <p className="text-xs text-foreground/60 leading-tight">
                      {config.description}
                    </p>
                  </div>
                </GradientCard>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Risk & Compliance */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
        <div className="grid gap-6 md:grid-cols-2">
          {riskMetrics.map((config, index) => {
            const value = metrics[config.key as keyof typeof metrics];
            const Icon = config.getIcon ? config.getIcon(value as number) : config.icon;
            const color = config.getColor(value as number);
            const bgColor = config.getBgColor(value as number);

            return (
              <motion.div
                key={config.key}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: (index + 4) * 0.05 }}
              >
                <GradientCard>
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${bgColor} flex-shrink-0`}>
                      <Icon className={`h-6 w-6 ${color}`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-foreground/80">
                          {config.label}
                        </span>
                        {value !== undefined && (
                          <span className={`text-lg font-bold ${color}`}>
                            {config.format(value as number)}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-foreground/60 leading-tight">
                        {config.description}
                      </p>
                    </div>

                    <div className="flex-shrink-0">
                      {value !== undefined && value < 0.01 && (
                        <div className="text-accent">
                          <TrendingDown className="h-4 w-4" />
                        </div>
                      )}
                      {value !== undefined && value > 0.05 && (
                        <div className="text-danger">
                          <TrendingUp className="h-4 w-4" />
                        </div>
                      )}
                    </div>
                  </div>
                </GradientCard>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Insights */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, delay: 0.6 }}
      >
        <GradientCard>
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              <h4 className="font-semibold">Quality Insights</h4>
            </div>

            <div className="grid gap-4 md:grid-cols-2 text-sm">
              <div className="text-left">
                <p className="text-foreground/70 mb-2">What this means:</p>
                <ul className="space-y-1 text-foreground/60">
                  <li>• High coverage indicates good content discovery</li>
                  <li>• Quality rate shows filtering effectiveness</li>
                  <li>• Low PII risk ensures compliance</li>
                </ul>
              </div>
              <div className="text-left">
                <p className="text-foreground/70 mb-2">Next steps:</p>
                <ul className="space-y-1 text-foreground/60">
                  <li>• Review sample data for content quality</li>
                  <li>• Adjust keywords if relevance is low</li>
                  <li>• Consider quality tier upgrade for better results</li>
                </ul>
              </div>
            </div>
          </div>
        </GradientCard>
      </motion.div>
    </div>
  );
}
