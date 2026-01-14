<script setup lang="ts">
/**
 * 帮助中心页面
 * 用户使用手册，包含功能介绍和使用指南
 */
import { ref } from 'vue'
import { 
  ChatLineSquare, 
  Coin, 
  DataAnalysis, 
  Document,
  Star,
  QuestionFilled,
  Right
} from '@element-plus/icons-vue'

// 当前选中的菜单
const activeMenu = ref('quick-start')

// 菜单列表
const menuList = [
  { id: 'quick-start', name: '快速开始', icon: Right },
  { id: 'chat', name: '智能对话', icon: ChatLineSquare },
  { id: 'calculator', name: '购房计算器', icon: Coin },
  { id: 'market', name: '市场分析', icon: DataAnalysis },
  { id: 'policy', name: '政策查询', icon: Document },
  { id: 'favorite', name: '关注功能', icon: Star },
  { id: 'faq', name: '常见问题', icon: QuestionFilled },
]
</script>

<template>
  <div class="help-view">
    <!-- 左侧内容 -->
    <div class="help-content">
      <!-- 快速开始 -->
      <div v-show="activeMenu === 'quick-start'" class="content-section">
        <h1>快速开始</h1>
        <p class="intro">欢迎使用购房决策智能助手！本系统基于多智能体协作技术，为您提供专业的购房咨询服务。</p>
        
        <h2>系统特点</h2>
        <ul>
          <li>多专家协作：财务顾问、政策专家、市场分析师、购房顾问四大角色协同工作</li>
          <li>智能问答：自然语言交互，理解您的购房需求</li>
          <li>精准计算：贷款、税费、总成本一键计算</li>
          <li>数据分析：实时市场行情，辅助决策</li>
        </ul>
        
        <h2>支持城市</h2>
        <p>目前支持广西南宁、柳州两个城市的购房咨询服务。</p>
        
        <h2>开始使用</h2>
        <ol>
          <li>在智能对话页面输入您的问题，如"我想在南宁买房，预算150万"</li>
          <li>系统会自动分析您的需求，调用相关专家进行解答</li>
          <li>您也可以使用快捷工具（计算器、市场分析、政策查询）获取特定信息</li>
        </ol>
      </div>
      
      <!-- 智能对话 -->
      <div v-show="activeMenu === 'chat'" class="content-section">
        <h1>智能对话</h1>
        <p class="intro">智能对话是系统的核心功能，您可以用自然语言提问，系统会智能调度多个专家角色为您解答。</p>
        
        <h2>如何提问</h2>
        <p>在输入框中输入您的问题，按回车或点击发送按钮即可。支持以下类型的问题：</p>
        <ul>
          <li>购房资格咨询：如"外地人在南宁能买几套房？"</li>
          <li>贷款计算：如"100万的房子，首付30%，月供多少？"</li>
          <li>政策解读：如"南宁最新的公积金政策是什么？"</li>
          <li>市场分析：如"青秀区和良庆区哪个更值得投资？"</li>
          <li>综合咨询：如"我月收入1.5万，想在南宁买房，有什么建议？"</li>
        </ul>
        
        <h2>专家角色</h2>
        <p>系统内置四大专家角色，会根据您的问题自动调度：</p>
        <ul>
          <li>财务顾问：负责贷款计算、税费分析、还款压力评估</li>
          <li>政策专家：负责限购限贷政策、公积金政策解读</li>
          <li>市场分析师：负责房价走势、区域对比、购房时机判断</li>
          <li>购房顾问：负责综合建议、风险提示、行动指南</li>
        </ul>
        
        <h2>对话管理</h2>
        <ul>
          <li>新建对话：点击左侧"新建对话"按钮开始新的咨询</li>
          <li>历史记录：左侧显示历史对话列表，点击可查看</li>
          <li>删除对话：鼠标悬停在对话上，点击删除图标</li>
        </ul>
      </div>
      
      <!-- 购房计算器 -->
      <div v-show="activeMenu === 'calculator'" class="content-section">
        <h1>购房计算器</h1>
        <p class="intro">提供专业的购房费用计算工具，帮助您精确规划购房预算。</p>
        
        <h2>贷款计算</h2>
        <p>支持三种贷款方式：</p>
        <ul>
          <li>商业贷款：利率较高，额度灵活</li>
          <li>公积金贷款：利率低，但有额度限制</li>
          <li>组合贷款：公积金+商贷组合，兼顾利率和额度</li>
        </ul>
        <p>支持两种还款方式：</p>
        <ul>
          <li>等额本息：每月还款金额固定，前期利息多</li>
          <li>等额本金：每月还款递减，总利息较少</li>
        </ul>
        
        <h2>税费计算</h2>
        <p>自动计算购房相关税费：</p>
        <ul>
          <li>契税：根据面积和首套/二套计算</li>
          <li>增值税：二手房满2年免征</li>
          <li>个人所得税：二手房交易需缴纳</li>
          <li>中介费：按成交价比例计算</li>
        </ul>
        
        <h2>总成本计算</h2>
        <p>汇总所有购房费用，包括：</p>
        <ul>
          <li>首付款</li>
          <li>贷款总利息</li>
          <li>各项税费</li>
          <li>装修费用（可选）</li>
          <li>其他费用（可选）</li>
        </ul>
      </div>
      
      <!-- 市场分析 -->
      <div v-show="activeMenu === 'market'" class="content-section">
        <h1>市场分析</h1>
        <p class="intro">提供南宁、柳州两市的房地产市场数据分析，帮助您了解市场行情。</p>
        
        <h2>数据概览</h2>
        <p>展示当前城市的核心指标：</p>
        <ul>
          <li>均价：当前城市二手房均价</li>
          <li>环比：与上月相比的涨跌幅</li>
          <li>成交量：近期成交套数</li>
          <li>库存：在售房源数量</li>
        </ul>
        
        <h2>价格走势</h2>
        <p>展示近12个月的房价走势图，帮助您判断市场趋势。</p>
        
        <h2>区域对比</h2>
        <p>各区域房价对比表，包含：</p>
        <ul>
          <li>区域均价</li>
          <li>环比变化</li>
          <li>成交量</li>
          <li>热度评级</li>
        </ul>
      </div>
      
      <!-- 政策查询 -->
      <div v-show="activeMenu === 'policy'" class="content-section">
        <h1>政策查询</h1>
        <p class="intro">汇总南宁、柳州两市的购房相关政策，方便快速查阅。</p>
        
        <h2>政策分类</h2>
        <ul>
          <li>限购政策：购房资格、限购套数</li>
          <li>贷款政策：首付比例、贷款利率</li>
          <li>公积金政策：提取条件、贷款额度</li>
          <li>税费政策：契税、增值税优惠</li>
        </ul>
        
        <h2>使用方法</h2>
        <ol>
          <li>选择城市（南宁/柳州）</li>
          <li>选择政策类型</li>
          <li>查看政策详情</li>
        </ol>
      </div>
      
      <!-- 关注功能 -->
      <div v-show="activeMenu === 'favorite'" class="content-section">
        <h1>关注功能</h1>
        <p class="intro">在对话过程中，您可以关注感兴趣的问答，方便后续查阅。</p>
        
        <h2>如何关注</h2>
        <ol>
          <li>在对话中找到您感兴趣的AI回复</li>
          <li>鼠标悬停在回复上，点击右上角的星星图标</li>
          <li>系统会自动保存该问答对</li>
        </ol>
        
        <h2>查看关注</h2>
        <ol>
          <li>点击页面右下角的星星悬浮按钮</li>
          <li>展开关注面板，查看所有关注的问答</li>
          <li>点击问答可展开查看完整内容</li>
          <li>点击跳转图标可回到原对话</li>
        </ol>
        
        <h2>取消关注</h2>
        <ul>
          <li>在关注面板中，点击删除图标</li>
          <li>或在对话中再次点击星星图标</li>
        </ul>
      </div>
      
      <!-- 常见问题 -->
      <div v-show="activeMenu === 'faq'" class="content-section">
        <h1>常见问题</h1>
        
        <h2>Q: 系统的数据准确吗？</h2>
        <p>A: 本系统使用模拟数据进行演示，政策信息仅供参考。实际购房请以官方发布的最新政策为准。</p>
        
        <h2>Q: 支持哪些城市？</h2>
        <p>A: 目前支持广西南宁、柳州两个城市。后续会逐步扩展到更多城市。</p>
        
        <h2>Q: 计算结果可以作为购房依据吗？</h2>
        <p>A: 计算器提供的结果仅供参考，实际贷款利率、税费等以银行和税务部门的最终核定为准。</p>
        
        <h2>Q: 如何切换城市？</h2>
        <p>A: 点击页面顶部的城市选择器，可以在南宁和柳州之间切换。</p>
        
        <h2>Q: 对话记录会保存吗？</h2>
        <p>A: 是的，您的对话记录会自动保存，下次登录可以继续查看。</p>
        
        <h2>Q: 如何联系客服？</h2>
        <p>A: 本系统为比赛演示项目，暂不提供客服支持。如有问题，请通过智能对话功能咨询。</p>
      </div>
    </div>
    
    <!-- 右侧导航 -->
    <div class="help-sidebar">
      <div class="sidebar-title">帮助中心</div>
      <div class="menu-list">
        <div 
          v-for="item in menuList"
          :key="item.id"
          class="menu-item"
          :class="{ active: activeMenu === item.id }"
          @click="activeMenu = item.id"
        >
          <el-icon :size="16"><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.help-view {
  display: flex;
  height: 100%;
  background: #f5f7fa;
}

