/** @type {import('next').NextConfig} */
const nextConfig = {
  // The public site is read-only against the FastAPI service (ADR-0004). The API
  // base URL is injected from the environment; it must be reachable server-side.
  env: {
    API_BASE_URL: process.env.API_BASE_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
