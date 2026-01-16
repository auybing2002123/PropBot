# 设计文档：数据准备与配置外部化

## 概述

本设计文档描述数据准备模块的技术实现方案，包括数据文件结构、DataLoader 服务设计、以及工具重构方案。

## 架构设计

### 数据目录结构

```
backend/data/
├── config/                          # 配置数据（相对稳定）
│   ├── interest_rates.json          # 贷款利率
│   ├── tax_rules.json               # 税费规则
│   ├── provident_fund.json          # 公积金政策
│   └── cost_reference.json          # 费用标准
├── market/                          # 市场数据（动态）
│   ├── nanning.json                 # 南宁市场数据
│   ├── liuzhou.json                 # 柳州市场数据
│   ├── houses/                      # 房源数据
│   │   ├── nanning_houses.json
│   │   └── liuzhou_houses.json
│   └── communities/                 # 小区数据
│       ├── nanning_communities.json
│       └── liuzhou_communities.json
└── knowledge/                       # 知识库（已存在）
    ├── policies/
    ├── guides/
    └── faq/
```

### 组件关系图

```
┌─────────────────────────────────────────────────────────┐
│                      工具层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ CalcTaxTool │  │QueryMarket  │  │ PolicyTool  │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
└─────────┼────────────────┼────────────────┼─────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                    DataLoader（单例）                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ ConfigData  │  │ MarketData  │  │ HouseData   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                    JSON 数据文件                         │
│  data/config/*.json    data/market/*.json               │
└─────────────────────────────────────────────────────────┘
```

## 详细设计

### 1. Pydantic 数据模型

文件：`backend/app/models/data_models.py`

```python
from pydantic import BaseModel
from typing import Optional

# ========== 配置数据模型 ==========

class LPRRates(BaseModel):
    """LPR 利率"""
    lpr_1y: float  # 1年期 LPR
    lpr_5y: float  # 5年期 LPR

class LoanRateConfig(BaseModel):
    """贷款利率配置"""
    rate: float
    rate_formula: str

class CommercialLoanRates(BaseModel):
    """商业贷款利率"""
    first_home: LoanRateConfig
    second_home: LoanRateConfig

class ProvidentFundRates(BaseModel):
    """公积金利率"""
    below_5y: float
    above_5y: float

class InterestRatesConfig(BaseModel):
    """利率配置"""
    update_date: str
    lpr: LPRRates
    commercial_loan: CommercialLoanRates
    provident_fund: ProvidentFundRates

class DeedTaxRates(BaseModel):
    """契税税率"""
    first_home_below_90: float
    first_home_above_90: float
    second_home_below_90: float
    second_home_above_90: float
    third_home: float

class TaxRulesConfig(BaseModel):
    """税费规则配置"""
    update_date: str
    deed_tax: DeedTaxRates
    vat_below_2y: float
    income_tax_rate: float
    agent_fee_rate: float
    other_fees: float

# ========== 市场数据模型 ==========

class DistrictMarketData(BaseModel):
    """区域市场数据"""
    avg_price: int
    price_range: list[int]
    monthly_sales: int
    inventory: int
    inventory_months: float
    yoy_change: float
    mom_change: float
    hot_level: str
    description: str

class PriceTrendPoint(BaseModel):
    """价格走势点"""
    month: str
    price: int

class CityMarketData(BaseModel):
    """城市市场数据"""
    city: str
    update_date: str
    districts: dict[str, DistrictMarketData]
    price_trends: dict[str, list[PriceTrendPoint]]
```

### 2. DataLoader 服务

文件：`backend/app/data/loader.py`

