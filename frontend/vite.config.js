import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/



export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    emptyOutDir: true
  },
  // Add this for proper routing in production
  base: './',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})