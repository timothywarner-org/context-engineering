import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // Output static files to be served by FastAPI
  output: 'static',
  outDir: '../backend/static/dash',

  // Base path for the dashboard (served at /dash/)
  base: '/dash/',

  // Build configuration
  build: {
    assets: '_assets',
  },

  // Dev server configuration
  server: {
    port: 4321,
  },

  // Vite configuration for development proxy
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  },
});
