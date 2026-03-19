import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 💡 配置绝对路径别名，告诉 Vite：'@' 就等于 'src' 目录！
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})