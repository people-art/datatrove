"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { useSystemStats } from "@/hooks/use-api";
import { ArrowRight, Database, Shield, Zap, Sparkles, Activity, Clock, CheckCircle } from "lucide-react";

export default function Home() {
  const { t } = useI18n();
  const { loading, activeBenchmarks, completedBenchmarks, activeOrders, totalTasks } = useSystemStats();

  // Fallback stats for when no data is available
  const displayStats = {
    activeBenchmarks: activeBenchmarks || 0,
    completedBenchmarks: completedBenchmarks || 0,
    activeOrders: activeOrders || 0,
    totalTasks: totalTasks || 0,
  };

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="max-w-3xl mx-auto text-center pt-8">
        <div className="text-[10px] uppercase tracking-[0.16em] text-neutral-500 mb-4">
          {t('home.hero.eyebrow')}
        </div>

        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-neutral-900 mb-4">
          {t('home.hero.title')}
        </h1>

        <p className="mx-auto max-w-2xl text-sm text-neutral-600 mb-8">
          {t('home.hero.subtitle')}
        </p>

        <div className="flex justify-center gap-3">
          <Link href="/new">
            <Button size="lg" className="gap-2">
              {t('home.hero.cta_primary')}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs">
            <Button variant="outline" size="lg">
              {t('home.hero.cta_secondary')}
            </Button>
          </Link>
        </div>
      </section>

      {/* Why Choose Section */}
      <section>
        <h2 className="text-base font-semibold text-neutral-900 text-center mb-8">{t('home.why.title')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Database className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('home.why.ai_filtering_title')}</h3>
            <p className="text-sm text-muted-foreground">
              {t('home.why.ai_filtering_desc')}
            </p>
          </div>
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Zap className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('home.why.scale_title')}</h3>
            <p className="text-sm text-muted-foreground">
              {t('home.why.scale_desc')}
            </p>
          </div>
          <div className="bg-card/70 border border-border/70 rounded-2xl px-6 py-5 hover:shadow-sm transition-all">
            <Shield className="h-6 w-6 text-primary mb-3" />
            <h3 className="text-base font-medium mb-2">{t('home.why.privacy_title')}</h3>
            <p className="text-sm text-muted-foreground">
              {t('home.why.privacy_desc')}
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section>
        <h2 className="text-base font-semibold text-neutral-900 text-center mb-8">{t('home.workflow.title')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              1
            </div>
            <h3 className="text-sm font-medium mb-2">{t('home.workflow.step1_title')}</h3>
            <p className="text-xs text-muted-foreground">
              {t('home.workflow.step1_desc')}
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              2
            </div>
            <h3 className="text-sm font-medium mb-2">{t('home.workflow.step2_title')}</h3>
            <p className="text-xs text-muted-foreground">
              {t('home.workflow.step2_desc')}
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              3
            </div>
            <h3 className="text-sm font-medium mb-2">{t('home.workflow.step3_title')}</h3>
            <p className="text-xs text-muted-foreground">
              {t('home.workflow.step3_desc')}
            </p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-medium mb-3">
              4
            </div>
            <h3 className="text-sm font-medium mb-2">{t('home.workflow.step4_title')}</h3>
            <p className="text-xs text-muted-foreground">
              {t('home.workflow.step4_desc')}
            </p>
          </div>
        </div>
      </section>

      {/* Live Job Snapshot */}
      <section className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
        <h3 className="text-sm font-medium mb-4 flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          {t('home.system_status_overview')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-3">
            <Database className="h-5 w-5 text-blue-500" />
            <div>
              <div className="text-lg font-semibold">{displayStats.activeBenchmarks}</div>
              <div className="text-xs text-muted-foreground">
                {t('home.stats.active_benchmarks')}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <div>
              <div className="text-lg font-semibold">{displayStats.completedBenchmarks}</div>
              <div className="text-xs text-muted-foreground">
                {t('home.stats.completed_benchmarks')}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Zap className="h-5 w-5 text-orange-500" />
            <div>
              <div className="text-lg font-semibold">{displayStats.activeOrders}</div>
              <div className="text-xs text-muted-foreground">
                {t('home.stats.active_orders')}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Activity className="h-5 w-5 text-purple-500" />
            <div>
              <div className="text-lg font-semibold">{displayStats.totalTasks}</div>
              <div className="text-xs text-muted-foreground">
                {t('home.stats.total_tasks')}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
