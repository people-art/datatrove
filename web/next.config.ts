import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  // Configure experimental features if needed
  experimental: {
    // Enable standalone mode optimizations
  },
};

export default nextConfig;