// 左侧内容区
.help-content {
  flex: 1;
  padding: 24px 40px;
  overflow-y: auto;
  
  .content-section {
    max-width: 800px;
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #e8e8e8;
    }
    
    h2 {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-top: 24px;
      margin-bottom: 12px;
    }
    
    .intro {
      font-size: 15px;
      color: #666;
      line-height: 1.8;
      margin-bottom: 20px;
    }
    
    p {
      font-size: 14px;
      color: #555;
      line-height: 1.8;
      margin-bottom: 12px;
    }
    
    ul, ol {
      padding-left: 20px;
      margin-bottom: 16px;
      
      li {
        font-size: 14px;
        color: #555;
        line-height: 2;
      }
    }
    
    ul {
      list-style-type: disc;
    }
    
    ol {
      list-style-type: decimal;
    }
  }
}

// 右侧导航
.help-sidebar {
  width: 200px;
  background: #fff;
  border-left: 1px solid #e8e8e8;
  padding: 20px 0;
  flex-shrink: 0;
  
  .sidebar-title {
    padding: 0 20px 16px;
    font-size: 16px;
    font-weight: 600;
    color: #333;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 8px;
  }
  
  .menu-list {
    .menu-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 20px;
      cursor: pointer;
      color: #666;
      font-size: 14px;
      transition: all 0.2s;
      
      &:hover {
        background: #f5f5f5;
        color: #333;
      }
      
      &.active {
        background: #e6f4ff;
        color: #1890ff;
        border-left: 3px solid #1890ff;
      }
    }
  }
}
</style>
