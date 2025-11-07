"use client";

import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import { useHealthCheck } from '@/hooks/use-api';

export function Footer() {
  const { t } = useI18n();
  const { data: health } = useHealthCheck();

  const getStatusColor = () => {
    if (!health) return 'bg-gray-400';
    return health.status === 'healthy' ? 'bg-emerald-500' : 'bg-red-500';
  };

  const getStatusText = () => {
    if (!health) return 'Checking...';
    return health.status === 'healthy' ? 'Healthy' : 'Degraded';
  };

  return (
    <footer className="border-t border-neutral-200/80 bg-white/90 backdrop-blur mt-16">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
        {/* Desktop Layout */}
        <div className="hidden md:flex items-center justify-between">
          {/* Left: Brand */}
          <div className="flex flex-col">
            <span className="font-semibold text-foreground">FineData</span>
            <span className="text-sm text-muted-foreground mt-1">
              {t('footer_tagline') || 'Custom domain datasets for AI teams.'}
            </span>
          </div>

          {/* Center: Navigation */}
          <div className="flex items-center gap-6">
            <Link href="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Docs
            </Link>
            <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Status
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Security
            </a>
          </div>

          {/* Right: Copyright & Status */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">© {new Date().getFullYear()} FineData</span>
            <div className="flex items-center gap-2">
              <span className={`h-1.5 w-1.5 rounded-full ${getStatusColor()}`} />
              <span className="text-sm text-muted-foreground">API: {getStatusText()}</span>
            </div>
          </div>
        </div>

        {/* Mobile Layout */}
        <div className="md:hidden space-y-4">
          {/* Row 1: Brand + Status */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="font-semibold text-foreground">FineData</span>
              <span className="text-sm text-muted-foreground mt-1">
                {t('footer_tagline') || 'Custom domain datasets for AI teams.'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`h-1.5 w-1.5 rounded-full ${getStatusColor()}`} />
              <span className="text-xs text-muted-foreground">API: {getStatusText()}</span>
            </div>
          </div>

          {/* Row 2: Navigation */}
          <div className="flex items-center justify-center gap-6 pt-2 border-t border-neutral-200/50">
            <Link href="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Docs
            </Link>
            <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Status
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Security
            </a>
          </div>

          {/* Copyright */}
          <div className="text-center pt-2 border-t border-neutral-200/50">
            <span className="text-xs text-muted-foreground">© {new Date().getFullYear()} FineData</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
