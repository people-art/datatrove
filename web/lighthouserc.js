module.exports = {
  ci: {
    collect: {
      startServerCommand: "npm run start",
      startServerReadyPattern: "ready - started server",
      url: ["http://localhost:3000"],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        // Performance
        "categories:performance": ["error", { minScore: 0.9 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["error", { minScore: 0.95 }],
        "categories:seo": ["error", { minScore: 0.9 }],
        "categories:pwa": "off",

        // Core Web Vitals
        "largest-contentful-paint": ["error", { maxNumericValue: 2500 }],
        "first-contentful-paint": ["error", { maxNumericValue: 1800 }],
        "speed-index": ["error", { maxNumericValue: 3000 }],
        "total-blocking-time": ["error", { maxNumericValue: 300 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],

        // Bundle size
        "total-byte-weight": ["error", { maxNumericValue: 2048000 }], // 2MB
        "mainthread-work-breakdown": ["error", { minScore: 0.9 }],

        // Accessibility
        "aria-allowed-attr": "error",
        "aria-required-attr": "error",
        "aria-required-children": "error",
        "aria-required-parent": "error",
        "aria-roles": "error",
        "aria-valid-attr-value": "error",
        "aria-valid-attr": "error",
        "button-name": "error",
        "color-contrast": "error",
        "document-title": "error",
        "duplicate-id-active": "error",
        "duplicate-id-aria": "error",
        "form-field-multiple-labels": "error",
        "heading-order": "error",
        "html-has-lang": "error",
        "html-lang-valid": "error",
        "image-alt": "error",
        "input-image-alt": "error",
        "label": "error",
        "link-name": "error",
        "list": "error",
        "listitem": "error",
        "meta-viewport": "error",

        // SEO
        "meta-description": "error",
        "http-status-code": "error",
        "font-size": "error",
        "tap-targets": "error",

        // Best Practices
        "doctype": "error",
        "charset": "error",
        "js-libraries": "error",
        "deprecations": "error",
        "errors-in-console": "error",
        "valid-source-maps": "error",
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
