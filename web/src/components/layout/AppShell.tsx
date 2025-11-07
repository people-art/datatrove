"use client";

import { ReactNode } from "react";
import { MainNav } from "@/components/nav/MainNav";
import { SiteFooter } from "./SiteFooter";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <MainNav />
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 pt-10 pb-16">
          {children}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
