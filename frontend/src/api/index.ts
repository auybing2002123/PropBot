/**
 * API 请求封装
 * 统一配置 axios 实例和拦截器
 */
import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/api'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 可以在这里添加 token 等认证信息
        const userId = localStorage.getItem('user_id')
        if (userId && config.headers) {
            config.headers['X-User-Id'] = userId
        }
        return config
    },
    (error) => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
api.interceptors.response.use(
    (response: AxiosResponse<ApiResponse>) => {
        const { code, message, data } = response.data

        // code 为 0 表示成功
        if (code === 0) {
            return data as any
        }

        // 业务错误
        ElMessage.error(message || '请求失败')
        return Promise.reject(new Error(message || '请求失败'))
    },
    (error) => {
        // 网络错误或服务器错误
        if (error.code === 'ECONNABORTED') {
            ElMessage.error('请求超时，请稍后重试')
        } else if (!error.response) {
            ElMessage.error('网络异常，请检查网络连接')
        } else {
            const status = error.response.status
            const message = error.response.data?.message

            switch (status) {
                case 400:
                    ElMessage.error(message || '请求参数错误')
                    break
                case 401:
                    ElMessage.error('请先登录')
                    // 可以在这里跳转到登录页
                    break
                case 403:
                    ElMessage.error('没有权限访问')
                    break
                case 404:
                    ElMessage.error(message || '请求的资源不存在')
                    break
                case 500:
                    ElMessage.error('服务器错误，请稍后重试')
                    break
                default:
                    ElMessage.error(message || '请求失败')
            }
        }

        return Promise.reject(error)
    }
)

export default api
