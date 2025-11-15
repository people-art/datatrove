"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useI18n } from "@/lib/i18n";
import { useAuth } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Sparkles, Menu } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

export function MainNav() {
  const { t, language, setLanguage } = useI18n();
  const { isAuthenticated, login, logout, user } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLanguageChange = (nextLocale: 'en' | 'zh') => {
    document.cookie = `NEXT_LOCALE=${nextLocale}; path=/`;
    setLanguage(nextLocale);
    router.refresh();
  };

  const links = [
    { href: "/features", labelKey: "nav.features" },
    { href: "/pricing", labelKey: "nav.pricing" },
    { href: "/docs", labelKey: "nav.docs" },
    { href: "/dashboard", labelKey: "nav.dashboard" },
  ];

  return (
    <nav className="sticky top-0 z-40 border-b border-neutral-200/80 bg-white/85 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
        {/* Left: Brand */}
        <Link href="/" className="flex items-center gap-2 font-semibold text-neutral-900">
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-neutral-900 text-white text-[11px]">
            F
          </span>
          <span>FineData</span>
        </Link>

        {/* Center: Navigation */}
        <ul className="hidden md:flex items-center gap-6 text-sm text-neutral-600">
          {links.map(link => {
            const active = pathname === link.href;
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={cn(
                    "pb-0.5 border-b-2 border-transparent hover:text-neutral-900 hover:border-neutral-300 transition-colors",
                    active && "text-neutral-900 border-neutral-900"
                  )}
                >
                  {t(link.labelKey)}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Right: Actions + Mobile Menu */}
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleLanguageChange(language === 'en' ? 'zh' : 'en')}
            className="flex items-center gap-1.5 text-sm"
          >
            <span className="hidden sm:inline">{language === 'en' ? '中文' : 'EN'}</span>
            <span className="sm:hidden">{language === 'en' ? 'ZH' : 'EN'}</span>
          </Button>

          <ThemeToggle />

          {isAuthenticated ? (
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-sm text-neutral-600">{user?.name || 'User'}</span>
              <button
                onClick={logout}
                className="h-8 px-3 text-xs rounded-full border border-neutral-300 hover:bg-neutral-50"
              >
                {t("nav.signout")}
              </button>
            </div>
          ) : (
            <button
              onClick={login}
              className="hidden sm:inline-flex h-8 px-3 text-xs rounded-full border border-neutral-300 hover:bg-neutral-50"
            >
              {t("nav.signin")}
            </button>
          )}

          <Link
            href="/new"
            className="hidden sm:inline-flex h-8 px-4 text-xs rounded-full bg-neutral-900 text-white hover:bg-neutral-800 transition-colors"
          >
            {t("nav.createDataset")}
          </Link>

          {/* Mobile Menu */}
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="md:hidden">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-80">
              <div className="flex flex-col gap-6 mt-6">
                {/* Mobile Navigation */}
                <nav className="flex flex-col gap-2">
                  {links.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        "px-4 py-3 text-sm rounded-md transition-colors",
                        pathname === item.href
                          ? "bg-neutral-100 text-neutral-900"
                          : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50"
                      )}
                    >
                      {t(item.labelKey)}
                    </Link>
                  ))}
                </nav>

                {/* Mobile Actions */}
                <div className="flex flex-col gap-3 pt-4 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleLanguageChange(language === 'en' ? 'zh' : 'en')}
                    className="flex items-center gap-1.5 justify-start"
                  >
                    <span>{language === 'en' ? '中文' : 'EN'}</span>
                  </Button>
                  <ThemeToggle />
                  <div className="pt-2 border-t">
                    <Link href="/new" onClick={() => setMobileMenuOpen(false)}>
                      <Button className="w-full mb-2">
                        {t("nav.createDataset")}
                      </Button>
                    </Link>
                    {isAuthenticated ? (
                      <div className="space-y-2">
                        <div className="text-sm text-neutral-600 text-center py-2">
                          {t('nav.signedInAs')} {user?.name || 'User'}
                        </div>
                        <Button
                          onClick={() => {
                            logout();
                            setMobileMenuOpen(false);
                          }}
                          variant="outline"
                          className="w-full"
                        >
                          {t('nav.signout')}
                        </Button>
                      </div>
                    ) : (
                      <Button
                        onClick={() => {
                          login();
                          setMobileMenuOpen(false);
                        }}
                        variant="outline"
                        className="w-full"
                      >
                        {t("nav.signin")}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
}