```python
import json
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache

from app.models.data_models import (
    InterestRatesConfig,
    TaxRulesConfig,
    CityMarketData,
)

logger = logging.getLogger(__name__)

class DataLoader:
    """
    数据加载服务（单例模式）
    负责从 JSON 文件加载配置和市场数据
    """
    
    _instance: Optional["DataLoader"] = None
    _data_dir: Path
    
    # 缓存的数据
    _interest_rates: Optional[InterestRatesConfig] = None
    _tax_rules: Optional[TaxRulesConfig] = None
    _market_data: dict[str, CityMarketData] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data_dir = Path(__file__).parent.parent.parent / "data"
            cls._instance._loaded = False
        return cls._instance
    
    def _load_json(self, path: Path) -> dict:
        """加载 JSON 文件"""
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @property
    def interest_rates(self) -> InterestRatesConfig:
        """获取利率配置"""
        if self._interest_rates is None:
            path = self._data_dir / "config" / "interest_rates.json"
            data = self._load_json(path)
            self._interest_rates = InterestRatesConfig(**data)
        return self._interest_rates
    
    @property
    def tax_rules(self) -> TaxRulesConfig:
        """获取税费规则"""
        if self._tax_rules is None:
            path = self._data_dir / "config" / "tax_rules.json"
            data = self._load_json(path)
            self._tax_rules = TaxRulesConfig(**data)
        return self._tax_rules
    
    def get_market_data(self, city: str) -> Optional[CityMarketData]:
        """获取城市市场数据"""
        if city not in self._market_data:
            city_file = f"{city.lower()}.json"
            # 城市名映射
            file_map = {"南宁": "nanning.json", "柳州": "liuzhou.json"}
            filename = file_map.get(city, city_file)
            path = self._data_dir / "market" / filename
            if not path.exists():
                return None
            data = self._load_json(path)
            self._market_data[city] = CityMarketData(**data)
        return self._market_data.get(city)
    
    def reload(self):
        """重新加载所有数据（热更新）"""
        self._interest_rates = None
        self._tax_rules = None
        self._market_data.clear()
        logger.info("数据已重新加载")


# 全局访问函数
def get_data_loader() -> DataLoader:
    """获取 DataLoader 单例"""
    return DataLoader()
```

### 3. 工具重构方案

#### 3.1 CalcTaxTool 重构

修改 `backend/app/agent/tools/financial.py`：

```python
from app.data.loader import get_data_loader

class CalcTaxTool(BaseTool):
    async def execute(self, **kwargs) -> dict:
        # 从 DataLoader 获取税费规则
        tax_rules = get_data_loader().tax_rules
        
        # 使用配置中的税率
        deed_tax_rate = self._get_deed_tax_rate(
            area, is_first_home, tax_rules.deed_tax
        )
        # ...
```

#### 3.2 市场工具重构

修改 `backend/app/agent/tools/market.py`：

```python
from app.data.loader import get_data_loader

# 删除硬编码的 MARKET_DATA 和 PRICE_TREND_DATA

class QueryMarketTool(BaseTool):
    async def execute(self, **kwargs) -> dict:
        city = kwargs["city"]
        
        # 从 DataLoader 获取市场数据
        market_data = get_data_loader().get_market_data(city)
        if not market_data:
            return {"success": False, "error": f"暂不支持 {city}"}
        
        # 使用 market_data.districts 替代原来的 MARKET_DATA[city]
        # ...
```

## 数据文件格式

### interest_rates.json

```json
{
  "update_date": "2025-01-10",
  "lpr": {
    "lpr_1y": 3.10,
    "lpr_5y": 3.60
  },
  "commercial_loan": {
    "first_home": {"rate": 3.40, "rate_formula": "LPR-20BP"},
    "second_home": {"rate": 3.80, "rate_formula": "LPR+20BP"}
  },
  "provident_fund": {
    "below_5y": 2.35,
    "above_5y": 2.85
  }
}
```

### tax_rules.json

```json
{
  "update_date": "2025-01-10",
  "deed_tax": {
    "first_home_below_90": 0.01,
    "first_home_above_90": 0.015,
    "second_home_below_90": 0.01,
    "second_home_above_90": 0.02,
    "third_home": 0.03
  },
  "vat_below_2y": 0.056,
  "income_tax_rate": 0.01,
  "agent_fee_rate": 0.02,
  "other_fees": 3000
}
```

### nanning.json（市场数据）

```json
{
  "city": "南宁",
  "update_date": "2025-01-10",
  "districts": {
    "青秀区": {
      "avg_price": 15800,
      "price_range": [12000, 25000],
      "monthly_sales": 320,
      "inventory": 4500,
      "inventory_months": 14.1,
      "yoy_change": -2.5,
      "mom_change": -0.3,
      "hot_level": "高",
      "description": "南宁核心城区，配套成熟，学区资源丰富"
    }
  },
  "price_trends": {
    "青秀区": [
      {"month": "2025-01", "price": 16200},
      {"month": "2025-02", "price": 16100}
    ]
  }
}
```

## 测试策略

1. **单元测试**：测试 DataLoader 的加载、缓存、重载功能
2. **集成测试**：测试工具使用 DataLoader 后的计算结果
3. **数据验证测试**：测试 Pydantic 模型对错误数据的校验

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 数据文件缺失导致启动失败 | 启动时检查必需文件，缺失时给出明确错误 |
| JSON 格式错误 | Pydantic 验证 + 详细错误信息 |
| 数据更新后未生效 | 提供 reload() 方法，或重启服务 |
