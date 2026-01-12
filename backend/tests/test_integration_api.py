# 集成测试 - API 端点测试
# 任务 15: 最终检查点 - 集成测试

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    with TestClient(app) as c:
        yield c


class TestHealthAPI:
    """健康检查 API 测试"""
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert data["data"]["name"] == "购房决策智能助手"
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "healthy"


class TestCalculatorLoanAPI:
    """贷款计算 API 测试"""
    
    def test_calc_loan_equal_payment(self, client):
        """测试等额本息贷款计算"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 1000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2,
            "method": "equal_payment"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "success"
        assert "data" in data
        
        result = data["data"]
        assert result["down_payment"] == 300000
        assert result["loan_amount"] == 700000
        assert result["monthly_payment"] > 0
        assert result["total_interest"] > 0
        assert result["method"] == "equal_payment"
    
    def test_calc_loan_equal_principal(self, client):
        """测试等额本金贷款计算"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 1000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2,
            "method": "equal_principal"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        assert result["method"] == "equal_principal"
        assert result["first_month_payment"] > result["last_month_payment"]
    
    def test_calc_loan_zero_rate(self, client):
        """测试零利率贷款计算"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 1000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 0,
            "method": "equal_payment"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        assert result["total_interest"] == 0
        # 零利率时月供 = 贷款金额 / 月数
        expected_monthly = 700000 / 360
        assert abs(result["monthly_payment"] - expected_monthly) < 0.01
    
    def test_calc_loan_validation_error(self, client):
        """测试参数验证错误"""
        response = client.post("/api/v1/calc/loan", json={
            "price": -1000,  # 无效价格
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        })
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == 3001
        assert "参数验证错误" in data["message"]


class TestCalculatorTaxAPI:
    """税费计算 API 测试"""
    
    def test_calc_tax_first_home_small(self, client):
        """测试首套小面积房税费"""
        response = client.post("/api/v1/calc/tax", json={
            "price": 1000000,
            "area": 85,
            "is_first_home": True,
            "house_age_years": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        # 首套小面积契税 1%
        assert result["deed_tax_rate"] == 0.01
        assert result["deed_tax"] == 10000
        # 满 2 年免增值税
        assert result["vat"] == 0
        assert result["vat_exempt"] is True
    
    def test_calc_tax_second_home_large(self, client):
        """测试二套大面积房税费"""
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
        # 二套大面积契税 2%
        assert result["deed_tax_rate"] == 0.02
        # 不满 2 年有增值税
        assert result["vat"] > 0
        assert result["vat_exempt"] is False


class TestCalculatorTotalCostAPI:
    """总成本计算 API 测试"""
    
    def test_calc_total_cost(self, client):
        """测试总成本计算"""
        response = client.post("/api/v1/calc/total_cost", json={
            "price": 1000000,
            "down_payment": 300000,
            "total_interest": 500000,
            "taxes": 50000,
            "decoration": 100000,
            "furniture": 50000,
            "other_fees": 10000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        result = data["data"]
        # 验证总成本计算
        expected_total = 1000000 + 500000 + 50000 + 100000 + 50000 + 10000
        assert result["total_cost"] == expected_total
        
        # 验证初期投入
        expected_initial = 300000 + 50000 + 100000 + 50000 + 10000
        assert result["initial_cost"] == expected_initial


class TestChatAPI:
    """对话 API 测试"""
    
    def test_chat_endpoint_exists(self, client):
        """测试对话端点存在"""
        # 发送一个简单请求，验证端点存在
        response = client.post("/api/v1/chat", json={
            "session_id": "test-session-001",
            "message": "你好",
            "mode": "standard"
        })
        # 应该返回流式响应
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"
    
    def test_chat_invalid_mode(self, client):
        """测试无效的 mode 参数"""
        response = client.post("/api/v1/chat", json={
            "session_id": "test-session-001",
            "message": "你好",
            "mode": "invalid_mode"
        })
        assert response.status_code == 400
    
    def test_chat_missing_session_id(self, client):
        """测试缺少 session_id"""
        response = client.post("/api/v1/chat", json={
            "message": "你好"
        })
        assert response.status_code == 422
    
    def test_chat_missing_message(self, client):
        """测试缺少 message"""
        response = client.post("/api/v1/chat", json={
            "session_id": "test-session-001"
        })
        assert response.status_code == 422
    
    def test_clear_session(self, client):
        """测试清除会话"""
        response = client.delete("/api/v1/chat/test-session-001")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestAPIResponseFormat:
    """API 响应格式一致性测试"""
    
    def test_success_response_has_required_fields(self, client):
        """测试成功响应包含必需字段"""
        response = client.post("/api/v1/calc/loan", json={
            "price": 1000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        })
        data = response.json()
        
        # 验证响应格式
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert data["code"] == 0
        assert data["message"] == "success"
    
    def test_error_response_has_required_fields(self, client):
        """测试错误响应包含必需字段"""
        response = client.post("/api/v1/calc/loan", json={
            "price": -1000,  # 无效
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        })
        data = response.json()
        
        # 验证响应格式
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert data["code"] != 0


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
