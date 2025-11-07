"use client";

import Link from "next/link";
import { useI18n } from '@/lib/i18n';
import { ArrowRight, Database, Zap, Shield, Code, Cpu, Server } from 'lucide-react';
import { Button } from "@/components/ui/button";

export default function DocsPage() {
  const { t } = useI18n();

  const workflow = [
    {
      step: 1,
      title: '提交数据需求',
      description: '通过控制台或 API 配置领域、关键词、语言、时间范围和质量档位。',
      icon: Database
    },
    {
      step: 2,
      title: '运行 100 万页 Benchmark',
      description: '使用真实流水线在本地环境运行预览任务，返回质量指标和可下载样本。',
      icon: Zap
    },
    {
      step: 3,
      title: '确认方案并支付',
      description: '确认预览效果与报价后，通过安全银行卡支付完成下单。',
      icon: Shield
    },
    {
      step: 4,
      title: '集群生产与私有交付',
      description: '在 Slurm 集群上执行全量生产，完成后通过邮件发送 Hugging Face 私有仓库链接。',
      icon: Code
    }
  ];

  const apiEndpoints = [
    'POST /benchmark/quote —— 根据配置生成价格预估。',
    'POST /benchmark/jobs —— 创建 100 万页 Benchmark 任务。',
    'GET /benchmark/jobs/{id} —— 轮询任务状态与质量指标。',
    'POST /orders —— 基于 quote 和 job 创建订单（支持幂等键）。',
    'GET /orders/{id} —— 查询订单与支付状态。',
    'GET /orders/{id}/production —— 查看生产流水线进度。',
    'POST /email/validate —— 校验邮箱格式/MX/SMTP/一次性域名。',
    'POST /checkout/session —— 创建支付会话（兼容 Stripe）。'
  ];

  return (
    <div className="space-y-16">
      {/* Header */}
      <header className="text-center">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight mb-4">
          快速开始
        </h1>
        <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
          了解 FineData 的工作原理，从需求提交到私有数据集交付仅需四个可预测步骤。
        </p>
      </header>

      {/* Workflow */}
      <div>
        <h2 className="text-xl font-semibold mb-8 text-center">工作流程</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            {workflow.slice(0, 2).map((step, index) => (
              <div key={index} className="flex gap-4 p-4 rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                    {step.step}
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium mb-2">{step.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
                </div>
                <step.icon className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
              </div>
            ))}
          </div>

          <div className="space-y-4">
            {workflow.slice(2).map((step, index) => (
              <div key={index + 2} className="flex gap-4 p-4 rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                    {step.step}
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium mb-2">{step.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
                </div>
                <step.icon className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* API Overview */}
      <div>
        <h2 className="text-xl font-semibold mb-6">API 概览</h2>
        <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
          <div className="grid gap-3 md:grid-cols-2">
            {apiEndpoints.map((endpoint, index) => (
              <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <code className="text-xs font-mono text-muted-foreground leading-relaxed">{endpoint}</code>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Technical Notes */}
      <div>
        <h2 className="text-xl font-semibold mb-6">技术细节</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4">
            <h3 className="font-medium mb-2 flex items-center gap-2">
              <Server className="h-4 w-4 text-primary" />
              错误处理
            </h3>
            <p className="text-xs text-muted-foreground">
              所有错误均使用统一结构：错误码、信息、建议和时间戳，便于排查。
            </p>
          </div>
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4">
            <h3 className="font-medium mb-2 flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              幂等性
            </h3>
            <p className="text-xs text-muted-foreground">
              所有创建类接口建议携带幂等键，确保网络重试是安全的。
            </p>
          </div>
          <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-4">
            <h3 className="font-medium mb-2 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-primary" />
              隔离性
            </h3>
            <p className="text-xs text-muted-foreground">
              生产任务彼此隔离，交付通过私有仓库或安全存储完成。
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-medium mb-4">
          准备开始？
        </div>
        <h2 className="text-xl font-semibold mb-4">
          在几分钟内获取你的第一个数据集
        </h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          从免费的 benchmark 开始，体验 FineData 如何提升你的训练数据质量。
        </p>
        <div className="flex gap-3 justify-center">
          <Link href="/new">
            <Button size="lg" className="gap-2">
              开始 Benchmark
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/features">
            <Button variant="outline" size="lg">
              了解更多
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}