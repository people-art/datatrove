"use client";

import Image, { ImageProps } from "next/image";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface OptimizedImageProps extends Omit<ImageProps, 'onLoad' | 'onError'> {
  fallbackSrc?: string;
  showSkeleton?: boolean;
}

export function OptimizedImage({
  src,
  alt,
  className,
  fallbackSrc,
  showSkeleton = true,
  priority = false,
  ...props
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
  };

  if (hasError && fallbackSrc) {
    return (
      <Image
        src={fallbackSrc}
        alt={alt}
        className={className}
        onLoad={handleLoad}
        onError={() => setIsLoading(false)}
        priority={priority}
        {...props}
      />
    );
  }

  return (
    <div className={cn("relative overflow-hidden", className)}>
      {showSkeleton && isLoading && (
        <div className="absolute inset-0 bg-muted animate-pulse" />
      )}
      <Image
        src={src}
        alt={alt}
        className={cn(
          "transition-opacity duration-300",
          isLoading ? "opacity-0" : "opacity-100"
        )}
        onLoad={handleLoad}
        onError={handleError}
        priority={priority}
        {...props}
      />
    </div>
  );
}

// Pre-optimized icons with proper ARIA labels
export function Logo({ className }: { className?: string }) {
  return (
    <OptimizedImage
      src="/next.svg"
      alt="FineData Logo"
      width={32}
      height={32}
      className={className}
      priority
    />
  );
}

export function HeroImage({ className }: { className?: string }) {
  return (
    <OptimizedImage
      src="/globe.svg"
      alt="Global data processing visualization"
      width={400}
      height={300}
      className={className}
      priority
    />
  );
}
