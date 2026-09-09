import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://10.180.24.176:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://10.180.24.176:8000',
        changeOrigin: true,
      },
    },
  },
})
