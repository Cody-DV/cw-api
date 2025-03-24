// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    hmr: {
      clientPort: 3000
    }
  },
  build: {
    outDir: 'dist',
    assetsInlineLimit: 0,
    sourcemap: true,
  }
});