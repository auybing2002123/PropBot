<script setup lang="ts">
/**
 * 我的页面
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  Setting, 
  QuestionFilled,
  Warning,
  ArrowRight,
  Location
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useCityStore, SUPPORTED_CITIES, type CityCode } from '@/stores/city'

const router = useRouter()
const authStore = useAuthStore()
const cityStore = useCityStore()

// 城市选择弹窗
const showCityDialog = ref(false)

// 城市列表
const cities = SUPPORTED_CITIES

// 选择城市
function selectCity(cityId: CityCode) {
  cityStore.setCity(cityId)
  showCityDialog.value = false
  ElMessage.success(`已切换到${cityStore.getCityName()}`)
}

// 退出登录
function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.clearAuth()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}
</script>

<template>
  <div class="profile-view">
    <div class="profile-container">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="avatar">
          <el-icon :size="48">
            <User />
          </el-icon>
        </div>
        <div class="user-info">
          <div class="nickname">{{ authStore.nickname || authStore.username || '用户' }}</div>
          <div class="meta">@{{ authStore.username }}</div>
        </div>
      </div>
      
      <!-- 功能列表 -->
      <div class="menu-list">
        <!-- 城市选择 -->
        <div class="menu-item" @click="showCityDialog = true">
          <div class="menu-left">
            <el-icon><Location /></el-icon>
            <span>当前城市</span>
          </div>
          <div class="menu-right">
            <span class="current-value">{{ cityStore.getCityName() }}</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        
        <div class="menu-item disabled">
          <div class="menu-left">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </div>
          <div class="menu-right">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        
        <div class="menu-item disabled">
          <div class="menu-left">
            <el-icon><QuestionFilled /></el-icon>
            <span>帮助与反馈</span>
          </div>
          <div class="menu-right">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
      
      <!-- 退出登录 -->
      <div class="logout-section">
        <el-button type="danger" plain @click="handleLogout">
          退出登录
        </el-button>
      </div>
      
      <!-- 免责声明 -->
      <div class="disclaimer">
        <el-icon><Warning /></el-icon>
        <span>免责声明：本工具仅供参考，不构成投资建议</span>
      </div>
    </div>
    
    <!-- 城市选择弹窗 -->
    <el-dialog
      v-model="showCityDialog"
      title="选择城市"
      width="90%"
      style="max-width: 400px"
    >
      <div class="city-list">
        <div
          v-for="city in cities"
          :key="city.value"
          class="city-item"
          :class="{ active: city.value === cityStore.currentCity }"
          @click="selectCity(city.value)"
        >
          <el-icon><Location /></el-icon>
          <span>{{ city.label }}</span>
          <el-icon v-if="city.value === cityStore.currentCity" class="check-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          </el-icon>
        </div>
      </div>
    </el-dialog>
  </div>
</template>


<style scoped lang="scss">
.profile-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7fa;
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
}

.user-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
  
  .avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: #f0f5ff;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1890ff;
  }
  
  .user-info {
    .nickname {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin-bottom: 4px;
    }
    
    .meta {
      font-size: 13px;
      color: #999;
    }
  }
}

.menu-list {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  margin-bottom: 16px;
  
  .menu-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:not(:last-child) {
      border-bottom: 1px solid #f0f0f0;
    }
    
    &:hover:not(.disabled) {
      background: #fafafa;
    }
    
    &.disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }
    
    .menu-left {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .el-icon {
        color: #1890ff;
        font-size: 18px;
      }
      
      span {
        font-size: 14px;
        color: #333;
      }
    }
    
    .menu-right {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .current-value {
        font-size: 14px;
        color: #666;
      }
      
      .el-icon {
        color: #c0c4cc;
        font-size: 14px;
      }
    }
  }
}

.logout-section {
  text-align: center;
  margin-bottom: 24px;
  
  .el-button {
    min-width: 120px;
  }
}

.disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #999;
  font-size: 12px;
  
  .el-icon {
    color: #faad14;
  }
}

.city-list {
  .city-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background: #f5f7fa;
    }
    
    &.active {
      background: #e6f7ff;
      color: #1890ff;
      
      .el-icon {
        color: #1890ff;
      }
    }
    
    .el-icon {
      color: #999;
    }
    
    span {
      flex: 1;
      font-size: 14px;
    }
    
    .check-icon {
      color: #1890ff;
    }
  }
}
</style>
