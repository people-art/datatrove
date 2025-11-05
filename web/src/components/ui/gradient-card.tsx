import { cn } from "@/lib/utils";

interface GradientCardProps {
  children: React.ReactNode;
  className?: string;
  glowOnHover?: boolean;
}

export function GradientCard({
  children,
  className,
  glowOnHover = true
}: GradientCardProps) {
  return (
    <div
      className={cn(
        "relative rounded-2xl p-px bg-gradient-to-b from-white/20 via-white/6 to-transparent",
        glowOnHover && "transition-all duration-300 hover:shadow-[0_0_32px_rgba(45,91,255,0.15)]",
        className
      )}
    >
      <div className="rounded-2xl bg-card p-6 md:p-8 border border-white/5">
        {children}
      </div>
    </div>
  );
}
