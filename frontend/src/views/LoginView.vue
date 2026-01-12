<script setup lang="ts">
/**
 * 登录/注册页面
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 当前模式：login 或 register
const mode = ref<'login' | 'register'>('login')

// 表单数据
const form = reactive({
    username: '',
    password: '',
    confirmPassword: '',
    nickname: ''
})

// 加载状态
const loading = ref(false)

// 切换模式
function switchMode() {
    mode.value = mode.value === 'login' ? 'register' : 'login'
    // 清空表单
    form.username = ''
    form.password = ''
    form.confirmPassword = ''
    form.nickname = ''
}

// 登录
async function handleLogin() {
    if (!form.username.trim()) {
        ElMessage.warning('请输入用户名')
        return
    }
    if (!form.password) {
        ElMessage.warning('请输入密码')
        return
    }

    loading.value = true
    try {
        await authStore.loginUser(form.username.trim(), form.password)
        ElMessage.success('登录成功')
        router.replace('/chat')
    } catch (error: any) {
        const message = error?.response?.data?.detail?.message || '登录失败'
        ElMessage.error(message)
    } finally {
        loading.value = false
    }
}

// 注册
async function handleRegister() {
    if (!form.username.trim()) {
        ElMessage.warning('请输入用户名')
        return
    }
    if (form.username.trim().length < 3) {
        ElMessage.warning('用户名至少3个字符')
        return
    }
    if (!form.password) {
        ElMessage.warning('请输入密码')
        return
    }
    if (form.password.length < 6) {
        ElMessage.warning('密码至少6个字符')
        return
    }
    if (form.password !== form.confirmPassword) {
        ElMessage.warning('两次密码输入不一致')
        return
    }

    loading.value = true
    try {
        await authStore.registerUser(
            form.username.trim(),
            form.password,
            form.nickname.trim() || undefined
        )
        ElMessage.success('注册成功')
        router.replace('/chat')
    } catch (error: any) {
        const message = error?.response?.data?.detail?.message || '注册失败'
        ElMessage.error(message)
    } finally {
        loading.value = false
    }
}

// 提交表单
function handleSubmit() {
    if (mode.value === 'login') {
        handleLogin()
    } else {
        handleRegister()
    }
}
</script>

<template>
    <div class="login-page">
        <div class="login-container">
            <!-- Logo 区域 -->
            <div class="login-header">
                <h1 class="title">购房决策智能助手</h1>
                <p class="subtitle">智能分析，助您做出明智的购房决策</p>
            </div>

            <!-- 登录/注册表单 -->
            <div class="login-form">
                <div class="form-tabs">
                    <div 
                        class="tab" 
                        :class="{ active: mode === 'login' }"
                        @click="mode = 'login'"
                    >
                        登录
                    </div>
                    <div 
                        class="tab" 
                        :class="{ active: mode === 'register' }"
                        @click="mode = 'register'"
                    >
                        注册
                    </div>
                </div>

                <div class="form-content">
                    <!-- 用户名 -->
                    <div class="form-item">
                        <el-input
                            v-model="form.username"
                            placeholder="请输入用户名"
                            size="large"
                            :prefix-icon="User"
                            maxlength="20"
                            @keyup.enter="handleSubmit"
                        />
                    </div>

                    <!-- 密码 -->
                    <div class="form-item">
                        <el-input
                            v-model="form.password"
                            type="password"
                            placeholder="请输入密码"
                            size="large"
                            :prefix-icon="Lock"
                            show-password
                            maxlength="50"
                            @keyup.enter="handleSubmit"
                        />
                    </div>

                    <!-- 注册模式：确认密码 -->
                    <div v-if="mode === 'register'" class="form-item">
                        <el-input
                            v-model="form.confirmPassword"
                            type="password"
                            placeholder="请确认密码"
                            size="large"
                            :prefix-icon="Lock"
                            show-password
                            maxlength="50"
                            @keyup.enter="handleSubmit"
                        />
                    </div>

                    <!-- 注册模式：昵称 -->
                    <div v-if="mode === 'register'" class="form-item">
                        <el-input
                            v-model="form.nickname"
                            placeholder="昵称（选填）"
                            size="large"
                            :prefix-icon="User"
                            maxlength="50"
                            @keyup.enter="handleSubmit"
                        />
                    </div>

                    <!-- 提交按钮 -->
                    <div class="form-item">
                        <el-button
                            type="primary"
                            size="large"
                            :loading="loading"
                            class="submit-btn"
                            @click="handleSubmit"
                        >
                            {{ mode === 'login' ? '登录' : '注册' }}
                        </el-button>
                    </div>

                    <!-- 切换提示 -->
                    <div class="switch-tip">
                        <span v-if="mode === 'login'">
                            还没有账号？
                            <a @click="switchMode">立即注册</a>
                        </span>
                        <span v-else>
                            已有账号？
                            <a @click="switchMode">立即登录</a>
                        </span>
                    </div>
                </div>
            </div>

            <!-- 底部信息 -->
            <div class="login-footer">
                <p>购房决策智能助手 - 比赛演示项目</p>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f7fa;
    padding: 20px;
}

.login-container {
    width: 100%;
    max-width: 400px;
}

.login-header {
    text-align: center;
    margin-bottom: 32px;

    .title {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
    }

    .subtitle {
        font-size: 14px;
        color: #909399;
    }
}

.login-form {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    overflow: hidden;

    .form-tabs {
        display: flex;
        border-bottom: 1px solid #ebeef5;

        .tab {
            flex: 1;
            padding: 16px;
            text-align: center;
            font-size: 15px;
            color: #909399;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;

            &.active {
                color: #1890ff;
                font-weight: 500;

                &::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 32px;
                    height: 2px;
                    background: #1890ff;
                }
            }

            &:hover:not(.active) {
                color: #606266;
            }
        }
    }

    .form-content {
        padding: 24px;

        .form-item {
            margin-bottom: 16px;

            &:last-child {
                margin-bottom: 0;
            }
        }

        .submit-btn {
            width: 100%;
        }

        .switch-tip {
            text-align: center;
            margin-top: 16px;
            font-size: 14px;
            color: #909399;

            a {
                color: #1890ff;
                cursor: pointer;

                &:hover {
                    text-decoration: underline;
                }
            }
        }
    }
}

.login-footer {
    text-align: center;
    margin-top: 24px;
    color: #c0c4cc;
    font-size: 12px;
}
</style>
