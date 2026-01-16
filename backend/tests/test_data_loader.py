# DataLoader 单元测试
# 测试数据加载、缓存、热更新功能

import pytest
from app.data.loader import DataLoader, get_data_loader


class TestDataLoaderSingleton:
    """测试单例模式"""
    
    def test_singleton_instance(self):
        """验证 DataLoader 是单例"""
        loader1 = DataLoader()
        loader2 = DataLoader()
        assert loader1 is loader2
    
    def test_get_data_loader_returns_singleton(self):
        """验证 get_data_loader 返回单例"""
        loader1 = get_data_loader()
        loader2 = get_data_loader()
        assert loader1 is loader2


class TestConfigDataLoading:
    """测试配置数据加载"""
    
    def test_load_interest_rates(self):
        """测试加载利率配置"""
        loader = get_data_loader()
        rates = loader.interest_rates
        
        assert rates is not None
        assert rates.lpr is not None
        assert rates.commercial_loan is not None
        assert rates.provident_fund is not None
    
    def test_load_tax_rules(self):
        """测试加载税费规则"""
        loader = get_data_loader()
        tax = loader.tax_rules
        
        assert tax is not None
        assert tax.deed_tax is not None
        assert tax.vat is not None
        assert tax.income_tax is not None
        assert tax.other_fees is not None
    
    def test_load_provident_fund(self):
        """测试加载公积金政策"""
        loader = get_data_loader()
        pf = loader.provident_fund
        
        assert pf is not None
        assert "南宁" in pf.cities or "nanning" in str(pf.cities).lower()
    
    def test_load_cost_reference(self):
        """测试加载费用标准"""
        loader = get_data_loader()
        cost = loader.cost_reference
        
        assert cost is not None
        assert cost.decoration_cost is not None
        assert cost.property_fee is not None


class TestMarketDataLoading:
    """测试市场数据加载"""
    
    def test_get_supported_cities(self):
        """测试获取支持的城市列表"""
        loader = get_data_loader()
        cities = loader.get_supported_cities()
        
        assert "南宁" in cities
        assert "柳州" in cities
    
    def test_get_market_data_nanning(self):
        """测试获取南宁市场数据"""
        loader = get_data_loader()
        data = loader.get_market_data("南宁")
        
        assert data is not None
        assert data.city == "南宁"
        assert len(data.districts) > 0
        assert "青秀区" in data.districts
    
    def test_get_market_data_liuzhou(self):
        """测试获取柳州市场数据"""
        loader = get_data_loader()
        data = loader.get_market_data("柳州")
        
        assert data is not None
        assert data.city == "柳州"
        assert len(data.districts) > 0
    
    def test_get_market_data_unsupported_city(self):
        """测试获取不支持城市的数据"""
        loader = get_data_loader()
        data = loader.get_market_data("北京")
        
        assert data is None
    
    def test_get_city_districts(self):
        """测试获取城市区域列表"""
        loader = get_data_loader()
        districts = loader.get_city_districts("南宁")
        
        assert len(districts) > 0
        assert "青秀区" in districts
        assert "良庆区" in districts
    
    def test_get_district_data(self):
        """测试获取区域数据"""
        loader = get_data_loader()
        data = loader.get_district_data("南宁", "青秀区")
        
        assert data is not None
        assert "avg_price" in data
        assert "monthly_sales" in data
        assert "hot_level" in data
    
    def test_get_district_data_not_found(self):
        """测试获取不存在的区域数据"""
        loader = get_data_loader()
        data = loader.get_district_data("南宁", "不存在区")
        
        assert data is None


class TestPriceTrendData:
    """测试价格走势数据"""
    
    def test_get_price_trend(self):
        """测试获取价格走势"""
        loader = get_data_loader()
        trend = loader.get_price_trend("南宁", "青秀区")
        
        assert trend is not None
        assert len(trend) > 0
        assert "month" in trend[0]
        assert "price" in trend[0]
    
    def test_get_price_trend_not_found(self):
        """测试获取不存在的走势数据"""
        loader = get_data_loader()
        trend = loader.get_price_trend("南宁", "不存在区")
        
        assert trend is None


class TestCaching:
    """测试缓存机制"""
    
    def test_config_caching(self):
        """测试配置数据缓存"""
        loader = get_data_loader()
        
        # 第一次加载
        rates1 = loader.interest_rates
        # 第二次应该返回缓存
        rates2 = loader.interest_rates
        
        assert rates1 is rates2
    
    def test_market_data_caching(self):
        """测试市场数据缓存"""
        loader = get_data_loader()
        
        # 第一次加载
        data1 = loader.get_market_data("南宁")
        # 第二次应该返回缓存
        data2 = loader.get_market_data("南宁")
        
        assert data1 is data2


class TestReload:
    """测试热更新功能"""
    
    def test_reload_clears_cache(self):
        """测试 reload 清除缓存"""
        loader = get_data_loader()
        
        # 先加载数据
        _ = loader.interest_rates
        _ = loader.get_market_data("南宁")
        
        # 重新加载
        loader.reload()
        
        # 验证缓存被清除（内部属性为 None）
        assert loader._interest_rates is None
        assert len(loader._market_data) == 0


class TestValidation:
    """测试数据验证"""
    
    def test_validate_required_files(self):
        """测试验证必需文件"""
        loader = get_data_loader()
        missing = loader.validate_required_files()
        
        # 所有必需文件应该存在
        assert len(missing) == 0, f"缺失文件: {missing}"
