# 财务计算工具属性测试
# Property 4: 贷款计算数学正确性
# Property 5: 税费计算规则正确性
# Property 6: 总成本汇总正确性
# Property 7: 还款压力等级划分
# 验证: 需求 3.1, 3.3, 3.4, 3.5

import pytest
from hypothesis import given, strategies as st, settings, assume
import math
import asyncio

from app.agent.tools.financial import (
    CalcLoanTool,
    CalcTaxTool,
    CalcTotalCostTool,
    AssessPressureTool
)


# ============================================================
# 数据生成策略
# ============================================================

# 有效的房价范围（10万 - 5000万）
price_strategy = st.floats(min_value=100000, max_value=50000000, allow_nan=False, allow_infinity=False)

# 有效的首付比例（10% - 90%）
down_payment_ratio_strategy = st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False)

# 有效的贷款年限（1 - 30年）
years_strategy = st.integers(min_value=1, max_value=30)

# 有效的年利率（0.1% - 20%，避免零利率的特殊情况）
rate_strategy = st.floats(min_value=0.1, max_value=20, allow_nan=False, allow_infinity=False)

# 有效的面积（10 - 1000 平方米）
area_strategy = st.floats(min_value=10, max_value=1000, allow_nan=False, allow_infinity=False)

# 房龄（0 - 50年）
house_age_strategy = st.integers(min_value=0, max_value=50)

# 月收入（1000 - 1000000）
monthly_income_strategy = st.floats(min_value=1000, max_value=1000000, allow_nan=False, allow_infinity=False)

# 月供（100 - 500000）
monthly_payment_strategy = st.floats(min_value=100, max_value=500000, allow_nan=False, allow_infinity=False)


# ============================================================
# Property 4: 贷款计算数学正确性
# 验证: 需求 3.1
# ============================================================

