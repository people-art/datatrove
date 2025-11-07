"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { ArrowRight, Database, Shield, Zap, Sparkles, Activity, Clock } from "lucide-react";

// Mock live job data - in real app, fetch from API
const liveJobStats = {
  activeBenchmarks: 3,
  activeOrders: 1,
  avgCompletionTime: "2.5h"
};

export default function Home() {
  const { t } = useI18n();

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="max-w-3xl mx-auto text-center pt-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-medium mb-6">
          <Sparkles className="h-4 w-4" />
          Custom Domain Datasets Powered by AI
        </div>

        <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4">
          {t('hero_title') || 'Custom Domain Datasets for AI Teams'}
        </h1>

        <p className="text-sm md:text-base text-muted-foreground mb-8 max-w-2xl mx-auto">
          {t('hero_subtitle') || 'From billions of web pages to curated, domain-specific datasets — ready for specialized models and RAG systems.'}
        </p>

        <div className="flex gap-3 justify-center">
          <Link href="/new">
            <Button size="lg" className="gap-2">
              {t('hero_cta_primary') || 'Create Dataset'}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs">
            <Button variant="outline" size="lg">
              {t('hero_cta_secondary') || 'View Docs'}
            </Button>
          </Link>
        </div>
      </section>

      {/* Why Choose Section */}
      <section>
        <h2 className="text-2xl font-semibold text-center mb-12">{t('why_title') || 'Why FineData'}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Database className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('why_ai_filtering') || 'AI-Powered Filtering'}</h3>
            <p className="text-sm text-muted-foreground">
              {t('why_ai_filtering_desc') || 'Ontology-based keyword expansion, LLM relevance scoring, multi-stage quality filtering for precise domain matching.'}
            </p>
          </div>
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Zap className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('why_scale') || 'Trillion-Scale Coverage'}</h3>
            <p className="text-sm text-muted-foreground">
              {t('why_scale_desc') || 'Built on Common Crawl with engineered pipelines, processing billions of pages with traceable configs and reproducible results.'}
            </p>
          </div>
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Shield className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('why_privacy') || 'Enterprise Privacy & Compliance'}</h3>
            <p className="text-sm text-muted-foreground">
              {t('why_privacy_desc') || 'Built-in PII detection, HIPAA rules for healthcare, anonymization and audit logs ensuring data security and compliance.'}
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section>
        <h2 className="text-2xl font-semibold text-center mb-12">{t('workflow_title') || 'How It Works'}</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              1
            </div>
            <h3 className="text-sm font-medium mb-2">提交需求</h3>
            <p className="text-xs text-muted-foreground">
              配置领域、关键词、语言和质量要求
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              2
            </div>
            <h3 className="text-sm font-medium mb-2">运行 Benchmark</h3>
            <p className="text-xs text-muted-foreground">
              本地 100 万页基准验证，生成质量报告
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              3
            </div>
            <h3 className="text-sm font-medium mb-2">确认并支付</h3>
            <p className="text-xs text-muted-foreground">
              基于基准结果定价，无隐藏费用
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              4
            </div>
            <h3 className="text-sm font-medium mb-2">集群生产交付</h3>
            <p className="text-xs text-muted-foreground">
              Slurm 集群处理，私有仓库交付
            </p>
          </div>
        </div>
      </section>

      {/* Live Job Snapshot */}
      <section className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
        <h3 className="text-sm font-medium mb-4 flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          系统状态概览
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <Database className="h-5 w-5 text-blue-500" />
            <div>
              <div className="text-lg font-semibold">{liveJobStats.activeBenchmarks}</div>
              <div className="text-xs text-muted-foreground">活跃基准任务</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Zap className="h-5 w-5 text-green-500" />
            <div>
              <div className="text-lg font-semibold">{liveJobStats.activeOrders}</div>
              <div className="text-xs text-muted-foreground">生产中订单</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Clock className="h-5 w-5 text-orange-500" />
            <div>
              <div className="text-lg font-semibold">{liveJobStats.avgCompletionTime}</div>
              <div className="text-xs text-muted-foreground">平均完成时间</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
