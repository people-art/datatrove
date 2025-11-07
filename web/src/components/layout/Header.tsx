"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n";
import { useHealthCheck } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Activity, Globe, Menu } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

// Mock data for active tasks - in real app, aggregate from API hooks
const mockTasks = {
  total: 3,
  running: 1,
  queued: 2
};

export function Header() {
  const { t, language, setLanguage } = useI18n();
  const pathname = usePathname();
  const { data: health } = useHealthCheck();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { href: "/features", label: t("features") },
    { href: "/pricing", label: t("pricing") },
    { href: "/docs", label: t("docs") },
    { href: "/dashboard", label: t("dashboard") },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <header className="sticky top-0 z-40 h-16 border-b border-neutral-200/80 bg-white/85 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 h-full flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="font-semibold text-lg">FineData</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`relative px-3 py-2 text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? "text-neutral-900 border-b-2 border-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {item.label}
            </Link>
          ))}
          {/* Task Badge next to Dashboard */}
          {isActive('/dashboard') && mockTasks.total > 0 && (
            <Badge
              variant="secondary"
              className="ml-1 px-2 py-0.5 text-xs bg-primary/10 text-primary border-primary/20"
            >
              {mockTasks.total}
            </Badge>
          )}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Language Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
            className="flex items-center gap-1.5 text-sm"
          >
            <Globe className="h-4 w-4" />
            <span className="hidden sm:inline">{language === 'en' ? '中文' : 'EN'}</span>
          </Button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Sign in */}
          <Button variant="outline" size="sm" className="text-muted-foreground hover:text-foreground">
            Sign in
          </Button>

          {/* Create Dataset */}
          <Link href="/new">
            <Button size="sm" className="hidden sm:inline-flex">
              Create Dataset
            </Button>
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
                  {navItems.map((item) => (
                    <div key={item.href} className="flex items-center justify-between">
                      <Link
                        href={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex-1 px-4 py-3 text-sm rounded-md transition-colors ${
                          isActive(item.href)
                            ? "bg-accent text-accent-foreground"
                            : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                        }`}
                      >
                        {item.label}
                      </Link>
                      {item.href === '/dashboard' && mockTasks.total > 0 && (
                        <Badge
                          variant="secondary"
                          className="ml-2 px-2 py-0.5 text-xs bg-primary/10 text-primary border-primary/20"
                        >
                          {mockTasks.total}
                        </Badge>
                      )}
                    </div>
                  ))}
                </nav>

                {/* Mobile Actions */}
                <div className="flex flex-col gap-3 pt-4 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
                    className="flex items-center gap-1.5 justify-start"
                  >
                    <Globe className="h-4 w-4" />
                    {language === 'en' ? '中文' : 'EN'}
                  </Button>
                  <ThemeToggle />
                  <div className="pt-2 border-t">
                    <Link href="/new" onClick={() => setMobileMenuOpen(false)}>
                      <Button className="w-full mb-2">
                        Create Dataset
                      </Button>
                    </Link>
                    <Button variant="outline" className="w-full">
                      Sign in
                    </Button>
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