class TestProperty4LoanCalculation:
    """
    Property 4: 贷款计算数学正确性
    
    *对于任意* 有效的贷款参数（房价、首付比例、年限、利率），等额本息月供计算应满足公式：
    月供 = 贷款金额 × 月利率 × (1+月利率)^月数 / ((1+月利率)^月数 - 1)
    
    **验证: 需求 3.1**
    """
    
    @given(
        price=price_strategy,
        down_payment_ratio=down_payment_ratio_strategy,
        years=years_strategy,
        rate=rate_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_equal_payment_formula(self, price, down_payment_ratio, years, rate):
        """
        **Feature: agent-core, Property 4: 贷款计算数学正确性**
        **Validates: Requirements 3.1**
        
        对于任意有效的贷款参数，等额本息月供应满足标准公式
        """
        # 创建工具实例
        loan_tool = CalcLoanTool()
        
        # 执行贷款计算
        result = asyncio.get_event_loop().run_until_complete(
            loan_tool.execute(
                price=price,
                down_payment_ratio=down_payment_ratio,
                years=years,
                rate=rate,
                method="equal_payment"
            )
        )
        
        # 计算预期值
        loan_amount = price * (1 - down_payment_ratio)
        monthly_rate = rate / 100 / 12
        months = years * 12
        
        # 使用标准公式计算预期月供
        power = (1 + monthly_rate) ** months
        expected_monthly = loan_amount * monthly_rate * power / (power - 1)
        
        # 验证月供（允许 0.01 元误差，因为四舍五入）
        assert abs(result["monthly_payment"] - round(expected_monthly, 2)) < 0.02, \
            f"月供计算不正确: 预期 {round(expected_monthly, 2)}, 实际 {result['monthly_payment']}"
        
        # 验证首付金额
        expected_down_payment = price * down_payment_ratio
        assert abs(result["down_payment"] - round(expected_down_payment, 2)) < 0.02, \
            f"首付计算不正确: 预期 {round(expected_down_payment, 2)}, 实际 {result['down_payment']}"
        
        # 验证贷款金额
        assert abs(result["loan_amount"] - round(loan_amount, 2)) < 0.02, \
            f"贷款金额计算不正确: 预期 {round(loan_amount, 2)}, 实际 {result['loan_amount']}"
    
    @given(
        price=price_strategy,
        down_payment_ratio=down_payment_ratio_strategy,
        years=years_strategy,
        rate=rate_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_total_interest_consistency(self, price, down_payment_ratio, years, rate):
        """
        **Feature: agent-core, Property 4: 贷款计算数学正确性**
        **Validates: Requirements 3.1**
        
        对于任意贷款参数，总利息 = 还款总额 - 贷款金额
        """
        loan_tool = CalcLoanTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            loan_tool.execute(
                price=price,
                down_payment_ratio=down_payment_ratio,
                years=years,
                rate=rate,
                method="equal_payment"
            )
        )
        
        # 验证总利息 = 还款总额 - 贷款金额
        expected_interest = result["total_payment"] - result["loan_amount"]
        assert abs(result["total_interest"] - expected_interest) < 0.02, \
            f"总利息计算不一致: 预期 {expected_interest}, 实际 {result['total_interest']}"


# ============================================================
# Property 5: 税费计算规则正确性
# 验证: 需求 3.3
# ============================================================

class TestProperty5TaxCalculation:
    """
    Property 5: 税费计算规则正确性
    
    *对于任意* 有效的房产参数，契税计算应满足：
    - 首套且面积≤90㎡：房价 × 1%
    - 首套且面积>90㎡：房价 × 1.5%
    - 二套且面积≤90㎡：房价 × 1%
    - 二套且面积>90㎡：房价 × 2%
    
    **验证: 需求 3.3**
    """
    
    @given(
        price=price_strategy,
        area=st.floats(min_value=10, max_value=90, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_deed_tax_first_home_small_area(self, price, area):
        """
        **Feature: agent-core, Property 5: 税费计算规则正确性**
        **Validates: Requirements 3.3**
        
        首套且面积≤90㎡：契税 = 房价 × 1%
        """
        tax_tool = CalcTaxTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            tax_tool.execute(
                price=price,
                area=area,
                is_first_home=True,
                house_age_years=0
            )
        )
        
        expected_deed_tax = price * 0.01
        assert abs(result["deed_tax"] - round(expected_deed_tax, 2)) < 0.02, \
            f"首套小面积契税计算错误: 预期 {round(expected_deed_tax, 2)}, 实际 {result['deed_tax']}"
        assert result["deed_tax_rate"] == 0.01, \
            f"契税税率应为 1%, 实际 {result['deed_tax_rate']}"
    
    @given(
        price=price_strategy,
        area=st.floats(min_value=90.01, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_deed_tax_first_home_large_area(self, price, area):
        """
        **Feature: agent-core, Property 5: 税费计算规则正确性**
        **Validates: Requirements 3.3**
        
        首套且面积>90㎡：契税 = 房价 × 1.5%
        """
        tax_tool = CalcTaxTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            tax_tool.execute(
                price=price,
                area=area,
                is_first_home=True,
                house_age_years=0
            )
        )
        
        expected_deed_tax = price * 0.015
        assert abs(result["deed_tax"] - round(expected_deed_tax, 2)) < 0.02, \
            f"首套大面积契税计算错误: 预期 {round(expected_deed_tax, 2)}, 实际 {result['deed_tax']}"
        assert result["deed_tax_rate"] == 0.015, \
            f"契税税率应为 1.5%, 实际 {result['deed_tax_rate']}"
    
    @given(
        price=price_strategy,
        area=st.floats(min_value=10, max_value=90, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_deed_tax_second_home_small_area(self, price, area):
        """
        **Feature: agent-core, Property 5: 税费计算规则正确性**
        **Validates: Requirements 3.3**
        
        二套且面积≤90㎡：契税 = 房价 × 1%
        """
        tax_tool = CalcTaxTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            tax_tool.execute(
                price=price,
                area=area,
                is_first_home=False,
                house_age_years=0
            )
        )
        
        expected_deed_tax = price * 0.01
        assert abs(result["deed_tax"] - round(expected_deed_tax, 2)) < 0.02, \
            f"二套小面积契税计算错误: 预期 {round(expected_deed_tax, 2)}, 实际 {result['deed_tax']}"
        assert result["deed_tax_rate"] == 0.01, \
            f"契税税率应为 1%, 实际 {result['deed_tax_rate']}"
    
    @given(
        price=price_strategy,
        area=st.floats(min_value=90.01, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_deed_tax_second_home_large_area(self, price, area):
        """
        **Feature: agent-core, Property 5: 税费计算规则正确性**
        **Validates: Requirements 3.3**
        
        二套且面积>90㎡：契税 = 房价 × 2%
        """
        tax_tool = CalcTaxTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            tax_tool.execute(
                price=price,
                area=area,
                is_first_home=False,
                house_age_years=0
            )
        )
        
        expected_deed_tax = price * 0.02
        assert abs(result["deed_tax"] - round(expected_deed_tax, 2)) < 0.02, \
            f"二套大面积契税计算错误: 预期 {round(expected_deed_tax, 2)}, 实际 {result['deed_tax']}"
        assert result["deed_tax_rate"] == 0.02, \
            f"契税税率应为 2%, 实际 {result['deed_tax_rate']}"


# ============================================================
# Property 6: 总成本汇总正确性
# 验证: 需求 3.4
# ============================================================

class TestProperty6TotalCostCalculation:
    """
    Property 6: 总成本汇总正确性
    
    *对于任意* 购房成本组成（首付、贷款利息、税费、其他费用），总成本应等于各项之和。
    
    **验证: 需求 3.4**
    """
    
    @given(
        price=price_strategy,
        down_payment=st.floats(min_value=10000, max_value=10000000, allow_nan=False, allow_infinity=False),
        total_interest=st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False),
        taxes=st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
        decoration=st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
        furniture=st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False),
        other_fees=st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_total_cost_sum(
        self, price, down_payment, total_interest, 
        taxes, decoration, furniture, other_fees
    ):
        """
        **Feature: agent-core, Property 6: 总成本汇总正确性**
        **Validates: Requirements 3.4**
        
        对于任意购房成本组成，总成本 = 房价 + 贷款利息 + 税费 + 装修 + 家具 + 其他
        """
        # 确保首付不超过房价
        assume(down_payment <= price)
        
        total_cost_tool = CalcTotalCostTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            total_cost_tool.execute(
                price=price,
                down_payment=down_payment,
                total_interest=total_interest,
                taxes=taxes,
                decoration=decoration,
                furniture=furniture,
                other_fees=other_fees
            )
        )
        
        # 计算预期总成本
        expected_total = price + total_interest + taxes + decoration + furniture + other_fees
        
        # 验证总成本
        assert abs(result["total_cost"] - round(expected_total, 2)) < 0.02, \
            f"总成本计算错误: 预期 {round(expected_total, 2)}, 实际 {result['total_cost']}"
    
    @given(
        price=price_strategy,
        down_payment=st.floats(min_value=10000, max_value=10000000, allow_nan=False, allow_infinity=False),
        total_interest=st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False),
        taxes=st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
        decoration=st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
        furniture=st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False),
        other_fees=st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_initial_cost_sum(
        self, price, down_payment, total_interest,
        taxes, decoration, furniture, other_fees
    ):
        """
        **Feature: agent-core, Property 6: 总成本汇总正确性**
        **Validates: Requirements 3.4**
        
        对于任意购房成本组成，初期投入 = 首付 + 税费 + 装修 + 家具 + 其他
        """
        assume(down_payment <= price)
        
        total_cost_tool = CalcTotalCostTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            total_cost_tool.execute(
                price=price,
                down_payment=down_payment,
                total_interest=total_interest,
                taxes=taxes,
                decoration=decoration,
                furniture=furniture,
                other_fees=other_fees
            )
        )
        
        # 计算预期初期投入
        expected_initial = down_payment + taxes + decoration + furniture + other_fees
        
        # 验证初期投入
        assert abs(result["initial_cost"] - round(expected_initial, 2)) < 0.02, \
            f"初期投入计算错误: 预期 {round(expected_initial, 2)}, 实际 {result['initial_cost']}"


# ============================================================
# Property 7: 还款压力等级划分
# 验证: 需求 3.5
# ============================================================

class TestProperty7PressureAssessment:
    """
    Property 7: 还款压力等级划分
    
    *对于任意* 月供和收入，压力等级应满足：
    - 月供/收入 ≤ 30%：低压力
    - 30% < 月供/收入 ≤ 50%：中压力
    - 月供/收入 > 50%：高压力
    
    **验证: 需求 3.5**
    """
    
    @given(
        monthly_income=monthly_income_strategy,
        ratio=st.floats(min_value=0.01, max_value=0.30, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_low_pressure_level(self, monthly_income, ratio):
        """
        **Feature: agent-core, Property 7: 还款压力等级划分**
        **Validates: Requirements 3.5**
        
        月供/收入 ≤ 30%：应返回低压力等级
        """
        monthly_payment = monthly_income * ratio
        pressure_tool = AssessPressureTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            pressure_tool.execute(
                monthly_payment=monthly_payment,
                monthly_income=monthly_income
            )
        )
        
        assert result["level"] == "low", \
            f"月供占比 {ratio*100:.1f}% 应为低压力，实际为 {result['level']}"
        assert result["level_name"] == "低", \
            f"压力等级名称应为 '低'，实际为 {result['level_name']}"
    
    @given(
        monthly_income=monthly_income_strategy,
        ratio=st.floats(min_value=0.31, max_value=0.50, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_medium_pressure_level(self, monthly_income, ratio):
        """
        **Feature: agent-core, Property 7: 还款压力等级划分**
        **Validates: Requirements 3.5**
        
        30% < 月供/收入 ≤ 50%：应返回中压力等级
        """
        monthly_payment = monthly_income * ratio
        pressure_tool = AssessPressureTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            pressure_tool.execute(
                monthly_payment=monthly_payment,
                monthly_income=monthly_income
            )
        )
        
        assert result["level"] == "medium", \
            f"月供占比 {ratio*100:.1f}% 应为中压力，实际为 {result['level']}"
        assert result["level_name"] == "中", \
            f"压力等级名称应为 '中'，实际为 {result['level_name']}"
    
    @given(
        monthly_income=monthly_income_strategy,
        ratio=st.floats(min_value=0.51, max_value=0.99, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_high_pressure_level(self, monthly_income, ratio):
        """
        **Feature: agent-core, Property 7: 还款压力等级划分**
        **Validates: Requirements 3.5**
        
        月供/收入 > 50%：应返回高压力等级
        """
        monthly_payment = monthly_income * ratio
        pressure_tool = AssessPressureTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            pressure_tool.execute(
                monthly_payment=monthly_payment,
                monthly_income=monthly_income
            )
        )
        
        assert result["level"] == "high", \
            f"月供占比 {ratio*100:.1f}% 应为高压力，实际为 {result['level']}"
        assert result["level_name"] == "高", \
            f"压力等级名称应为 '高'，实际为 {result['level_name']}"
    
    @given(
        monthly_payment=monthly_payment_strategy,
        monthly_income=monthly_income_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_payment_ratio_calculation(self, monthly_payment, monthly_income):
        """
        **Feature: agent-core, Property 7: 还款压力等级划分**
        **Validates: Requirements 3.5**
        
        对于任意月供和收入，月供收入比应正确计算
        """
        pressure_tool = AssessPressureTool()
        
        result = asyncio.get_event_loop().run_until_complete(
            pressure_tool.execute(
                monthly_payment=monthly_payment,
                monthly_income=monthly_income
            )
        )
        
        expected_ratio = (monthly_payment / monthly_income) * 100
        
        # 验证月供收入比（允许 0.1% 误差）
        assert abs(result["payment_ratio"] - round(expected_ratio, 1)) < 0.2, \
            f"月供收入比计算错误: 预期 {round(expected_ratio, 1)}%, 实际 {result['payment_ratio']}%"
