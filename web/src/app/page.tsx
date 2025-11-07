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
          为 AI 团队定制的<br />领域数据集工厂
        </h1>

        <p className="text-sm md:text-base text-muted-foreground mb-8 max-w-2xl mx-auto">
          从数十亿网页中生成高质量、特定领域的训练数据集，为专业 AI 模型、研究和分析做好准备。
        </p>

        <div className="flex gap-3 justify-center">
          <Link href="/new">
            <Button size="lg" className="gap-2">
              创建数据集
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs">
            <Button variant="outline" size="lg">
              查看文档
            </Button>
          </Link>
        </div>
      </section>

      {/* Why Choose Section */}
      <section>
        <h2 className="text-2xl font-semibold text-center mb-8">为什么选择 FineData</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4 flex flex-col gap-1">
            <Database className="h-5 w-5 text-primary mb-2" />
            <h3 className="text-sm font-medium">AI 驱动过滤</h3>
            <p className="text-xs text-muted-foreground">
              基于本体的关键词扩展、LLM 相关性打分、多阶段质量过滤，精准匹配你的细分领域。
            </p>
          </div>
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4 flex flex-col gap-1">
            <Zap className="h-5 w-5 text-primary mb-2" />
            <h3 className="text-sm font-medium">万亿级网页覆盖</h3>
            <p className="text-xs text-muted-foreground">
              基于 Common Crawl 与工程化流水线，稳定处理数十亿网页，配置可追踪、结果可复现。
            </p>
          </div>
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4 flex flex-col gap-1">
            <Shield className="h-5 w-5 text-primary mb-2" />
            <h3 className="text-sm font-medium">企业级隐私与合规</h3>
            <p className="text-xs text-muted-foreground">
              内置 PII 检测、医疗场景 HIPAA 规则、脱敏与审计日志，确保数据安全合规。
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section>
        <h2 className="text-2xl font-semibold text-center mb-8">工作流程</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
