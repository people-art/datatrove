"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { cardHover } from "@/lib/animations";

interface GradientCardProps {
  children: React.ReactNode;
  className?: string;
  glowOnHover?: boolean;
  animate?: boolean;
}

export function GradientCard({
  children,
  className,
  glowOnHover = true,
  animate = true
}: GradientCardProps) {
  const CardComponent = animate ? motion.div : "div";

  const motionProps = animate ? {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    whileHover: glowOnHover ? "hover" : undefined,
    variants: cardHover,
    transition: { duration: 0.2 }
  } : {};

  return (
    <CardComponent
      className={cn(
        "relative rounded-2xl p-px bg-gradient-to-b from-white/20 via-white/6 to-transparent",
        glowOnHover && "transition-all duration-300 hover:shadow-[0_0_32px_rgba(45,91,255,0.15)]",
        className
      )}
      {...motionProps}
    >
      <div className="rounded-2xl bg-card p-6 md:p-8 border border-white/5">
        {children}
      </div>
    </CardComponent>
  );
}
