import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/app/',
  build: {
    outDir: 'build',
    assetsDir: 'static'
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
})
