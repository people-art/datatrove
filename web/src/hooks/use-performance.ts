"use client";

import { useEffect, useRef, useCallback } from "react";

declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

export function usePerformance() {
  const startTimeRef = useRef<number>(0);

  const markStart = useCallback((name: string) => {
    if (typeof window !== "undefined" && "performance" in window) {
      startTimeRef.current = performance.now();
      performance.mark(`${name}-start`);
    }
  }, []);

  const markEnd = useCallback((name: string) => {
    if (typeof window !== "undefined" && "performance" in window && startTimeRef.current) {
      performance.mark(`${name}-end`);
      performance.measure(name, `${name}-start`, `${name}-end`);

      const measure = performance.getEntriesByName(name)[0];
      if (measure) {
        console.log(`Performance: ${name} took ${measure.duration.toFixed(2)}ms`);

        // Send to analytics if available
        if (typeof window.gtag !== "undefined") {
          window.gtag("event", "performance_metric", {
            event_category: "performance",
            event_label: name,
            value: Math.round(measure.duration),
          });
        }
      }
    }
  }, []);

  return { markStart, markEnd };
}

export function useWebVitals() {
  useEffect(() => {
    // Web Vitals tracking
    if (typeof window !== "undefined") {
      // CLS (Cumulative Layout Shift)
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
      });

      observer.observe({ entryTypes: ["layout-shift"] });

      // Report CLS on page unload
      const reportCLS = () => {
        if (clsValue > 0 && typeof window.gtag !== "undefined") {
          window.gtag("event", "web_vitals", {
            event_category: "Web Vitals",
            event_label: "CLS",
            value: Math.round(clsValue * 1000),
          });
        }
      };

      window.addEventListener("beforeunload", reportCLS);

      return () => {
        observer.disconnect();
        window.removeEventListener("beforeunload", reportCLS);
      };
    }
  }, []);
}

export function useLazyLoad() {
  const observerRef = useRef<IntersectionObserver | null>(null);

  const observe = useCallback((element: Element, callback: () => void) => {
    if (!observerRef.current) {
      observerRef.current = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              callback();
              observerRef.current?.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: "50px",
          threshold: 0.1,
        }
      );
    }

    observerRef.current.observe(element);
  }, []);

  const unobserve = useCallback((element: Element) => {
    observerRef.current?.unobserve(element);
  }, []);

  useEffect(() => {
    return () => {
      observerRef.current?.disconnect();
    };
  }, []);

  return { observe, unobserve };
}

export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const debouncedCallback = useCallback(
    ((...args: any[]) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    }) as T,
    [callback, delay]
  );

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return debouncedCallback;
}

export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastExecRef = useRef<number>(0);

  const throttledCallback = useCallback(
    ((...args: any[]) => {
      const now = Date.now();

      if (now - lastExecRef.current >= delay) {
        lastExecRef.current = now;
        callback(...args);
      }
    }) as T,
    [callback, delay]
  );

  return throttledCallback;
}

// Resource hints for critical resources
export function useResourceHints() {
  useEffect(() => {
    if (typeof document === "undefined") return;

    // Preconnect to external domains
    const preconnectDomains = [
      "https://fonts.googleapis.com",
      "https://fonts.gstatic.com",
    ];

    preconnectDomains.forEach((domain) => {
      const link = document.createElement("link");
      link.rel = "preconnect";
      link.href = domain;
      link.crossOrigin = "anonymous";
      document.head.appendChild(link);
    });

    // DNS prefetch for common domains
    const dnsDomains = ["api.github.com"];

    dnsDomains.forEach((domain) => {
      const link = document.createElement("link");
      link.rel = "dns-prefetch";
      link.href = `//${domain}`;
      document.head.appendChild(link);
    });
  }, []);
}

// Critical CSS inlining helper
export function useCriticalCSS() {
  useEffect(() => {
    // This would typically be handled by Next.js or a build tool
    // For runtime critical CSS, we can preload critical styles
    if (typeof document !== "undefined") {
      const criticalStyles = document.querySelectorAll('style[data-critical]');
      criticalStyles.forEach((style) => {
        style.setAttribute("media", "all");
      });
    }
  }, []);
}
