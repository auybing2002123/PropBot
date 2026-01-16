# 数据模型定义
# 用于验证 JSON 配置文件和市场数据的格式

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


class VATRates(BaseModel):
    """增值税税率"""
    below_2y: float
    above_2y: float


class IncomeTaxRates(BaseModel):
    """个税税率"""
    rate: float
    diff_rate: float
    full_5y_only: float


class OtherFees(BaseModel):
    """其他费用"""
    registration_fee: float
    stamp_duty: float
    agent_fee_rate: float
    misc_fees: float


class TaxRulesConfig(BaseModel):
    """税费规则配置"""
    update_date: str
    deed_tax: DeedTaxRates
    vat: VATRates
    income_tax: IncomeTaxRates
    other_fees: OtherFees


class CityProvidentFund(BaseModel):
    """城市公积金政策"""
    single_max_loan: int
    couple_max_loan: int
    min_deposit_months: int
    first_home_down_payment: float
    second_home_down_payment: float
    loan_rate_below_5y: float
    loan_rate_above_5y: float


class ProvidentFundConfig(BaseModel):
    """公积金政策配置"""
    update_date: str
    cities: dict[str, CityProvidentFund]


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


# ========== 房源数据模型 ==========

class PriceHistoryPoint(BaseModel):
    """价格历史点"""
    date: str
    price: int


class HouseData(BaseModel):
    """房源数据"""
    house_id: str
    district: str
    community: str
    address: str
    price_total: int
    price_per_sqm: int
    area: float
    layout: str
    floor: str
    orientation: str
    decoration: str
    building_year: int
    property_type: str
    property_rights: str
    elevator: bool
    listing_date: str
    price_history: list[PriceHistoryPoint]


class CityHousesData(BaseModel):
    """城市房源数据"""
    city: str
    update_date: str
    houses: list[HouseData]


# ========== 费用标准模型 ==========

class CostRange(BaseModel):
    """费用范围"""
    min: float
    max: float
    unit: str
    desc: Optional[str] = None


class CostRangeSimple(BaseModel):
    """简单费用范围"""
    min: float
    max: float
    unit: str
    avg: Optional[float] = None


class ParkingCost(BaseModel):
    """停车费用"""
    buy: CostRangeSimple
    rent: CostRangeSimple


class CostReferenceConfig(BaseModel):
    """费用标准配置"""
    update_date: str
    decoration_cost: dict[str, CostRange]
    property_fee: dict[str, CostRangeSimple]
    parking: dict[str, ParkingCost]
    furniture: dict[str, CostRange]
