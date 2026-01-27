import type { NextConfig } from "next";
import { config } from 'dotenv';
import { resolve } from 'path';

// Load .env from parent folder (project root)
config({ path: resolve(__dirname, '../.env') });

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',

  // Enable experimental optimizations for faster builds
  experimental: {
    optimizePackageImports: [
      '@copilotkit/react-core',
      '@copilotkit/react-ui',
      '@copilotkit/runtime',
      '@radix-ui/react-icons',
      '@radix-ui/react-dialog',
      '@radix-ui/react-scroll-area',
      '@radix-ui/react-toast',
      'lucide-react',
      'framer-motion',
      'reactflow',
    ],
    // Turbo mode optimizations
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },

  // Optimize webpack for faster builds
  webpack: (config, { isServer }) => {
    // Reduce bundle size for client
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        crypto: false,
      };
    }

    // Optimize module resolution
    config.resolve.alias = {
      ...config.resolve.alias,
    };

    return config;
  },

  env: {
    HYPERBROWSER_API_KEY: process.env.HYPERBROWSER_API_KEY,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    OPENAI_SUMMARY_MODEL: process.env.OPENAI_SUMMARY_MODEL,
    VEO3_API_KEY: process.env.VEO3_API_KEY,
    ELEVENLABS_API_KEY: process.env.ELEVENLABS_API_KEY,
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
    GEMINI_MODEL: process.env.GEMINI_MODEL,
    VEO_MODEL: process.env.VEO_MODEL,
  },
};

export default nextConfig;
