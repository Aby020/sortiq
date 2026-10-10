import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true, rewrite: (p) => p },
      '/service': { target: 'http://127.0.0.1:8100', changeOrigin: true, rewrite: (p) => p },
    },
  },
});
