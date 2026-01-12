import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        // Element Plus 按需导入
        AutoImport({
            resolvers: [ElementPlusResolver()],
            imports: ['vue', 'vue-router', 'pinia'],
            dts: 'src/auto-imports.d.ts'
        }),
        Components({
            resolvers: [ElementPlusResolver()],
            dts: 'src/components.d.ts'
        })
    ],
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src')
        }
    },
    server: {
        port: 5173,
        host: '0.0.0.0',  // 允许外部访问
        // 允许 cpolar 穿透域名访问
        allowedHosts: [
            '.cpolar.top',
            '.cpolar.cn',
            '.r37.cpolar.top'
        ],
        proxy: {
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true
            }
        }
    }
});
