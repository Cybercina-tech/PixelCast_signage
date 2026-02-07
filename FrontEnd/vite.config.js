import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'child_process'

// Get Git info at build time
function getGitVersion() {
  try {
    const commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim()
    // Return just the commit hash (e.g., "e994370")
    // Or use format: "v1.0.0-e994370" if you have a version number
    return commitHash
  } catch (error) {
    console.warn('Git info not available, using fallback version')
    return 'dev'
  }
}

const gitVersion = getGitVersion()

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    hmr: {
      clientPort: 5173,
      path: '/vite-hmr',
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://backend:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(gitVersion)
  },
  optimizeDeps: {
    include: ['qrcode']
  }
})
