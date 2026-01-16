# 财务计算工具
# 包含贷款计算、税费计算、总成本计算、还款压力评估

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import register_tool
from app.data.loader import get_data_loader


@register_tool
class CalcLoanTool(BaseTool):
    """贷款计算工具"""
    
    name = "calc_loan"
    description = "计算房贷，支持等额本息和等额本金两种还款方式，返回首付、贷款金额、月供、总利息等信息"
    parameters = [
        ToolParameter(
            name="price",
            type="number",
            description="房屋总价（元）"
        ),
        ToolParameter(
            name="down_payment_ratio",
            type="number",
            description="首付比例，如 0.3 表示 30%"
        ),
        ToolParameter(
            name="years",
            type="integer",
            description="贷款年限（年）"
        ),
        ToolParameter(
            name="rate",
            type="number",
            description="年利率（%），如 4.2 表示 4.2%"
        ),
        ToolParameter(
            name="method",
            type="string",
            description="还款方式",
            required=False,
            enum=["equal_payment", "equal_principal"]
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行贷款计算
        
        Args:
            price: 房屋总价（元）
            down_payment_ratio: 首付比例
            years: 贷款年限
            rate: 年利率（%）
            method: 还款方式，equal_payment=等额本息，equal_principal=等额本金
            
        Returns:
            计算结果字典
        """
        self.validate_params(**kwargs)
        
        price = kwargs["price"]
        down_payment_ratio = kwargs["down_payment_ratio"]
        years = kwargs["years"]
        rate = kwargs["rate"]
        method = kwargs.get("method", "equal_payment")
        
        # 计算基础数据
        down_payment = price * down_payment_ratio  # 首付金额
        loan_amount = price - down_payment  # 贷款金额
        monthly_rate = rate / 100 / 12  # 月利率
        months = years * 12  # 还款月数
        
        if method == "equal_payment":
            # 等额本息：月供 = 贷款金额 × 月利率 × (1+月利率)^月数 / ((1+月利率)^月数 - 1)
            result = self._calc_equal_payment(loan_amount, monthly_rate, months)
        else:
            # 等额本金
            result = self._calc_equal_principal(loan_amount, monthly_rate, months)
        
        return {
            "down_payment": round(down_payment, 2),
            "loan_amount": round(loan_amount, 2),
            "monthly_payment": round(result["monthly_payment"], 2),
            "first_month_payment": round(result.get("first_month_payment", result["monthly_payment"]), 2),
            "last_month_payment": round(result.get("last_month_payment", result["monthly_payment"]), 2),
            "total_payment": round(result["total_payment"], 2),
            "total_interest": round(result["total_interest"], 2),
            "method": method,
            "method_name": "等额本息" if method == "equal_payment" else "等额本金"
        }
    
    def _calc_equal_payment(self, loan_amount: float, monthly_rate: float, months: int) -> dict:
        """
        等额本息计算
        月供固定，前期利息多本金少，后期本金多利息少
        """
        # 处理零利率或极小利率情况（避免除零错误）
        # 当利率极小时，(1+r)^n ≈ 1，导致 power - 1 ≈ 0
        if monthly_rate < 1e-10:
            # 零利率或极小利率情况，按无息贷款处理
            monthly_payment = loan_amount / months
            return {
                "monthly_payment": monthly_payment,
                "total_payment": loan_amount,
                "total_interest": 0
            }
        
        # 月供 = P × r × (1+r)^n / ((1+r)^n - 1)
        # P = 贷款金额, r = 月利率, n = 月数
        power = (1 + monthly_rate) ** months
        
        # 再次检查 power - 1 是否接近零（防止浮点精度问题）
        if abs(power - 1) < 1e-10:
            monthly_payment = loan_amount / months
            return {
                "monthly_payment": monthly_payment,
                "total_payment": loan_amount,
                "total_interest": 0
            }
        
        monthly_payment = loan_amount * monthly_rate * power / (power - 1)
        total_payment = monthly_payment * months
        total_interest = total_payment - loan_amount
        
        return {
            "monthly_payment": monthly_payment,
            "total_payment": total_payment,
            "total_interest": total_interest
        }
    
    def _calc_equal_principal(self, loan_amount: float, monthly_rate: float, months: int) -> dict:
        """
        等额本金计算
        每月本金固定，利息递减，月供逐月减少
        """
        # 每月本金 = 贷款金额 / 月数
        monthly_principal = loan_amount / months
        
        # 首月月供 = 每月本金 + 贷款金额 × 月利率
        first_month_payment = monthly_principal + loan_amount * monthly_rate
        
        # 末月月供 = 每月本金 + 每月本金 × 月利率
        last_month_payment = monthly_principal + monthly_principal * monthly_rate
        
        # 总利息 = (月数 + 1) × 贷款金额 × 月利率 / 2
        total_interest = (months + 1) * loan_amount * monthly_rate / 2
        total_payment = loan_amount + total_interest
        
        # 平均月供（用于展示）
        avg_monthly_payment = total_payment / months
        
        return {
            "monthly_payment": avg_monthly_payment,
            "first_month_payment": first_month_payment,
            "last_month_payment": last_month_payment,
            "total_payment": total_payment,
            "total_interest": total_interest
        }



@register_tool
class CalcTaxTool(BaseTool):
    """税费计算工具"""
    
    name = "calc_tax"
    description = "计算购房税费，包括契税、增值税、个税、中介费等"
    parameters = [
        ToolParameter(
            name="price",
            type="number",
            description="房屋总价（元）"
        ),
        ToolParameter(
            name="area",
            type="number",
            description="房屋面积（平方米）"
        ),
        ToolParameter(
            name="is_first_home",
            type="boolean",
            description="是否首套房"
        ),
        ToolParameter(
            name="house_age_years",
            type="integer",
            description="房龄（年），新房填 0"
        ),
        ToolParameter(
            name="original_price",
            type="number",
            description="原购买价格（元），用于计算增值税和个税，新房可不填",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行税费计算
        
        Args:
            price: 房屋总价（元）
            area: 房屋面积（平方米）
            is_first_home: 是否首套房
            house_age_years: 房龄（年）
            original_price: 原购买价格（元）
            
        Returns:
            税费计算结果
        """
        self.validate_params(**kwargs)
        
        price = kwargs["price"]
        area = kwargs["area"]
        is_first_home = kwargs["is_first_home"]
        house_age_years = kwargs["house_age_years"]
        original_price = kwargs.get("original_price", price * 0.7)  # 默认按 70% 估算原价
        
        # 从配置文件获取税费规则
        tax_rules = get_data_loader().tax_rules
        
        # 1. 契税计算
        deed_tax = self._calc_deed_tax(price, area, is_first_home, tax_rules.deed_tax)
        
        # 2. 增值税计算（满 2 年免征）
        vat = self._calc_vat(price, original_price, house_age_years, tax_rules.vat)
        
        # 3. 个人所得税计算（满 5 年且唯一免征，这里简化处理）
        income_tax = self._calc_income_tax(price, original_price, house_age_years, is_first_home, tax_rules.income_tax)
        
        # 4. 中介费（从配置读取）
        agent_fee = price * tax_rules.other_fees.agent_fee_rate
        
        # 5. 其他费用（从配置读取）
        other_fees = tax_rules.other_fees.misc_fees
        
        total = deed_tax + vat + income_tax + agent_fee + other_fees
        
        return {
            "deed_tax": round(deed_tax, 2),
            "deed_tax_rate": self._get_deed_tax_rate(area, is_first_home, tax_rules.deed_tax),
            "vat": round(vat, 2),
            "vat_exempt": house_age_years >= 2,
            "income_tax": round(income_tax, 2),
            "income_tax_exempt": house_age_years >= 5 and is_first_home,
            "agent_fee": round(agent_fee, 2),
            "other_fees": round(other_fees, 2),
            "total": round(total, 2)
        }
    
    def _get_deed_tax_rate(self, area: float, is_first_home: bool, deed_tax_config) -> float:
        """获取契税税率（从配置读取）"""
        if is_first_home:
            # 首套房
            if area <= 90:
                return deed_tax_config.first_home_below_90
            else:
                return deed_tax_config.first_home_above_90
        else:
            # 二套房
            if area <= 90:
                return deed_tax_config.second_home_below_90
            else:
                return deed_tax_config.second_home_above_90
    
    def _calc_deed_tax(self, price: float, area: float, is_first_home: bool, deed_tax_config) -> float:
        """
        计算契税（从配置读取税率）
        - 首套且面积≤90㎡：1%
        - 首套且面积>90㎡：1.5%
        - 二套且面积≤90㎡：1%
        - 二套且面积>90㎡：2%
        """
        rate = self._get_deed_tax_rate(area, is_first_home, deed_tax_config)
        return price * rate
    
    def _calc_vat(self, price: float, original_price: float, house_age_years: int, vat_config) -> float:
        """
        计算增值税（从配置读取税率）
        - 满 2 年：免征
        - 不满 2 年：差额 × 5.6%（增值税 5% + 附加税 0.6%）
        """
        if house_age_years >= 2:
            return 0
        
        # 差额计税
        diff = price - original_price
        if diff <= 0:
            return 0
        return diff * vat_config.below_2y
    
    def _calc_income_tax(
        self, 
        price: float, 
        original_price: float, 
        house_age_years: int,
        is_first_home: bool,
        income_tax_config
    ) -> float:
        """
        计算个人所得税（从配置读取税率）
        - 满 5 年且唯一住房：免征
        - 其他情况：差额 × 20% 或 全额 × 1%（取较低者）
        """
        # 满 5 年且唯一（这里用首套近似）
        if house_age_years >= 5 and is_first_home:
            return 0
        
        # 差额计税
        diff = price - original_price
        tax_by_diff = max(0, diff * income_tax_config.diff_rate)
        
        # 全额计税
        tax_by_full = price * income_tax_config.rate
        
        # 取较低者
        return min(tax_by_diff, tax_by_full)



@register_tool
class CalcTotalCostTool(BaseTool):
    """总成本计算工具"""
    
    name = "calc_total_cost"
    description = "计算购房总成本，汇总首付、贷款利息、税费和其他费用"
    parameters = [
        ToolParameter(
            name="price",
            type="number",
            description="房屋总价（元）"
        ),
        ToolParameter(
            name="down_payment",
            type="number",
            description="首付金额（元）"
        ),
        ToolParameter(
            name="total_interest",
            type="number",
            description="贷款总利息（元）"
        ),
        ToolParameter(
            name="taxes",
            type="number",
            description="税费总额（元）"
        ),
        ToolParameter(
            name="decoration",
            type="number",
            description="装修费用（元）",
            required=False
        ),
        ToolParameter(
            name="furniture",
            type="number",
            description="家具家电费用（元）",
            required=False
        ),
        ToolParameter(
            name="other_fees",
            type="number",
            description="其他费用（元）",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行总成本计算
        
        Args:
            price: 房屋总价
            down_payment: 首付金额
            total_interest: 贷款总利息
            taxes: 税费总额
            decoration: 装修费用
            furniture: 家具家电费用
            other_fees: 其他费用
            
        Returns:
            总成本计算结果
        """
        self.validate_params(**kwargs)
        
        price = kwargs["price"]
        down_payment = kwargs["down_payment"]
        total_interest = kwargs["total_interest"]
        taxes = kwargs["taxes"]
        decoration = kwargs.get("decoration", 0)
        furniture = kwargs.get("furniture", 0)
        other_fees = kwargs.get("other_fees", 0)
        
        # 贷款金额
        loan_amount = price - down_payment
        
        # 各项成本
        costs = {
            "房屋总价": price,
            "首付金额": down_payment,
            "贷款金额": loan_amount,
            "贷款利息": total_interest,
            "税费": taxes,
            "装修费用": decoration,
            "家具家电": furniture,
            "其他费用": other_fees
        }
        
        # 初期投入（需要立即支付的）
        initial_cost = down_payment + taxes + decoration + furniture + other_fees
        
        # 总成本（含贷款利息）
        total_cost = price + total_interest + taxes + decoration + furniture + other_fees
        
        # 成本明细
        breakdown = [
            {"name": "首付", "amount": down_payment, "type": "initial"},
            {"name": "税费", "amount": taxes, "type": "initial"},
            {"name": "装修", "amount": decoration, "type": "initial"},
            {"name": "家具家电", "amount": furniture, "type": "initial"},
            {"name": "其他", "amount": other_fees, "type": "initial"},
            {"name": "贷款本金", "amount": loan_amount, "type": "loan"},
            {"name": "贷款利息", "amount": total_interest, "type": "loan"}
        ]
        
        return {
            "price": round(price, 2),
            "initial_cost": round(initial_cost, 2),
            "loan_amount": round(loan_amount, 2),
            "total_interest": round(total_interest, 2),
            "total_cost": round(total_cost, 2),
            "breakdown": breakdown,
            "summary": {
                "initial": round(initial_cost, 2),
                "loan_total": round(loan_amount + total_interest, 2),
                "grand_total": round(total_cost, 2)
            }
        }



@register_tool
class GenerateRepaymentPlanTool(BaseTool):
    """还款计划生成工具"""
    
    name = "generate_repayment_plan"
    description = "生成详细的还款计划表，展示每月/每年的本金、利息、剩余本金"
    parameters = [
        ToolParameter(
            name="loan_amount",
            type="number",
            description="贷款金额（元）"
        ),
        ToolParameter(
            name="years",
            type="integer",
            description="贷款年限（年）"
        ),
        ToolParameter(
            name="rate",
            type="number",
            description="年利率（%），如 4.2 表示 4.2%"
        ),
        ToolParameter(
            name="method",
            type="string",
            description="还款方式",
            enum=["equal_payment", "equal_principal"]
        ),
        ToolParameter(
            name="detail_level",
            type="string",
            description="明细级别：monthly=按月，yearly=按年",
            required=False,
            enum=["monthly", "yearly"]
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        生成还款计划
        
        Args:
            loan_amount: 贷款金额（元）
            years: 贷款年限
            rate: 年利率（%）
            method: 还款方式
            detail_level: 明细级别（monthly/yearly）
            
        Returns:
            还款计划详情
        """
        self.validate_params(**kwargs)
        
        loan_amount = kwargs["loan_amount"]
        years = kwargs["years"]
        rate = kwargs["rate"]
        method = kwargs["method"]
        detail_level = kwargs.get("detail_level", "yearly")
        
        monthly_rate = rate / 100 / 12
        months = years * 12
        
        if method == "equal_payment":
            schedule = self._generate_equal_payment_schedule(
                loan_amount, monthly_rate, months
            )
        else:
            schedule = self._generate_equal_principal_schedule(
                loan_amount, monthly_rate, months
            )
        
        # 计算汇总数据
        total_payment = sum(item["payment"] for item in schedule)
        total_interest = sum(item["interest"] for item in schedule)
        
        # 按年汇总（如果需要）
        if detail_level == "yearly":
            schedule = self._aggregate_yearly(schedule)
        
        return {
            "loan_amount": round(loan_amount, 2),
            "years": years,
            "rate": rate,
            "method": method,
            "method_name": "等额本息" if method == "equal_payment" else "等额本金",
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "detail_level": detail_level,
            "schedule": schedule[:36] if detail_level == "monthly" else schedule,  # 月度最多返回36期
            "schedule_count": len(schedule)
        }
    
    def _generate_equal_payment_schedule(
        self, 
        loan_amount: float, 
        monthly_rate: float, 
        months: int
    ) -> list[dict]:
        """生成等额本息还款计划"""
        schedule = []
        
        # 处理零利率
        if monthly_rate < 1e-10:
            monthly_payment = loan_amount / months
            remaining = loan_amount
            for period in range(1, months + 1):
                principal = monthly_payment
                remaining -= principal
                schedule.append({
                    "period": period,
                    "payment": round(monthly_payment, 2),
                    "principal": round(principal, 2),
                    "interest": 0,
                    "remaining": round(max(0, remaining), 2)
                })
            return schedule
        
        # 计算月供
        power = (1 + monthly_rate) ** months
        monthly_payment = loan_amount * monthly_rate * power / (power - 1)
        
        remaining = loan_amount
        for period in range(1, months + 1):
            interest = remaining * monthly_rate
            principal = monthly_payment - interest
            remaining -= principal
            
            schedule.append({
                "period": period,
                "payment": round(monthly_payment, 2),
                "principal": round(principal, 2),
                "interest": round(interest, 2),
                "remaining": round(max(0, remaining), 2)
            })
        
        return schedule
    
    def _generate_equal_principal_schedule(
        self, 
        loan_amount: float, 
        monthly_rate: float, 
        months: int
    ) -> list[dict]:
        """生成等额本金还款计划"""
        schedule = []
        monthly_principal = loan_amount / months
        remaining = loan_amount
        
        for period in range(1, months + 1):
            interest = remaining * monthly_rate
            payment = monthly_principal + interest
            remaining -= monthly_principal
            
            schedule.append({
                "period": period,
                "payment": round(payment, 2),
                "principal": round(monthly_principal, 2),
                "interest": round(interest, 2),
                "remaining": round(max(0, remaining), 2)
            })
        
        return schedule
    
    def _aggregate_yearly(self, monthly_schedule: list[dict]) -> list[dict]:
        """按年汇总还款计划"""
        yearly_schedule = []
        
        for year in range(1, len(monthly_schedule) // 12 + 1):
            start_idx = (year - 1) * 12
            end_idx = year * 12
            year_data = monthly_schedule[start_idx:end_idx]
            
            if not year_data:
                break
            
            yearly_schedule.append({
                "period": year,
                "period_label": f"第{year}年",
                "payment": round(sum(m["payment"] for m in year_data), 2),
                "principal": round(sum(m["principal"] for m in year_data), 2),
                "interest": round(sum(m["interest"] for m in year_data), 2),
                "remaining": year_data[-1]["remaining"]
            })
        
        return yearly_schedule


@register_tool
class AssessPressureTool(BaseTool):
    """还款压力评估工具"""
    
    name = "assess_pressure"
    description = "评估还款压力，根据月供和收入计算压力等级并给出建议"
    parameters = [
        ToolParameter(
            name="monthly_payment",
            type="number",
            description="月供金额（元）"
        ),
        ToolParameter(
            name="monthly_income",
            type="number",
            description="家庭月收入（元）"
        ),
        ToolParameter(
            name="monthly_expense",
            type="number",
            description="家庭月支出（元，不含房贷）",
            required=False
        ),
        ToolParameter(
            name="savings",
            type="number",
            description="现有存款（元）",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行还款压力评估
        
        Args:
            monthly_payment: 月供金额
            monthly_income: 家庭月收入
            monthly_expense: 家庭月支出（不含房贷）
            savings: 现有存款
            
        Returns:
            压力评估结果
        """
        self.validate_params(**kwargs)
        
        monthly_payment = kwargs["monthly_payment"]
        monthly_income = kwargs["monthly_income"]
        monthly_expense = kwargs.get("monthly_expense", 0)
        savings = kwargs.get("savings", 0)
        
        # 计算月供收入比
        payment_ratio = monthly_payment / monthly_income if monthly_income > 0 else 1
        
        # 计算剩余可支配收入
        disposable_income = monthly_income - monthly_payment - monthly_expense
        
        # 计算存款可支撑月数
        if monthly_payment > 0:
            savings_months = savings / monthly_payment
        else:
            savings_months = float('inf')
        
        # 评估压力等级
        level, level_name, color = self._assess_level(payment_ratio)
        
        # 生成建议
        suggestions = self._generate_suggestions(
            payment_ratio, 
            disposable_income, 
            savings_months,
            level
        )
        
        # 风险指标
        risk_factors = []
        if payment_ratio > 0.5:
            risk_factors.append("月供占比过高")
        if disposable_income < 2000:
            risk_factors.append("剩余可支配收入较低")
        if savings_months < 6:
            risk_factors.append("应急储备不足6个月")
        
        return {
            "payment_ratio": round(payment_ratio * 100, 1),  # 百分比
            "payment_ratio_display": f"{round(payment_ratio * 100, 1)}%",
            "level": level,
            "level_name": level_name,
            "level_color": color,
            "disposable_income": round(disposable_income, 2),
            "savings_months": round(savings_months, 1),
            "risk_factors": risk_factors,
            "suggestions": suggestions,
            "summary": self._generate_summary(level_name, payment_ratio, disposable_income)
        }
    
    def _assess_level(self, payment_ratio: float) -> tuple[str, str, str]:
        """
        评估压力等级
        - 月供/收入 ≤ 30%：低压力
        - 30% < 月供/收入 ≤ 50%：中压力
        - 月供/收入 > 50%：高压力
        """
        if payment_ratio <= 0.3:
            return "low", "低", "green"
        elif payment_ratio <= 0.5:
            return "medium", "中", "orange"
        else:
            return "high", "高", "red"
    
    def _generate_suggestions(
        self, 
        payment_ratio: float, 
        disposable_income: float,
        savings_months: float,
        level: str
    ) -> list[str]:
        """生成建议"""
        suggestions = []
        
        if level == "low":
            suggestions.append("您的还款压力较低，财务状况健康")
            suggestions.append("建议保持当前储蓄习惯，可考虑适当投资理财")
        elif level == "medium":
            suggestions.append("还款压力适中，建议控制其他大额支出")
            suggestions.append("建议保持至少6个月月供的应急储备")
            if disposable_income < 3000:
                suggestions.append("可考虑增加收入来源或减少非必要支出")
        else:
            suggestions.append("还款压力较大，需谨慎规划财务")
            suggestions.append("强烈建议减少非必要支出，优先保障还款")
            suggestions.append("可考虑延长贷款年限以降低月供")
            if savings_months < 3:
                suggestions.append("应急储备不足，建议尽快积累至少3个月月供")
        
        return suggestions
    
    def _generate_summary(
        self, 
        level_name: str, 
        payment_ratio: float,
        disposable_income: float
    ) -> str:
        """生成总结"""
        ratio_pct = round(payment_ratio * 100, 1)
        
        if level_name == "低":
            return f"您的月供占收入的{ratio_pct}%，还款压力较低，财务状况良好。"
        elif level_name == "中":
            return f"您的月供占收入的{ratio_pct}%，还款压力适中，建议合理规划支出。"
        else:
            return f"您的月供占收入的{ratio_pct}%，还款压力较大，建议谨慎考虑或调整贷款方案。"
