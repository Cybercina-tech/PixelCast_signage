import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'child_process'
import fs from 'node:fs'

/**
 * Vite proxy must reach Django. Inside Docker, 127.0.0.1:8000 is wrong (backend is another container).
 * Prefer VITE_PROXY_TARGET; else if /.dockerenv exists use service hostname; else local dev on host.
 */
function getBackendProxyTarget() {
  if (process.env.VITE_PROXY_TARGET) {
    return process.env.VITE_PROXY_TARGET
  }
  try {
    if (fs.existsSync('/.dockerenv')) {
      return 'http://backend:8000'
    }
  } catch {
    /* non-blocking */
  }
  return 'http://127.0.0.1:8000'
}

const backendProxyTarget = getBackendProxyTarget()

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
        target: backendProxyTarget,
        changeOrigin: true,
      },
      '/admin': {
        target: backendProxyTarget,
        changeOrigin: true,
      },
      '/media': {
        target: backendProxyTarget,
        changeOrigin: true,
      },
      '/ws': {
        target: backendProxyTarget,
        changeOrigin: true,
        ws: true,
      },
      // Player IoT traffic (template, heartbeat, commands) — same issue as /api when backend
      // is only reachable as backend:8000 inside Docker; browser must use same-origin /iot.
      '/iot': {
        target: backendProxyTarget,
        changeOrigin: true,
      },
      '/public-iot': {
        target: backendProxyTarget,
        changeOrigin: true,
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
