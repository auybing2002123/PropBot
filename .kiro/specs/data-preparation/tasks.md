# 任务清单：数据准备与配置外部化

## 任务概览

| 阶段 | 任务数 | 状态 |
|------|--------|------|
| 阶段一：配置数据文件 | 4 | ✅ 已完成 |
| 阶段二：市场数据文件 | 4 | ✅ 已完成 |
| 阶段三：DataLoader 实现 | 3 | ✅ 已完成 |
| 阶段四：工具重构 | 3 | ✅ 已完成 |
| 阶段五：测试验证 | 2 | ✅ 已完成 |

---

## 阶段一：配置数据文件

### 任务 1.1：创建利率配置文件
- [x] 创建 `backend/data/config/interest_rates.json`
- [x] 包含 LPR 利率、商贷利率、公积金利率
- [x] 验证 JSON 格式正确

**验收标准**：文件存在且 JSON 格式有效 ✅

### 任务 1.2：创建税费规则文件
- [x] 创建 `backend/data/config/tax_rules.json`
- [x] 包含契税、增值税、个税、中介费率
- [x] 从 financial.py 中提取现有硬编码值

**验收标准**：文件存在且包含所有税费规则 ✅

### 任务 1.3：创建公积金政策文件
- [x] 创建 `backend/data/config/provident_fund.json`
- [x] 包含南宁、柳州的公积金贷款额度和政策

**验收标准**：文件存在且包含两个城市的公积金政策 ✅

### 任务 1.4：创建费用标准文件
- [x] 创建 `backend/data/config/cost_reference.json`
- [x] 包含装修费用、物业费、停车费、家具费用参考

**验收标准**：文件存在且包含各类费用标准 ✅

---

## 阶段二：市场数据文件

### 任务 2.1：创建南宁市场数据文件
- [x] 创建 `backend/data/market/nanning.json`
- [x] 从 market.py 的 MARKET_DATA["南宁"] 迁移数据
- [x] 从 market.py 的 PRICE_TREND_DATA["南宁"] 迁移走势数据
- [x] 补充缺失区域的走势数据

**验收标准**：包含 7 个区域的市场数据和价格走势 ✅

### 任务 2.2：创建柳州市场数据文件
- [x] 创建 `backend/data/market/liuzhou.json`
- [x] 从 market.py 迁移柳州数据
- [x] 补充缺失区域的走势数据

**验收标准**：包含 6 个区域的市场数据和价格走势 ✅

### 任务 2.3：创建南宁房源数据文件
- [x] 创建 `backend/data/market/houses/nanning_houses.json`
- [x] 生成 20 套模拟房源数据
- [x] 覆盖不同区域、价格段、户型

**验收标准**：包含 20 套房源，数据结构符合数据需求文档 ✅

### 任务 2.4：创建柳州房源数据文件
- [x] 创建 `backend/data/market/houses/liuzhou_houses.json`
- [x] 生成 15 套模拟房源数据

**验收标准**：包含 15 套房源 ✅

---

## 阶段三：DataLoader 实现

### 任务 3.1：创建数据模型
- [x] 创建 `backend/app/models/data_models.py`
- [x] 定义 InterestRatesConfig 模型
- [x] 定义 TaxRulesConfig 模型
- [x] 定义 CityMarketData 模型
- [x] 定义 HouseData 模型

**验收标准**：所有模型定义完成，能正确解析对应 JSON ✅

### 任务 3.2：实现 DataLoader 服务
- [x] 创建 `backend/app/data/__init__.py`
- [x] 创建 `backend/app/data/loader.py`
- [x] 实现单例模式
- [x] 实现配置数据加载（interest_rates, tax_rules）
- [x] 实现市场数据加载
- [x] 实现 reload() 热更新方法

**验收标准**：DataLoader 能正确加载所有数据文件 ✅

### 任务 3.3：添加数据验证
- [x] 启动时验证必需文件存在
- [x] 加载时验证数据格式
- [x] 错误时记录日志并抛出明确异常

**验收标准**：缺失文件或格式错误时有明确错误提示 ✅

---

## 阶段四：工具重构

### 任务 4.1：重构 CalcTaxTool
- [x] 修改 `backend/app/agent/tools/financial.py`
- [x] 导入 DataLoader
- [x] 将硬编码税率替换为从 DataLoader 读取
- [x] 保持计算逻辑不变

**验收标准**：税费计算结果与重构前一致 ✅

### 任务 4.2：重构市场查询工具
- [x] 修改 `backend/app/agent/tools/market.py`
- [x] 删除 MARKET_DATA 和 PRICE_TREND_DATA 硬编码
- [x] 从 DataLoader 获取市场数据
- [x] 修改 QueryMarketTool、QueryPriceTrendTool、CompareDistrictsTool、JudgeTimingTool

**验收标准**：市场查询结果与重构前一致 ✅

### 任务 4.3：更新辅助函数
- [x] 修改 get_city_districts() 使用 DataLoader
- [x] 修改 get_district_data() 使用 DataLoader
- [x] 修改 get_city_overview() 使用 DataLoader

**验收标准**：所有辅助函数正常工作 ✅

---

## 阶段五：测试验证

### 任务 5.1：DataLoader 单元测试
- [x] 创建 `backend/tests/test_data_loader.py`
- [x] 测试配置数据加载
- [x] 测试市场数据加载
- [x] 测试缓存机制
- [x] 测试 reload() 功能
- [x] 测试文件缺失错误处理

**验收标准**：所有测试通过 ✅

### 任务 5.2：集成测试验证
- [x] 运行现有的 test_financial_tools_pbt.py
- [x] 运行现有的市场工具测试
- [x] 确保重构后功能不变

**验收标准**：所有现有测试通过 ✅

---

## 执行顺序

```
阶段一（配置文件）
    ↓
阶段二（市场数据）
    ↓
阶段三（DataLoader）
    ↓
阶段四（工具重构）
    ↓
阶段五（测试验证）
```

## 注意事项

1. **数据一致性**：从代码迁移数据时，确保数值完全一致
2. **向后兼容**：重构后工具的输入输出格式保持不变
3. **错误处理**：数据文件问题不应导致整个服务崩溃
4. **日志记录**：数据加载过程记录日志，便于排查问题
