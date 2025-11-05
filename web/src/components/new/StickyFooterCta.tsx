"use client";

import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

interface StickyFooterCtaProps {
  disabled?: boolean;
  onClick: () => void;
  label: string;
  isVisible?: boolean;
}

export function StickyFooterCta({
  disabled,
  onClick,
  label,
  isVisible = true
}: StickyFooterCtaProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-x-0 bottom-0 z-40"
        >
          <div className="mx-auto w-full max-w-[1080px] px-4 pb-5">
            <div className="rounded-2xl border border-line bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60 p-4 shadow-[0_8px_24px_rgba(0,0,0,0.12)]">
              <div className="flex items-center justify-between gap-4">
                <div className="text-sm text-foreground/70">
                  We&apos;ll run a local 1M-page benchmark. No charge yet.
                </div>
                <Button
                  size="lg"
                  disabled={disabled}
                  onClick={onClick}
                  className="min-w-[180px]"
                >
                  {label}
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
