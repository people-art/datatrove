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
      <main className="min-h-[calc(100vh-64px)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 pt-10 pb-16">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}
