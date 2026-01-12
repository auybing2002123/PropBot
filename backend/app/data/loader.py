# 数据加载服务
# 负责从 JSON 文件加载配置和市场数据，提供单例模式访问

import json
import logging
from pathlib import Path
from typing import Optional

from app.models.data_models import (
    InterestRatesConfig,
    TaxRulesConfig,
    ProvidentFundConfig,
    CostReferenceConfig,
    CityMarketData,
    CityHousesData,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    数据加载服务（单例模式）
    负责从 JSON 文件加载配置和市场数据
    """
    
    _instance: Optional["DataLoader"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 数据目录路径
        self._data_dir = Path(__file__).parent.parent.parent / "data"
        
        # 缓存的配置数据
        self._interest_rates: Optional[InterestRatesConfig] = None
        self._tax_rules: Optional[TaxRulesConfig] = None
        self._provident_fund: Optional[ProvidentFundConfig] = None
        self._cost_reference: Optional[CostReferenceConfig] = None
        
        # 缓存的市场数据
        self._market_data: dict[str, CityMarketData] = {}
        self._houses_data: dict[str, CityHousesData] = {}
        
        # 城市名到文件名的映射
        self._city_file_map = {
            "南宁": "nanning",
            "柳州": "liuzhou",
        }
        
        self._initialized = True
        logger.info(f"DataLoader 初始化完成，数据目录: {self._data_dir}")
    
    def _load_json(self, path: Path) -> dict:
        """加载 JSON 文件"""
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {path}, {e}")
            raise ValueError(f"数据文件格式错误: {path}")
    
    # ========== 配置数据访问 ==========
    
    @property
    def interest_rates(self) -> InterestRatesConfig:
        """获取利率配置"""
        if self._interest_rates is None:
            path = self._data_dir / "config" / "interest_rates.json"
            data = self._load_json(path)
            self._interest_rates = InterestRatesConfig(**data)
            logger.debug(f"加载利率配置: {path}")
        return self._interest_rates
    
    @property
    def tax_rules(self) -> TaxRulesConfig:
        """获取税费规则"""
        if self._tax_rules is None:
            path = self._data_dir / "config" / "tax_rules.json"
            data = self._load_json(path)
            self._tax_rules = TaxRulesConfig(**data)
            logger.debug(f"加载税费规则: {path}")
        return self._tax_rules
    
    @property
    def provident_fund(self) -> ProvidentFundConfig:
        """获取公积金政策"""
        if self._provident_fund is None:
            path = self._data_dir / "config" / "provident_fund.json"
            data = self._load_json(path)
            self._provident_fund = ProvidentFundConfig(**data)
            logger.debug(f"加载公积金政策: {path}")
        return self._provident_fund
    
    @property
    def cost_reference(self) -> CostReferenceConfig:
        """获取费用标准"""
        if self._cost_reference is None:
            path = self._data_dir / "config" / "cost_reference.json"
            data = self._load_json(path)
            self._cost_reference = CostReferenceConfig(**data)
            logger.debug(f"加载费用标准: {path}")
        return self._cost_reference
    
    # ========== 市场数据访问 ==========
    
    def get_market_data(self, city: str) -> Optional[CityMarketData]:
        """
        获取城市市场数据
        
        Args:
            city: 城市名称（如：南宁、柳州）
            
        Returns:
            城市市场数据，不存在则返回 None
        """
        if city not in self._market_data:
            filename = self._city_file_map.get(city)
            if not filename:
                logger.warning(f"不支持的城市: {city}")
                return None
            
            path = self._data_dir / "market" / f"{filename}.json"
            if not path.exists():
                logger.warning(f"市场数据文件不存在: {path}")
                return None
            
            try:
                data = self._load_json(path)
                self._market_data[city] = CityMarketData(**data)
                logger.debug(f"加载市场数据: {path}")
            except Exception as e:
                logger.error(f"加载市场数据失败: {path}, {e}")
                return None
        
        return self._market_data.get(city)
    
    def get_houses_data(self, city: str) -> Optional[CityHousesData]:
        """
        获取城市房源数据
        
        Args:
            city: 城市名称（如：南宁、柳州）
            
        Returns:
            城市房源数据，不存在则返回 None
        """
        if city not in self._houses_data:
            filename = self._city_file_map.get(city)
            if not filename:
                logger.warning(f"不支持的城市: {city}")
                return None
            
            path = self._data_dir / "market" / "houses" / f"{filename}_houses.json"
            if not path.exists():
                logger.warning(f"房源数据文件不存在: {path}")
                return None
            
            try:
                data = self._load_json(path)
                self._houses_data[city] = CityHousesData(**data)
                logger.debug(f"加载房源数据: {path}")
            except Exception as e:
                logger.error(f"加载房源数据失败: {path}, {e}")
                return None
        
        return self._houses_data.get(city)
    
    # ========== 便捷方法 ==========
    
    def get_supported_cities(self) -> list[str]:
        """获取支持的城市列表"""
        return list(self._city_file_map.keys())
    
    def get_district_data(self, city: str, district: str) -> Optional[dict]:
        """
        获取指定区域的市场数据
        
        Args:
            city: 城市名称
            district: 区域名称
            
        Returns:
            区域市场数据字典，不存在则返回 None
        """
        market_data = self.get_market_data(city)
        if not market_data:
            return None
        
        district_data = market_data.districts.get(district)
        if not district_data:
            return None
        
        return district_data.model_dump()
    
    def get_city_districts(self, city: str) -> list[str]:
        """
        获取城市的所有区域
        
        Args:
            city: 城市名称
            
        Returns:
            区域名称列表
        """
        market_data = self.get_market_data(city)
        if not market_data:
            return []
        return list(market_data.districts.keys())
    
    def get_price_trend(self, city: str, district: str) -> Optional[list[dict]]:
        """
        获取区域房价走势
        
        Args:
            city: 城市名称
            district: 区域名称
            
        Returns:
            价格走势列表，不存在则返回 None
        """
        market_data = self.get_market_data(city)
        if not market_data:
            return None
        
        trend = market_data.price_trends.get(district)
        if not trend:
            return None
        
        return [p.model_dump() for p in trend]
    
    # ========== 数据管理 ==========
    
    def reload(self):
        """重新加载所有数据（热更新）"""
        self._interest_rates = None
        self._tax_rules = None
        self._provident_fund = None
        self._cost_reference = None
        self._market_data.clear()
        self._houses_data.clear()
        logger.info("数据已重新加载")
    
    def validate_required_files(self) -> list[str]:
        """
        验证必需的数据文件是否存在
        
        Returns:
            缺失的文件路径列表
        """
        required_files = [
            self._data_dir / "config" / "interest_rates.json",
            self._data_dir / "config" / "tax_rules.json",
            self._data_dir / "config" / "provident_fund.json",
            self._data_dir / "config" / "cost_reference.json",
        ]
        
        missing = []
        for path in required_files:
            if not path.exists():
                missing.append(str(path))
        
        return missing


# 全局访问函数
def get_data_loader() -> DataLoader:
    """获取 DataLoader 单例"""
    return DataLoader()
