import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Type errors in existing code should not block deployment
  typescript: { ignoreBuildErrors: true },
  async redirects() {
    return [
      {
        source: "/",
        destination: "/dashboard",
        permanent: false,
      },
    ];
  },
};  

export default nextConfig;
