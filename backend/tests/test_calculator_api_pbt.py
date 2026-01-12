"""
计算器 API 属性测试
使用 hypothesis 进行属性测试

Property 11: API 响应格式一致性
Property 12: 参数验证错误格式
验证: 需求 10.5, 11.4
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ==================== 数据生成策略 ====================

# 有效的贷款计算参数
valid_loan_params = st.fixed_dictionaries({
    "price": st.floats(min_value=100000, max_value=50000000, allow_nan=False, allow_infinity=False),
    "down_payment_ratio": st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
    "years": st.integers(min_value=1, max_value=30),
    "rate": st.floats(min_value=0, max_value=20, allow_nan=False, allow_infinity=False),
    "method": st.sampled_from(["equal_payment", "equal_principal"])
})

# 有效的税费计算参数
valid_tax_params = st.fixed_dictionaries({
    "price": st.floats(min_value=100000, max_value=50000000, allow_nan=False, allow_infinity=False),
    "area": st.floats(min_value=10, max_value=1000, allow_nan=False, allow_infinity=False),
    "is_first_home": st.booleans(),
    "house_age_years": st.integers(min_value=0, max_value=50)
})

# 有效的总成本计算参数
valid_total_cost_params = st.fixed_dictionaries({
    "price": st.floats(min_value=100000, max_value=50000000, allow_nan=False, allow_infinity=False),
    "down_payment": st.floats(min_value=0, max_value=50000000, allow_nan=False, allow_infinity=False),
    "total_interest": st.floats(min_value=0, max_value=50000000, allow_nan=False, allow_infinity=False),
    "taxes": st.floats(min_value=0, max_value=5000000, allow_nan=False, allow_infinity=False)
})

# 无效参数策略（用于测试验证错误）
invalid_price_params = st.fixed_dictionaries({
    "price": st.floats(max_value=0, allow_nan=False, allow_infinity=False),  # 无效价格
    "down_payment_ratio": st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
    "years": st.integers(min_value=1, max_value=30),
    "rate": st.floats(min_value=0, max_value=20, allow_nan=False, allow_infinity=False)
})


# ==================== Property 11: API 响应格式一致性 ====================

class TestProperty11ResponseFormatConsistency:
    """
    Property 11: API 响应格式一致性
    
    *对于任意* Calculator_API 调用（成功或失败），响应应包含 code、message、data 三个字段。
    **验证: 需求 10.5**
    """
    
    @given(params=valid_loan_params)
    @settings(max_examples=100)
    def test_loan_api_response_format(self, params):
        """
        Feature: agent-core, Property 11: API 响应格式一致性
        对于任意有效的贷款计算参数，响应应包含 code、message、data 三个字段
        """
        response = client.post("/api/v1/calc/loan", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "响应缺少 code 字段"
        assert "message" in data, "响应缺少 message 字段"
        assert "data" in data, "响应缺少 data 字段"
        
        # 验证成功响应的格式
        assert data["code"] == 0, f"成功响应的 code 应为 0，实际为 {data['code']}"
        assert data["message"] == "success", f"成功响应的 message 应为 'success'，实际为 {data['message']}"
        assert data["data"] is not None, "成功响应的 data 不应为 None"
    
    @given(params=valid_tax_params)
    @settings(max_examples=100)
    def test_tax_api_response_format(self, params):
        """
        Feature: agent-core, Property 11: API 响应格式一致性
        对于任意有效的税费计算参数，响应应包含 code、message、data 三个字段
        """
        response = client.post("/api/v1/calc/tax", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "响应缺少 code 字段"
        assert "message" in data, "响应缺少 message 字段"
        assert "data" in data, "响应缺少 data 字段"
        
        # 验证成功响应的格式
        assert data["code"] == 0
        assert data["message"] == "success"
        assert data["data"] is not None
    
    @given(params=valid_total_cost_params)
    @settings(max_examples=100)
    def test_total_cost_api_response_format(self, params):
        """
        Feature: agent-core, Property 11: API 响应格式一致性
        对于任意有效的总成本计算参数，响应应包含 code、message、data 三个字段
        """
        response = client.post("/api/v1/calc/total_cost", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "响应缺少 code 字段"
        assert "message" in data, "响应缺少 message 字段"
        assert "data" in data, "响应缺少 data 字段"
        
        # 验证成功响应的格式
        assert data["code"] == 0
        assert data["message"] == "success"
        assert data["data"] is not None


# ==================== Property 12: 参数验证错误格式 ====================

class TestProperty12ValidationErrorFormat:
    """
    Property 12: 参数验证错误格式
    
    *对于任意* 缺少必需参数的 API 请求，响应应包含非零 code 和说明缺失字段的 message。
    **验证: 需求 11.4**
    """
    
    @given(params=invalid_price_params)
    @settings(max_examples=100)
    def test_invalid_price_error_format(self, params):
        """
        Feature: agent-core, Property 12: 参数验证错误格式
        对于任意无效价格参数，响应应包含非零 code 和说明错误的 message
        """
        response = client.post("/api/v1/calc/loan", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "错误响应缺少 code 字段"
        assert "message" in data, "错误响应缺少 message 字段"
        assert "data" in data, "错误响应缺少 data 字段"
        
        # 验证错误响应的格式
        assert data["code"] != 0, "错误响应的 code 应为非零"
        assert len(data["message"]) > 0, "错误响应的 message 不应为空"
        assert "参数" in data["message"] or "price" in data["message"].lower(), \
            f"错误消息应说明参数问题，实际为: {data['message']}"
    
    @given(missing_field=st.sampled_from(["price", "down_payment_ratio", "years", "rate"]))
    @settings(max_examples=100)
    def test_missing_required_field_error_format(self, missing_field):
        """
        Feature: agent-core, Property 12: 参数验证错误格式
        对于任意缺少必需字段的请求，响应应包含非零 code 和说明缺失字段的 message
        """
        # 构建缺少某个必需字段的参数
        params = {
            "price": 2000000,
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        }
        del params[missing_field]
        
        response = client.post("/api/v1/calc/loan", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "错误响应缺少 code 字段"
        assert "message" in data, "错误响应缺少 message 字段"
        assert "data" in data, "错误响应缺少 data 字段"
        
        # 验证错误响应的格式
        assert data["code"] != 0, "错误响应的 code 应为非零"
        assert len(data["message"]) > 0, "错误响应的 message 不应为空"
    
    @given(invalid_type=st.sampled_from(["string", [], {}, None]))
    @settings(max_examples=100)
    def test_invalid_type_error_format(self, invalid_type):
        """
        Feature: agent-core, Property 12: 参数验证错误格式
        对于任意类型错误的参数，响应应包含非零 code 和说明错误的 message
        """
        params = {
            "price": invalid_type,  # 类型错误
            "down_payment_ratio": 0.3,
            "years": 30,
            "rate": 4.2
        }
        
        response = client.post("/api/v1/calc/loan", json=params)
        data = response.json()
        
        # 验证响应包含必需字段
        assert "code" in data, "错误响应缺少 code 字段"
        assert "message" in data, "错误响应缺少 message 字段"
        assert "data" in data, "错误响应缺少 data 字段"
        
        # 验证错误响应的格式
        assert data["code"] != 0, "错误响应的 code 应为非零"
