import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/app/',
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  build: {
    outDir: 'build',
    assetsDir: 'static'
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
})
