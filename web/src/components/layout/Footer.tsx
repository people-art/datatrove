"use client";

import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import { useHealthCheck } from '@/hooks/use-api';

export function Footer() {
  const { t } = useI18n();
  const { data: health } = useHealthCheck();

  return (
    <footer className="border-t border-border/60 mt-16">
      <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-xs text-foreground">FineData</span>
          <span>Custom domain datasets for AI teams.</span>
        </div>

        <div className="flex flex-wrap gap-4">
          <Link href="/docs" className="hover:text-foreground transition-colors">
            Docs
          </Link>
          <Link href="/pricing" className="hover:text-foreground transition-colors">
            Pricing
          </Link>
          <a href="#" className="hover:text-foreground transition-colors">
            Status
          </a>
          <a href="#" className="hover:text-foreground transition-colors">
            Security
          </a>
        </div>

        <div className="flex items-center gap-2">
          <span>© {new Date().getFullYear()} FineData</span>
          <span className="h-1 w-1 rounded-full bg-emerald-500" />
          <span>API: {health?.status === 'healthy' ? 'Healthy' : 'Checking...'}</span>
        </div>
      </div>
    </footer>
  );
}
