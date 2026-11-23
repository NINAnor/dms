import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import wasm from 'vite-plugin-wasm';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [wasm(), react()],
  optimizeDeps: {
    exclude: ['parquet-wasm'],
  },
  // NOTE: same as STATIC_URL
  base: '/static/frontend/',
  build: {
    manifest: 'manifest.json',
    sourcemap: true,
    // NOTE: django app static folder
    outDir: resolve(__dirname, 'static/frontend'),
    rollupOptions: {
      input: {
        relationships: resolve(__dirname, 'src/relationships/main.tsx'),
        upload: resolve(__dirname, 'src/upload/main.tsx'),
        preview: resolve(__dirname, 'src/preview/main.tsx'),
      },
    },
  },
});
