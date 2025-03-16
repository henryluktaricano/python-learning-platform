/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    // These experimental features help with CSS loading
    optimizeCss: true,
    // Ensures CSS is processed properly
    forceSwcTransforms: true,
  },
}

module.exports = nextConfig 