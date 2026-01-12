"""
计算器 API 测试
验证贷款计算、税费计算、总成本计算接口
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestLoanCalcAPI:
    """贷款计算 API 测试"""
    
    def test_calc_loan_equal_payment(self):
        """测试等额本息贷款计算"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 2000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2,
            "method": "equal_payment"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "success"
        assert data["data"] is not None
        
        result = data["data"]
        assert result["down_payment"] == 600000
        assert result["loan_amount"] == 1400000
        assert result["method"] == "equal_payment"
        assert result["monthly_payment"] > 0
        assert result["total_interest"] > 0
    
    def test_calc_loan_equal_principal(self):
        """测试等额本金贷款计算"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 2000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2,
            "method": "equal_principal"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["method"] == "equal_principal"
        assert data["data"]["first_month_payment"] > data["data"]["last_month_payment"]
    
    def test_calc_loan_validation_error(self):
        """测试参数验证错误"""
        response = client.post("/api/v1/calc/loan", json={
            "price": -100,  # 无效价格
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        })
        
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == 3001
        assert "参数验证错误" in data["message"]
    
    def test_calc_loan_missing_param(self):
        """测试缺少必需参数"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 2000000
            # 缺少其他必需参数
        })
        
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == 3001


class TestTaxCalcAPI:
    """税费计算 API 测试"""
    
    def test_calc_tax_first_home_small(self):
        """测试首套小面积房税费计算"""
        response = client.post("/api/v1/calc/tax", json={
            "price": 1000000,
            "area": 80,
            "is_first_home": True,
            "house_age_years": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        # 首套≤90㎡，契税1%
        assert result["deed_tax"] == 10000
        assert result["deed_tax_rate"] == 0.01
        # 满2年免增值税
        assert result["vat"] == 0
        assert result["vat_exempt"] is True
    
    def test_calc_tax_second_home_large(self):
        """测试二套大面积房税费计算"""
        response = client.post("/api/v1/calc/tax", json={
            "price": 2000000,
            "area": 120,
            "is_first_home": False,
            "house_age_years": 1
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        # 二套>90㎡，契税2%
        assert result["deed_tax"] == 40000
        assert result["deed_tax_rate"] == 0.02
        # 不满2年有增值税
        assert result["vat_exempt"] is False


class TestTotalCostCalcAPI:
    """总成本计算 API 测试"""
    
    def test_calc_total_cost_basic(self):
        """测试基本总成本计算"""
        response = client.post("/api/v1/calc/total_cost", json={
            "price": 2000000,
            "down_payment": 600000,
            "total_interest": 500000,
            "taxes": 50000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        assert result["price"] == 2000000
        assert result["loan_amount"] == 1400000
        # 总成本 = 房价 + 利息 + 税费
        assert result["total_cost"] == 2550000
    
    def test_calc_total_cost_with_extras(self):
        """测试包含装修等额外费用的总成本计算"""
        response = client.post("/api/v1/calc/total_cost", json={
            "price": 2000000,
            "down_payment": 600000,
            "total_interest": 500000,
            "taxes": 50000,
            "decoration": 200000,
            "furniture": 50000,
            "other_fees": 10000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        # 总成本 = 房价 + 利息 + 税费 + 装修 + 家具 + 其他
        assert result["total_cost"] == 2810000


class TestAPIResponseFormat:
    """API 响应格式测试"""
    
    def test_success_response_format(self):
        """测试成功响应格式"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 1000000,
            "down_payment_ratio": 0.3,
            "years": 20,
            "rate": 4.0
        })
        
        data = response.json()
        # 验证统一响应格式
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert data["code"] == 0
        assert data["message"] == "success"
    
    def test_error_response_format(self):
        """测试错误响应格式"""
        response = client.post("/api/v1/calc/loan", json={
            "price": "invalid"  # 类型错误
        })
        
        data = response.json()
        # 验证统一响应格式
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert data["code"] != 0
