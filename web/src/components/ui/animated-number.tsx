"use client";

import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";
import { cn } from "@/lib/utils";

interface AnimatedNumberProps {
  value: number;
  className?: string;
  duration?: number;
  format?: (value: number) => string;
}

export function AnimatedNumber({
  value,
  className,
  duration = 0.5,
  format = (val) => val.toString()
}: AnimatedNumberProps) {
  const motionValue = useMotionValue(0);
  const rounded = useTransform(motionValue, (latest) => format(Math.round(latest)));

  useEffect(() => {
    const controls = animate(motionValue, value, {
      duration,
      ease: "easeOut"
    });

    return controls.stop;
  }, [value, duration, motionValue]);

  return (
    <motion.span className={cn(className)}>
      {rounded}
    </motion.span>
  );
}

// For currency values
export function AnimatedPrice({
  value,
  currency = "USD",
  className,
  duration = 0.5
}: Omit<AnimatedNumberProps, 'format'> & { currency?: string }) {
  return (
    <AnimatedNumber
      value={value}
      className={className}
      duration={duration}
      format={(val) => `$${val.toFixed(2)}`}
    />
  );
}

// For percentages
export function AnimatedPercentage({
  value,
  className,
  duration = 0.5,
  decimals = 1
}: Omit<AnimatedNumberProps, 'format'> & { decimals?: number }) {
  return (
    <AnimatedNumber
      value={value}
      className={className}
      duration={duration}
      format={(val) => `${val.toFixed(decimals)}%`}
    />
  );
}
