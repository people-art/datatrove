"use client";

import Link from "next/link";
import { useI18n } from '@/lib/i18n';
import { Database, Shield, Zap, Globe, BarChart, Lock, Cpu, Users, Building, ArrowRight } from 'lucide-react';
import { Button } from "@/components/ui/button";

export default function FeaturesPage() {
  const { t } = useI18n();

  const features = [
    {
      icon: Database,
      title: 'AI 驱动过滤',
      description: '基于本体的关键词扩展、LLM 相关性打分、多阶段质量过滤，精准匹配你的细分领域和使用场景。'
    },
    {
      icon: Zap,
      title: '万亿级网页覆盖',
      description: '基于 Common Crawl 与工程化流水线，稳定处理数十亿网页，配置可追踪、结果可复现。'
    },
    {
      icon: Shield,
      title: '企业级隐私与合规',
      description: '内置 PII 检测、医疗场景 HIPAA 规则、脱敏与审计日志，确保数据安全合规。'
    },
    {
      icon: Globe,
      title: '任意垂直领域定制',
      description: '支持金融、医疗、法律、教育、能源、安全、机器人等高价值领域，以及自定义业务本体。'
    },
    {
      icon: BarChart,
      title: '完整质量度量',
      description: '每次运行提供覆盖率、去重率、语言分布、毒性和隐私指标，以及领域相关性报告。'
    },
    {
      icon: Lock,
      title: '私有交付与权限控制',
      description: '通过 Hugging Face 私有仓库或 S3 等方式交付，支持精细化访问控制和审计。'
    }
  ];

  const builtFor = [
    { name: 'Fintech', icon: Building },
    { name: 'Healthcare', icon: Shield },
    { name: 'LLM Labs', icon: Cpu },
    { name: 'Research', icon: Users }
  ];

  return (
    <div className="space-y-16">
      <header className="mb-8">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {t('features_title')}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          {t('features_subtitle')}
        </p>
      </header>

      {/* Main Features */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          {features.slice(0, 3).map((feature, index) => (
            <div key={index} className="flex gap-4 p-4 rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm">
              <feature.icon className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium mb-1">{feature.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-4">
          {features.slice(3).map((feature, index) => (
            <div key={index + 3} className="flex gap-4 p-4 rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm">
              <feature.icon className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium mb-1">{feature.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Highlights */}
      <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
        <h2 className="text-lg font-semibold mb-4">技术亮点</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <div className="font-medium">Common Crawl 集成</div>
              <div className="text-muted-foreground text-xs">直接处理原始 Common Crawl 数据，无中间环节</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <div className="font-medium">Slurm 集群支持</div>
              <div className="text-muted-foreground text-xs">大规模分布式处理，支持数TB数据集生成</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <div className="font-medium">多语言支持</div>
              <div className="text-muted-foreground text-xs">自动语言检测与过滤，支持100+种语言</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <div className="font-medium">实时质量监控</div>
              <div className="text-muted-foreground text-xs">处理过程中实时监控数据质量指标</div>
            </div>
          </div>
        </div>
      </div>

      {/* Built For */}
      <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
        <h2 className="text-lg font-semibold mb-4">适用于</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {builtFor.map((item, index) => (
            <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <item.icon className="h-5 w-5 text-primary" />
              <span className="text-sm font-medium">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-4">准备开始了吗？</h2>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          在几分钟内创建你的第一个定制数据集
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
      </div>
    </div>
  );
}