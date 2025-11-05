"use client";

import { useKeyboardNavigation, useSkipLinks } from "@/hooks/use-accessibility";

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export function AccessibilityProvider({ children }: AccessibilityProviderProps) {
  // Initialize keyboard navigation
  useKeyboardNavigation();

  // Initialize skip links
  useSkipLinks();

  return <>{children}</>;
}
