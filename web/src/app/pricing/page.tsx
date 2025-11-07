"use client";

import Link from "next/link";
import { useI18n } from '@/lib/i18n';
import { Check, ArrowRight } from 'lucide-react';
import { Button } from "@/components/ui/button";

export default function PricingPage() {
  const { t } = useI18n();

  const pricingCards = [
    {
      name: '预览 Benchmark',
      price: '免费',
      unit: '',
      desc: '本地 100 万页基准运行，先看效果再决策。',
      items: [
        '自定义领域与关键词',
        '端到端流水线模拟',
        '质量与覆盖率报告',
        '可下载样本数据集'
      ],
      popular: false,
      action: '开始免费测试',
      href: '/new'
    },
    {
      name: '标准生产版',
      price: '50 美元起',
      unit: '每百万 tokens',
      desc: '适用于绝大多数微调与 RAG 场景的高性价比方案。',
      items: [
        '基于 Common Crawl 的数据源',
        '多阶段质量与隐私过滤',
        'Minhash 去重与统计报告',
        'Hugging Face 私有仓交付'
      ],
      popular: true,
      action: '开始使用',
      href: '/new'
    },
    {
      name: '高端定制版',
      price: '定制报价',
      unit: '',
      desc: '面向金融、医疗、政企等高敏感场景的严选数据。',
      items: [
        '更严格的过滤与 LLM 打分',
        '可选专家审核与黑白名单',
        '支持自定义本体与合规策略',
        'SLA、专属支持与治理方案'
      ],
      popular: false,
      action: '联系销售',
      href: '/contact'
    }
  ];

  return (
    <div className="space-y-16">
      <header className="text-center mb-8">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {t('pricing_title')}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl mx-auto">
          {t('pricing_subtitle')}
        </p>
      </header>

      {/* Pricing Cards */}
      <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-4">
        {pricingCards.map((card, index) => (
          <div key={index} className={`relative rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6 ${card.popular ? 'ring-2 ring-primary' : ''}`}>
            {card.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="px-3 py-1 bg-primary text-primary-foreground text-xs font-medium rounded-full">
                  最受欢迎
                </div>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold mb-2">{card.name}</h3>
              <div className="text-3xl font-bold text-primary mb-1">
                {card.price}
                {card.unit && <span className="text-sm font-normal text-muted-foreground"> {card.unit}</span>}
              </div>
              <p className="text-xs text-muted-foreground">{card.desc}</p>
            </div>

            <ul className="space-y-3 mb-8">
              {card.items.map((item, itemIndex) => (
                <li key={itemIndex} className="flex items-start gap-3">
                  <Check className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-muted-foreground">{item}</span>
                </li>
              ))}
            </ul>

            <Link href={card.href}>
              <Button className="w-full" variant={card.popular ? "default" : "outline"}>
                {card.action}
              </Button>
            </Link>
          </div>
        ))}
      </div>

      {/* Important Notes */}
      <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-sm p-6">
        <h2 className="text-lg font-semibold mb-6 text-center">重要说明</h2>
        <div className="grid gap-4 md:grid-cols-1 max-w-4xl mx-auto">
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-sm text-muted-foreground">最终价格由领域难度、时间范围、目标规模、质量档位等综合计算。</p>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-sm text-muted-foreground">在支付前，你将基于 Benchmark 结果看到真实区间报价。</p>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-sm text-muted-foreground">长期合作与多批次任务可提供折扣与专属方案。</p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-4">有疑问？</h2>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          关于定价或需要定制方案？我们随时为您提供帮助。
        </p>
        <div className="flex gap-3 justify-center">
          <Link href="/docs">
            <Button variant="outline" size="lg">
              查看文档
            </Button>
          </Link>
          <Link href="/contact">
            <Button size="lg" className="gap-2">
              联系我们
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
