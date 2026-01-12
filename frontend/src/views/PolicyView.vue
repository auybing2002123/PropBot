<script setup lang="ts">
/**
 * 政策页面
 * 优化布局，与整体风格统一
 */
import { ref, computed } from 'vue'
import { useCityStore } from '@/stores/city'
import PolicyCard from '@/components/common/PolicyCard.vue'

const cityStore = useCityStore()
const activeTab = ref('purchase')

// 模拟政策数据
const policies = computed(() => {
  const cityName = cityStore.getCityName()
  
  return {
    purchase: [
      {
        id: '1',
        title: `${cityName}市住房限购政策（2024年最新）`,
        summary: [
          '2024年9月起，全面取消住房限购',
          '本地户籍和外地户籍均不限购套数',
          '首套房首付最低15%',
          '二套房首付最低25%'
        ],
        source: `${cityName}市住房和城乡建设局`,
        updateTime: '2024-09-30'
      }
    ],
    provident: [
      {
        id: '2',
        title: `${cityName}市公积金贷款政策`,
        summary: [
          '个人最高贷款额度：60万元',
          '夫妻最高贷款额度：80万元',
          '连续缴存12个月以上可申请',
          '贷款利率：5年以下2.35%，5年以上2.85%'
        ],
        source: `${cityName}住房公积金管理中心`,
        updateTime: '2024-10-01'
      }
    ],
    loan: [
      {
        id: '3',
        title: '商业贷款利率政策（2025年1月）',
        summary: [
          'LPR 5年期以上：3.60%',
          '首套房利率：LPR-20BP，约3.40%',
          '二套房利率：LPR+20BP，约3.80%',
          '支持等额本息和等额本金还款'
        ],
        source: '中国人民银行',
        updateTime: '2025-01-01'
      }
    ],
    process: [
      {
        id: '4',
        title: '二手房购买全流程指南',
        summary: [
          '第一步：资质审核（1-3天）',
          '第二步：看房选房（1-4周）',
          '第三步：签订合同、支付定金',
          '第四步：贷款申请（2-4周）',
          '第五步：过户缴税（1-2周）',
          '第六步：交房入住'
        ],
        source: '购房指南',
        updateTime: '2024-12-01'
      }
    ]
  }
})

// 当前 tab 的政策列表
const currentPolicies = computed(() => {
  return policies.value[activeTab.value as keyof typeof policies.value] || []
})
</script>

<template>
  <div class="policy-view">
    <div class="policy-container">
      <el-tabs v-model="activeTab" class="policy-tabs">
        <el-tab-pane label="限购政策" name="purchase" />
        <el-tab-pane label="公积金" name="provident" />
        <el-tab-pane label="贷款政策" name="loan" />
        <el-tab-pane label="购房流程" name="process" />
      </el-tabs>
      
      <div class="policy-list">
        <PolicyCard
          v-for="policy in currentPolicies"
          :key="policy.id"
          :title="policy.title"
          :summary="policy.summary"
          :source="policy.source"
          :update-time="policy.updateTime"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.policy-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7fa;
}

.policy-container {
  max-width: 700px;
  margin: 0 auto;
}

.policy-tabs {
  background: #fff;
  border-radius: 12px 12px 0 0;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

  :deep(.el-tabs__header) {
    margin: 0;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background: #e5e7eb;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    color: #666;
    height: 48px;
    line-height: 48px;
    
    &.is-active {
      color: #1890ff;
      font-weight: 500;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: #1890ff;
  }

  :deep(.el-tabs__content) {
    display: none;
  }
}

.policy-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}
</style>
