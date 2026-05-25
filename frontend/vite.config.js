import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// When the default API port is taken (e.g. a stale root-owned process), run:
//   FASHION_API_ORIGIN=http://127.0.0.1:8001 npm run dev -- --port 5175
const apiOrigin = process.env.FASHION_API_ORIGIN || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiOrigin,
        changeOrigin: true,
        timeout: 600_000, // long-running /api/tryon (replicate / HF Space)
      },
    },
  },
});
