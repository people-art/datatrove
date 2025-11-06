"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { Menu, X, Activity, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useHealthCheck } from "@/hooks/use-api";
import { useI18n } from "@/lib/i18n";
import { Badge } from "@/components/ui/badge";

// Skip to main content link
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
    >
      Skip to main content
    </a>
  );
}

export function MainNav() {
  const { t, language, setLanguage } = useI18n();
  const pathname = usePathname();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { href: "/features", label: t('features') },
    { href: "/pricing", label: t('pricing') },
    { href: "/docs", label: t('docs') },
  ];

  // Mock task counts (in real app, aggregate from queries)
  const taskCounts = {
    running: 2,
    queued: 1,
    total: 3,
  };

  const healthCheck = useHealthCheck();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname?.startsWith(href);
  };

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-background/80 backdrop-blur-md border-b border-line"
          : "bg-transparent"
      }`}
    >
      <nav className="container flex items-center justify-between h-16">
        {/* Logo */}
        <Link
          href="/"
          className="text-xl font-semibold text-foreground hover:text-primary transition-colors"
        >
          FineData
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive(item.href)
                  ? "text-primary"
                  : "text-foreground/70"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>

                {/* Right side actions */}
                <div className="flex items-center space-x-3">
                  {/* Health indicator */}
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-2 w-2 rounded-full ${
                        healthCheck.isSuccess
                          ? 'bg-green-500'
                          : healthCheck.isError
                          ? 'bg-red-500'
                          : 'bg-yellow-500 animate-pulse'
                      }`}
                      title={
                        healthCheck.isSuccess
                          ? 'API healthy'
                          : healthCheck.isError
                          ? 'API unhealthy'
                          : 'Checking API health...'
                      }
                    />
                    <Activity className="h-4 w-4 text-foreground/70" />
                  </div>

                  {/* Task badge */}
                  {taskCounts.total > 0 && (
                    <Link href="/dashboard">
                      <Badge variant="secondary" className="relative cursor-pointer hover:bg-secondary/80 transition-colors">
                        {taskCounts.total}
                        <span className="sr-only">
                          {taskCounts.running} running, {taskCounts.queued} queued tasks
                        </span>
                      </Badge>
                    </Link>
                  )}

                  {/* Language switcher */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
                    className="flex items-center gap-1"
                  >
                    <Globe className="h-4 w-4" />
                    <span className="text-xs font-medium">
                      {language === 'en' ? '中文' : 'EN'}
                    </span>
                  </Button>

                  <ThemeToggle />

                  {/* User menu placeholder */}
                  <Button variant="ghost" size="sm">
                    Sign in
                  </Button>

                  {/* Desktop CTA */}
                  <div className="hidden md:block">
                    <Button asChild size="sm">
                      <Link href="/new">{t('createDataset')}</Link>
                    </Button>
                  </div>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
            <span className="sr-only">Toggle menu</span>
          </Button>
        </div>
      </nav>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-line bg-background/95 backdrop-blur-md">
          <div className="container py-4 space-y-3">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block text-sm font-medium transition-colors hover:text-primary ${
                  isActive(item.href)
                    ? "text-primary"
                    : "text-foreground/70"
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="pt-2">
              <Button asChild size="sm" className="w-full">
                <Link href="/new" onClick={() => setIsMobileMenuOpen(false)}>
                  Create Dataset
                </Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
