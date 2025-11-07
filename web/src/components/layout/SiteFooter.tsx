"use client";

import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import { useHealthCheck } from '@/hooks/use-api';

export function SiteFooter() {
  const { t } = useI18n();
  const { data: health } = useHealthCheck();

  const color =
    !health ? "bg-gray-400" :
    health.status === "healthy" ? "bg-emerald-500" :
    health.status === "degraded" ? "bg-amber-500" : "bg-red-500";

  return (
    <footer className="border-t border-neutral-200/80 bg-white/90 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-neutral-500">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-neutral-800">FineData</span>
          <span className="hidden xs:inline-block">
            {t("footer.tagline") || "Custom domain datasets for AI teams."}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/docs" className="hover:text-neutral-800">{t("footer.docs") || "Docs"}</Link>
          <Link href="/pricing" className="hover:text-neutral-800">{t("footer.pricing") || "Pricing"}</Link>
          <Link href="/status" className="hover:text-neutral-800">{t("footer.status") || "Status"}</Link>
          <Link href="/security" className="hover:text-neutral-800">{t("footer.security") || "Security"}</Link>
        </div>

        <div className="flex items-center gap-2">
          <span>© 2025 FineData</span>
          <span className="inline-flex items-center gap-1">
            <span className={`h-2 w-2 rounded-full ${color}`} />
            <span>{t(`footer.apiStatus.${health?.status || 'checking'}`) || `API: ${health?.status === 'healthy' ? 'Healthy' : 'Checking...'}`}</span>
          </span>
        </div>
      </div>
    </footer>
  );
}
