/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Optimize component imports to prevent loading issues
  experimental: {
    optimizePackageImports: ['lucide-react', 'd3'],
  },
  // Prevent aggressive prefetching that can cause route fetch aborts
  productionBrowserSourceMaps: false,
  // Ensure proper build ID generation
  generateBuildId: async () => {
    return process.env.VERCEL_GIT_COMMIT_SHA || `build-${Date.now()}`;
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    // Ensure URL has protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    return [
      {
        source: '/api/:path*',
        destination: `${fullApiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
