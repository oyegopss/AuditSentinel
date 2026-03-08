/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      { source: "/", destination: "/dashboard", permanent: false },
      { source: "/AuditSentinel", destination: "/dashboard", permanent: false },
      { source: "/Analytics", destination: "/analytics", permanent: false },
      { source: "/risk-analytics", destination: "/analytics", permanent: false },
    ];
  },
};

export default nextConfig;

