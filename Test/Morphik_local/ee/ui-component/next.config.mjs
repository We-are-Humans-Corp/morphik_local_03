/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/query',
        destination: `${apiUrl}/query`,
      },
      {
        source: '/api/v1/:path*',
        destination: `${apiUrl}/api/v1/:path*`,
      },
      {
        source: '/auth/:path*',
        destination: `${apiUrl}/auth/:path*`,
      },
      {
        source: '/folders/:path*',
        destination: `${apiUrl}/folders/:path*`,
      },
      {
        source: '/documents/:path*',
        destination: `${apiUrl}/documents/:path*`,
      },
      {
        source: '/chats/:path*',
        destination: `${apiUrl}/chats/:path*`,
      },
      {
        source: '/chat/:path*',
        destination: `${apiUrl}/chat/:path*`,
      },
      {
        source: '/models',
        destination: `${apiUrl}/models`,
      },
      {
        source: '/batch/:path*',
        destination: `${apiUrl}/batch/:path*`,
      },
    ]
  },
};

export default nextConfig;
