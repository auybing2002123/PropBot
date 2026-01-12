# 需求文档：数据准备与配置外部化

## 简介

本需求文档定义了购房决策智能助手的数据准备工作，包括将硬编码数据抽取到独立配置文件、创建模拟市场数据、以及重构代码以支持从外部文件加载数据。

## 术语表

- **Data_Loader**: 数据加载服务，负责从 JSON 文件读取配置和市场数据
- **Config_Data**: 配置数据，包括利率、税费规则、公积金政策等相对稳定的数据
- **Market_Data**: 市场数据，包括各区域房价、成交量、库存等动态数据
- **House_Data**: 房源数据，模拟的在售房源信息
- **Community_Data**: 小区数据，包含小区详情和周边配套

## 需求列表

### 需求 1：配置数据文件创建

**用户故事：** 作为开发者，我希望将税费规则、利率等配置数据存储在独立的 JSON 文件中，以便于维护和更新。

#### 验收标准

1. THE Data_Loader SHALL 从 `data/config/interest_rates.json` 读取贷款利率数据
2. THE Data_Loader SHALL 从 `data/config/tax_rules.json` 读取税费规则数据
3. THE Data_Loader SHALL 从 `data/config/provident_fund.json` 读取公积金政策数据
4. THE Data_Loader SHALL 从 `data/config/cost_reference.json` 读取费用标准数据
5. WHEN 配置文件不存在时 THEN THE Data_Loader SHALL 抛出明确的错误信息

### 需求 2：市场数据文件创建

**用户故事：** 作为开发者，我希望将市场数据存储在独立的 JSON 文件中，以便于模拟不同的市场场景。

#### 验收标准

1. THE Data_Loader SHALL 从 `data/market/nanning.json` 读取南宁市场数据
2. THE Data_Loader SHALL 从 `data/market/liuzhou.json` 读取柳州市场数据
3. WHEN 查询不存在的城市时 THEN THE Data_Loader SHALL 返回空结果而非抛出异常
4. THE Market_Data SHALL 包含各区域的均价、成交量、库存量、同比环比变化
5. THE Market_Data SHALL 包含近12个月的房价走势数据

### 需求 3：房源模拟数据创建

**用户故事：** 作为用户，我希望能够查看模拟的房源信息，以便了解系统的房源展示功能。

#### 验收标准

1. THE House_Data SHALL 存储在 `data/market/houses/` 目录下
2. THE House_Data SHALL 包含南宁至少 20 套模拟房源
3. THE House_Data SHALL 包含柳州至少 15 套模拟房源
4. WHEN 查询房源时 THE Data_Loader SHALL 支持按城市、区域、价格范围筛选
5. THE House_Data SHALL 符合数据需求文档中定义的房源数据结构

### 需求 4：小区模拟数据创建

**用户故事：** 作为用户，我希望能够查看小区详情和周边配套信息。

#### 验收标准

1. THE Community_Data SHALL 存储在 `data/market/communities/` 目录下
2. THE Community_Data SHALL 包含南宁至少 10 个模拟小区
3. THE Community_Data SHALL 包含柳州至少 8 个模拟小区
4. THE Community_Data SHALL 包含周边配套信息（地铁、学校、医院、商场）
5. THE Community_Data SHALL 包含近6个月的小区均价走势

### 需求 5：数据加载服务实现

**用户故事：** 作为开发者，我希望有一个统一的数据加载服务来管理所有数据文件的读取。

#### 验收标准

1. THE Data_Loader SHALL 提供单例模式访问
2. THE Data_Loader SHALL 在首次访问时加载数据并缓存
3. THE Data_Loader SHALL 提供 `reload()` 方法支持热更新数据
4. WHEN 数据文件格式错误时 THEN THE Data_Loader SHALL 记录错误日志并抛出异常
5. THE Data_Loader SHALL 提供类型安全的数据访问接口

### 需求 6：财务工具重构

**用户故事：** 作为开发者，我希望财务计算工具从配置文件读取税费规则，而非硬编码。

#### 验收标准

1. THE CalcTaxTool SHALL 从 Data_Loader 获取契税税率
2. THE CalcTaxTool SHALL 从 Data_Loader 获取增值税税率
3. THE CalcTaxTool SHALL 从 Data_Loader 获取个税税率
4. THE CalcTaxTool SHALL 从 Data_Loader 获取中介费率
5. WHEN 配置数据更新后 THEN THE CalcTaxTool SHALL 使用最新的税率计算

### 需求 7：市场工具重构

**用户故事：** 作为开发者，我希望市场查询工具从数据文件读取市场数据，而非硬编码。

#### 验收标准

1. THE QueryMarketTool SHALL 从 Data_Loader 获取市场数据
2. THE QueryPriceTrendTool SHALL 从 Data_Loader 获取房价走势数据
3. THE CompareDistrictsTool SHALL 从 Data_Loader 获取区域对比数据
4. THE JudgeTimingTool SHALL 从 Data_Loader 获取市场分析数据
5. WHEN 新增城市数据文件后 THEN THE 市场工具 SHALL 自动支持新城市查询

### 需求 8：数据验证

**用户故事：** 作为开发者，我希望数据文件在加载时进行格式验证，确保数据完整性。

#### 验收标准

1. THE Data_Loader SHALL 使用 Pydantic 模型验证配置数据格式
2. THE Data_Loader SHALL 使用 Pydantic 模型验证市场数据格式
3. WHEN 数据缺少必填字段时 THEN THE Data_Loader SHALL 抛出验证错误
4. WHEN 数据类型不匹配时 THEN THE Data_Loader SHALL 抛出验证错误
5. THE Data_Loader SHALL 在启动时验证所有必需的数据文件存在

