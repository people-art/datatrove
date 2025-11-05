"use client";

import { Variants } from "framer-motion";

// Common animation variants
export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 8 }
};

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};

export const slideInLeft: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 }
};

export const slideInRight: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 }
};

export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 }
};

// Hover animations
export const hoverLift = {
  scale: 1.01,
  y: -2,
  transition: {
    duration: 0.2,
    ease: "easeOut"
  }
};

export const tapShrink = {
  scale: 0.98,
  transition: {
    duration: 0.1
  }
};

// Loading animations
export const pulse = {
  scale: [1, 1.05, 1],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: "easeInOut"
  }
};

export const shimmer = {
  backgroundPosition: ["-200% 0", "200% 0"],
  transition: {
    duration: 1.5,
    repeat: Infinity,
    ease: "linear"
  }
};

// Page transitions
export const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: {
    duration: 0.3,
    ease: "easeInOut"
  }
};

// Card hover effects
export const cardHover = {
  hover: {
    y: -4,
    boxShadow: "0 12px 32px rgba(0,0,0,0.12)",
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  }
};

// Button animations
export const buttonHover = {
  hover: {
    y: -1,
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  },
  tap: {
    scale: 0.98,
    transition: {
      duration: 0.1
    }
  }
};

// Input focus animations
export const inputFocus = {
  focus: {
    scale: 1.01,
    borderColor: "hsl(var(--primary))",
    boxShadow: "0 0 0 2px hsl(var(--primary) / 0.2)",
    transition: {
      duration: 0.2
    }
  }
};

// Number counter animation
export const counterAnimation = {
  initial: { scale: 0.8, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  exit: { scale: 0.8, opacity: 0 },
  transition: {
    duration: 0.3,
    ease: "easeOut"
  }
};

// Skeleton loading
export const skeletonPulse = {
  animate: {
    backgroundColor: [
      "hsl(var(--muted))",
      "hsl(var(--muted) / 0.5)",
      "hsl(var(--muted))"
    ]
  },
  transition: {
    duration: 1.5,
    repeat: Infinity,
    ease: "easeInOut"
  }
};

// Toast animations
export const toastSlideIn = {
  initial: { opacity: 0, x: 300, scale: 0.3 },
  animate: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: 300, scale: 0.3, transition: { duration: 0.2 } }
};

// Modal animations
export const modalBackdrop = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};

export const modalContent = {
  initial: { opacity: 0, scale: 0.95, y: 20 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.95, y: 20 },
  transition: {
    duration: 0.2,
    ease: "easeOut"
  }
};

// List item animations
export const listItem = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.2 }
};

// Icon animations
export const iconSpin = {
  animate: { rotate: 360 },
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: "linear"
  }
};

export const iconBounce = {
  animate: {
    y: [0, -4, 0],
  },
  transition: {
    duration: 1,
    repeat: Infinity,
    ease: "easeInOut"
  }
};

// Progress animations
export const progressFill = {
  initial: { width: 0 },
  animate: { width: "100%" },
  transition: { duration: 0.5, ease: "easeOut" }
};

// Tab animations
export const tabIndicator = {
  initial: { width: 0, x: 0 },
  animate: { width: "100%", x: 0 },
  exit: { width: 0 },
  transition: { duration: 0.2 }
};
