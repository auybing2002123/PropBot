# -*- coding: utf-8 -*-
"""
综合报告生成工具
整合财务分析、市场分析、政策信息，生成结构化的购房分析报告
"""

from typing import Optional
from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import register_tool
from app.utils.logger import get_logger

logger = get_logger(__name__)


@register_tool
class GenerateReportTool(BaseTool):
    """综合购房分析报告生成工具"""
    
    name = "generate_report"
    description = "生成综合购房分析报告，整合财务、市场、政策等多维度分析"
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="目标城市",
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="district",
            type="string",
            description="目标区域",
            required=False
        ),
        ToolParameter(
            name="budget",
            type="number",
            description="预算（元）"
        ),
        ToolParameter(
            name="loan_years",
            type="integer",
            description="贷款年限"
        ),
        ToolParameter(
            name="is_first_home",
            type="boolean",
            description="是否首套房"
        ),
        ToolParameter(
            name="monthly_income",
            type="number",
            description="家庭月收入（元）",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行报告生成
        
        Args:
            city: 目标城市
            district: 目标区域（可选）
            budget: 预算（元）
            loan_years: 贷款年限
            is_first_home: 是否首套房
            monthly_income: 家庭月收入（可选）
        
        Returns:
            综合分析报告
        """
        self.validate_params(**kwargs)
        
        city = kwargs["city"]
        district = kwargs.get("district")
        budget = kwargs["budget"]
        loan_years = kwargs["loan_years"]
        is_first_home = kwargs["is_first_home"]
        monthly_income = kwargs.get("monthly_income")
        
        # 各维度分析
        financial = self._analyze_financial(budget, loan_years, is_first_home, monthly_income)
        market = await self._analyze_market(city, district, budget)
        policy = self._summarize_policy(city, is_first_home)
        risks = self._identify_risks(financial, market, monthly_income)
        recommendations = self._generate_recommendations(financial, market)
        next_steps = self._generate_next_steps(city, district)
        summary = self._generate_summary(city, district, budget, financial, market)
        
        return {
            "summary": summary,
            "city": city,
            "district": district,
            "budget": budget,
            "financial_analysis": financial,
            "market_analysis": market,
            "policy_summary": policy,
            "risk_factors": risks,
            "recommendations": recommendations,
            "next_steps": next_steps
        }

    def _analyze_financial(
        self,
        budget: float,
        loan_years: int,
        is_first_home: bool,
        monthly_income: Optional[float]
    ) -> dict:
        """财务分析"""
        # 首付比例：首套20%，二套30%
        down_ratio = 0.2 if is_first_home else 0.3
        down_payment = budget * down_ratio
        loan_amount = budget - down_payment
        
        # 贷款利率：首套3.5%，二套3.9%
        rate = 3.5 if is_first_home else 3.9
        monthly_rate = rate / 100 / 12
        months = loan_years * 12
        
        # 等额本息月供计算
        if monthly_rate > 0:
            power = (1 + monthly_rate) ** months
            monthly_payment = loan_amount * monthly_rate * power / (power - 1)
        else:
            monthly_payment = loan_amount / months
        
        total_interest = monthly_payment * months - loan_amount
        
        # 还款压力评估
        pressure_level = "未知"
        pressure_ratio = None
        if monthly_income and monthly_income > 0:
            pressure_ratio = monthly_payment / monthly_income
            if pressure_ratio <= 0.3:
                pressure_level = "低"
            elif pressure_ratio <= 0.5:
                pressure_level = "中"
            else:
                pressure_level = "高"
        
        return {
            "budget": round(budget, 2),
            "down_payment": round(down_payment, 2),
            "down_payment_ratio": f"{int(down_ratio * 100)}%",
            "loan_amount": round(loan_amount, 2),
            "rate": rate,
            "rate_display": f"{rate}%",
            "loan_years": loan_years,
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(loan_amount + total_interest, 2),
            "pressure_level": pressure_level,
            "pressure_ratio": round(pressure_ratio * 100, 1) if pressure_ratio else None,
            "pressure_ratio_display": f"{round(pressure_ratio * 100, 1)}%" if pressure_ratio else "未提供收入"
        }

    async def _analyze_market(
        self,
        city: str,
        district: Optional[str],
        budget: float
    ) -> dict:
        """市场分析"""
        from app.agent.tools.registry import tool_registry
        
        # 尝试调用市场查询工具
        market_tool = tool_registry.get("query_market")
        market_data = {}
        
        if market_tool:
            try:
                result = await market_tool.execute(city=city, district=district)
                market_data = result
            except Exception as e:
                logger.warning(f"获取市场数据失败: {e}")
        
        # 计算可购面积
        avg_price = market_data.get("avg_price", 10000)
        affordable_area = budget / avg_price if avg_price > 0 else 0
        
        # 市场趋势判断
        price_change = market_data.get("price_change_yoy", 0)
        if price_change > 5:
            trend = "上涨"
            trend_advice = "市场处于上升期，建议尽早决策"
        elif price_change < -5:
            trend = "下跌"
            trend_advice = "市场处于调整期，可适当观望或议价"
        else:
            trend = "平稳"
            trend_advice = "市场相对稳定，可从容选择"
        
        return {
            "city": city,
            "district": district,
            "avg_price": avg_price,
            "avg_price_display": f"{avg_price}元/㎡",
            "affordable_area": round(affordable_area, 1),
            "affordable_area_display": f"约{round(affordable_area, 0)}㎡",
            "trend": trend,
            "trend_advice": trend_advice,
            "price_change_yoy": price_change
        }

    def _summarize_policy(self, city: str, is_first_home: bool) -> dict:
        """政策摘要"""
        home_type = "首套房" if is_first_home else "二套房"
        down_ratio = "20%" if is_first_home else "30%"
        
        policy_points = [
            f"{city}目前无限购政策，外地户籍可购房",
            f"{home_type}最低首付比例：{down_ratio}",
            "公积金贷款额度：双职工最高80万，单职工最高50万",
            "契税优惠：首套90㎡以下1%，90㎡以上1.5%"
        ]
        
        if is_first_home:
            policy_points.append("首套房贷款利率可享受优惠")
        
        return {
            "city": city,
            "is_first_home": is_first_home,
            "home_type": home_type,
            "down_payment_ratio": down_ratio,
            "policy_points": policy_points
        }

    def _identify_risks(
        self,
        financial: dict,
        market: dict,
        monthly_income: Optional[float]
    ) -> list:
        """风险识别"""
        risks = []
        
        # 还款压力风险
        pressure_level = financial.get("pressure_level")
        if pressure_level == "高":
            risks.append("月供占收入比例过高，还款压力较大，建议降低预算或延长贷款年限")
        elif pressure_level == "中":
            risks.append("月供占收入比例适中，需注意控制其他支出")
        
        # 市场风险
        trend = market.get("trend")
        if trend == "下跌":
            risks.append("当前市场处于下行周期，房产可能面临短期贬值风险")
        
        # 收入信息缺失
        if not monthly_income:
            risks.append("未提供收入信息，无法准确评估还款能力")
        
        # 无明显风险
        if not risks:
            risks.append("暂未发现明显风险因素")
        
        return risks

    def _generate_recommendations(self, financial: dict, market: dict) -> list:
        """生成建议"""
        recommendations = []
        
        # 基于财务状况的建议
        pressure_level = financial.get("pressure_level")
        if pressure_level == "高":
            recommendations.append("建议适当降低购房预算，或考虑延长贷款年限以降低月供")
            recommendations.append("可考虑增加首付比例，减少贷款金额")
        elif pressure_level == "低":
            recommendations.append("财务状况良好，可考虑适当提高预算以获得更好的房源")
        else:
            recommendations.append("建议保持当前预算范围，量力而行")
        
        # 基于市场状况的建议
        trend = market.get("trend")
        if trend == "上涨":
            recommendations.append("市场上行期，如有合适房源建议尽早决策")
        elif trend == "下跌":
            recommendations.append("市场调整期，可多看多比较，适当议价")
        else:
            recommendations.append("市场平稳，可从容选择，不必过于着急")
        
        # 通用建议
        recommendations.append("建议实地看房，了解小区环境和配套设施")
        recommendations.append("购房前建议咨询专业人士，了解最新政策")
        
        return recommendations

    def _generate_next_steps(self, city: str, district: Optional[str]) -> list:
        """生成下一步行动建议"""
        location = district if district else city
        
        return [
            "1. 确认购房资格：准备身份证、户口本、婚姻证明等材料",
            "2. 准备首付资金：确保首付款和税费资金到位",
            f"3. 实地看房：前往{location}实地考察意向楼盘",
            "4. 对比选择：从位置、价格、户型、配套等多维度对比",
            "5. 选择贷款银行：比较各银行利率和服务，选择最优方案",
            "6. 签约购房：仔细阅读合同条款，确认无误后签约",
            "7. 办理贷款：提交贷款申请，等待银行审批",
            "8. 缴纳税费：办理契税、维修基金等相关税费",
            "9. 办理过户：完成产权过户登记",
            "10. 收房验房：验收房屋质量，办理入住手续"
        ]

    def _generate_summary(
        self,
        city: str,
        district: Optional[str],
        budget: float,
        financial: dict,
        market: dict
    ) -> str:
        """生成总结"""
        location = f"{city}{district}" if district else city
        area = market.get("affordable_area", 0)
        monthly_payment = financial.get("monthly_payment", 0)
        pressure_level = financial.get("pressure_level", "未知")
        
        budget_wan = budget / 10000
        
        summary = (
            f"在{location}，预算{budget_wan:.0f}万元，"
            f"按当前均价可购买约{area:.0f}平方米的房产。"
            f"贷款{financial.get('loan_years')}年，月供约{monthly_payment:.0f}元，"
            f"还款压力{pressure_level}。"
        )
        
        trend = market.get("trend", "平稳")
        if trend == "上涨":
            summary += "当前市场处于上升期，建议尽早决策。"
        elif trend == "下跌":
            summary += "当前市场处于调整期，可适当观望。"
        else:
            summary += "当前市场相对平稳，可从容选择。"
        
        return summary
