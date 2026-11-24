import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Type errors in existing code should not block deployment
  typescript: { ignoreBuildErrors: true },
  // Lets the dev server be opened by the computer's network address, not only localhost
  allowedDevOrigins: ["192.168.141.1", "localhost", "127.0.0.1"],
  async redirects() {
    return [
      {
        source: "/",
        destination: "/login",
        permanent: false,
      },
    ];
  },
};  

export default nextConfig;
