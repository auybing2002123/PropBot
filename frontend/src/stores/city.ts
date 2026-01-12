/**
 * 城市选择状态管理
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// localStorage 键名
const CITY_KEY = 'selected_city'

// 支持的城市列表
export const SUPPORTED_CITIES = [
    { value: 'nanning', label: '南宁' },
    { value: 'liuzhou', label: '柳州' }
] as const

export type CityCode = typeof SUPPORTED_CITIES[number]['value']

// 城市区域数据
export const CITY_DISTRICTS: Record<CityCode, string[]> = {
    nanning: ['青秀区', '良庆区', '西乡塘区', '江南区', '兴宁区', '邕宁区', '武鸣区'],
    liuzhou: ['城中区', '鱼峰区', '柳南区', '柳北区', '柳江区']
}

export const useCityStore = defineStore('city', () => {
    // 从 localStorage 读取，默认南宁
    const savedCity = localStorage.getItem(CITY_KEY) as CityCode | null
    const currentCity = ref<CityCode>(savedCity || 'nanning')
    const currentDistrict = ref<string>('')

    // 监听城市变化，保存到 localStorage
    watch(currentCity, (newCity) => {
        localStorage.setItem(CITY_KEY, newCity)
        // 切换城市时重置区域
        currentDistrict.value = ''
    })

    /**
     * 获取当前城市名称
     */
    function getCityName(): string {
        const city = SUPPORTED_CITIES.find(c => c.value === currentCity.value)
        return city?.label || '南宁'
    }

    /**
     * 获取当前城市的区域列表
     */
    function getDistricts(): string[] {
        return CITY_DISTRICTS[currentCity.value] || []
    }

    /**
     * 设置城市
     */
    function setCity(city: CityCode) {
        currentCity.value = city
    }

    /**
     * 设置区域
     */
    function setDistrict(district: string) {
        currentDistrict.value = district
    }

    return {
        // 状态
        currentCity,
        currentDistrict,
        // 方法
        getCityName,
        getDistricts,
        setCity,
        setDistrict
    }
})
