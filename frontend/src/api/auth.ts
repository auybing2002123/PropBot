/**
 * 用户认证 API
 */
import api from './index'
import type { UserInfo } from '@/types/api'

/**
 * 用户注册
 * @param username 用户名
 * @param password 密码
 * @param nickname 昵称（可选）
 */
export async function register(
    username: string,
    password: string,
    nickname?: string
): Promise<UserInfo> {
    return api.post('/auth/register', { username, password, nickname })
}

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 */
export async function login(username: string, password: string): Promise<UserInfo> {
    return api.post('/auth/login', { username, password })
}

/**
 * 获取当前用户信息
 * @param userId 用户 ID
 */
export async function getCurrentUser(userId: string): Promise<UserInfo> {
    return api.get('/auth/me', { params: { user_id: userId } })
}
