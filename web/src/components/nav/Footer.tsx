import Link from 'next/link';
import { useI18n } from '@/lib/i18n';

export function Footer() {
  const { t } = useI18n();

  return (
    <footer className="bg-slate-900 text-slate-300">
      <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">FD</span>
              </div>
              <span className="font-bold text-white">FineData</span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              Custom domain datasets powered by AI. Generate high-quality, domain-specific training data from billions of web pages.
            </p>
            <p className="text-slate-500 text-xs">
              © 2025 FineData. All rights reserved.
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/features" className="text-slate-400 hover:text-white transition-colors">
                  {t('features')}
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-slate-400 hover:text-white transition-colors">
                  {t('pricing')}
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-slate-400 hover:text-white transition-colors">
                  {t('docs')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/privacy" className="text-slate-400 hover:text-white transition-colors">
                  {t('privacy')}
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-slate-400 hover:text-white transition-colors">
                  {t('terms')}
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-slate-400 hover:text-white transition-colors">
                  {t('contact')}
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-slate-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-6 mb-4 md:mb-0">
            <span className="text-slate-500 text-sm">Compatible with:</span>
            <div className="flex items-center space-x-4 opacity-60">
              {/* Placeholder logos */}
              <div className="w-6 h-6 bg-slate-700 rounded"></div>
              <div className="w-6 h-6 bg-slate-700 rounded"></div>
              <div className="w-6 h-6 bg-slate-700 rounded"></div>
            </div>
          </div>
          <div className="text-slate-500 text-sm">
            Trusted by AI teams worldwide
          </div>
        </div>
      </div>
    </footer>
  );
}
