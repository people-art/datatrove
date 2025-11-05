"use client";

import React, { useEffect, useRef, useCallback, useState } from "react";

export function useKeyboardNavigation() {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Enhanced keyboard navigation
    if (event.key === "Tab") {
      // Add visual focus indicators
      document.body.classList.add("keyboard-navigation");
    }
  }, []);

  const handleMouseDown = useCallback(() => {
    // Remove visual focus indicators when mouse is used
    document.body.classList.remove("keyboard-navigation");
  }, []);

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleMouseDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleMouseDown);
    };
  }, [handleKeyDown, handleMouseDown]);
}

export function useFocusTrap(containerRef: React.RefObject<HTMLElement>) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key !== "Tab") return;

    const container = containerRef.current;
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement?.focus();
      }
    }
  }, [containerRef]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown, containerRef]);
}

export function useAnnounce(message: string, priority: "polite" | "assertive" = "polite") {
  const announceRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!announceRef.current) {
      const announcer = document.createElement("div");
      announcer.setAttribute("aria-live", priority);
      announcer.setAttribute("aria-atomic", "true");
      announcer.style.position = "absolute";
      announcer.style.left = "-10000px";
      announcer.style.width = "1px";
      announcer.style.height = "1px";
      announcer.style.overflow = "hidden";
      document.body.appendChild(announcer);
      announceRef.current = announcer;
    }

    if (announceRef.current && message) {
      announceRef.current.textContent = message;
    }
  }, [message, priority]);

  return announceRef;
}

export function useReducedMotion() {
  const prefersReducedMotion = useRef(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    prefersReducedMotion.current = mediaQuery.matches;

    const handleChange = (event: MediaQueryListEvent) => {
      prefersReducedMotion.current = event.matches;
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return prefersReducedMotion.current;
}

export function useSkipLinks() {
  useEffect(() => {
    const handleSkipLink = (event: KeyboardEvent) => {
      if (event.key === "Enter" && event.target instanceof HTMLAnchorElement) {
        const href = event.target.getAttribute("href");
        if (href?.startsWith("#")) {
          event.preventDefault();
          const target = document.querySelector(href);
          if (target instanceof HTMLElement) {
            target.focus();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }
      }
    };

    document.addEventListener("keydown", handleSkipLink);
    return () => document.removeEventListener("keydown", handleSkipLink);
  }, []);
}

// High contrast mode detection
export function useHighContrast() {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    const checkHighContrast = () => {
      // Check for Windows high contrast mode
      const testElement = document.createElement("div");
      testElement.style.color = "rgb(31, 41, 55)"; // gray-800
      document.body.appendChild(testElement);

      const computedColor = window.getComputedStyle(testElement).color;
      document.body.removeChild(testElement);

      // If the computed color is different, high contrast mode might be active
      setIsHighContrast(computedColor !== "rgb(31, 41, 55)");
    };

    checkHighContrast();

    // Listen for changes (though this is rare)
    const mediaQuery = window.matchMedia("(prefers-contrast: high)");
    const handleChange = () => checkHighContrast();

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return isHighContrast;
}
