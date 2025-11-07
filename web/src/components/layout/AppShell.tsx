"use client";

import { ReactNode } from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
      <Header />
      <main className="pt-16">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}
