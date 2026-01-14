/**
 * 收藏 API
 */
import api from './index'

export interface Favorite {
    id: string
    user_id: string
    message_id?: string
    conversation_id?: string
    question: string
    answer: string
    created_at: string
}

export interface FavoriteListResponse {
    items: Favorite[]
    total: number
    page: number
    page_size: number
}

/**
 * 添加收藏
 */
export function addFavorite(data: {
    user_id: string
    message_id?: string
    conversation_id?: string
    question: string
    answer: string
}) {
    return api.post<Favorite>('/favorites', data)
}

/**
 * 获取收藏列表
 */
export function getFavorites(userId: string, page = 1, pageSize = 20) {
    return api.get<FavoriteListResponse>('/favorites', {
        params: { user_id: userId, page, page_size: pageSize }
    })
}

/**
 * 删除收藏
 */
export function deleteFavorite(favoriteId: string, userId: string) {
    return api.delete(`/favorites/${favoriteId}`, {
        params: { user_id: userId }
    })
}
