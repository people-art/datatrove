"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { skeletonPulse } from "@/lib/animations";

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function Skeleton({ className, animate = true }: SkeletonProps) {
  const Component = animate ? motion.div : "div";

  const motionProps = animate ? {
    variants: skeletonPulse,
    animate: "animate"
  } : {};

  return (
    <Component
      className={cn("bg-muted rounded-md", className)}
      {...motionProps}
    />
  );
}

// Predefined skeleton components
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  );
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn(
            "h-4",
            i === lines - 1 ? "w-3/4" : "w-full" // Last line shorter
          )}
        />
      ))}
    </div>
  );
}

export function SkeletonAvatar({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12"
  };

  return <Skeleton className={cn("rounded-full", sizeClasses[size])} />;
}

export function SkeletonButton({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClasses = {
    sm: "h-8 w-20",
    md: "h-10 w-24",
    lg: "h-11 w-32"
  };

  return <Skeleton className={cn("rounded-md", sizeClasses[size])} />;
}
