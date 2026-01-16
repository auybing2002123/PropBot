"""
计算器 API
提供直接的财务计算功能，无需对话
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.tools.financial import CalcLoanTool, CalcTaxTool, CalcTotalCostTool
from app.utils.logger import get_logger

logger = get_logger("house_advisor.api.calculator")

router = APIRouter(prefix="/calc", tags=["计算器"])


# ==================== 请求模型 ====================

class LoanCalcRequest(BaseModel):
    """贷款计算请求"""
    price: float = Field(..., gt=0, description="房屋总价（元）")
    down_payment_ratio: float = Field(..., gt=0, le=1, description="首付比例，如 0.3 表示 30%")
    years: int = Field(..., gt=0, le=30, description="贷款年限（年）")
    rate: float = Field(..., ge=0, description="年利率（%），如 4.2 表示 4.2%")
    method: str = Field(default="equal_payment", description="还款方式: equal_payment=等额本息, equal_principal=等额本金")


class TaxCalcRequest(BaseModel):
    """税费计算请求"""
    price: float = Field(..., gt=0, description="房屋总价（元）")
    area: float = Field(..., gt=0, description="房屋面积（平方米）")
    is_first_home: bool = Field(..., description="是否首套房")
    house_age_years: int = Field(..., ge=0, description="房龄（年），新房填 0")
    original_price: float | None = Field(default=None, ge=0, description="原购买价格（元），用于计算增值税和个税")


class TotalCostCalcRequest(BaseModel):
    """总成本计算请求"""
    price: float = Field(..., gt=0, description="房屋总价（元）")
    down_payment: float = Field(..., ge=0, description="首付金额（元）")
    total_interest: float = Field(..., ge=0, description="贷款总利息（元）")
    taxes: float = Field(..., ge=0, description="税费总额（元）")
    decoration: float = Field(default=0, ge=0, description="装修费用（元）")
    furniture: float = Field(default=0, ge=0, description="家具家电费用（元）")
    other_fees: float = Field(default=0, ge=0, description="其他费用（元）")


# ==================== 响应模型 ====================

class APIResponse(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: dict | None = None


# ==================== API 端点 ====================

@router.post("/loan", response_model=APIResponse, summary="贷款计算")
async def calc_loan(request: LoanCalcRequest):
    """
    计算房贷
    
    支持等额本息和等额本金两种还款方式，返回首付、贷款金额、月供、总利息等信息。
    
    - equal_payment: 等额本息，月供固定
    - equal_principal: 等额本金，月供递减
    """
    logger.info(f"贷款计算请求: price={request.price}, ratio={request.down_payment_ratio}, years={request.years}")
    
    # 验证还款方式
    if request.method not in ("equal_payment", "equal_principal"):
        return APIResponse(
            code=3002,
            message="参数类型错误：method 必须是 equal_payment 或 equal_principal",
            data=None
        )
    
    tool = CalcLoanTool()
    result = await tool.execute(
        price=request.price,
        down_payment_ratio=request.down_payment_ratio,
        years=request.years,
        rate=request.rate,
        method=request.method
    )
    
    return APIResponse(code=0, message="success", data=result)


@router.post("/tax", response_model=APIResponse, summary="税费计算")
async def calc_tax(request: TaxCalcRequest):
    """
    计算购房税费
    
    包括契税、增值税、个税、中介费等。
    
    税费规则：
    - 契税：首套≤90㎡ 1%，首套>90㎡ 1.5%，二套≤90㎡ 1%，二套>90㎡ 2%
    - 增值税：满2年免征，不满2年按差额5.6%
    - 个税：满5年且唯一免征，其他按差额20%或全额1%取低
    """
    logger.info(f"税费计算请求: price={request.price}, area={request.area}, first_home={request.is_first_home}")
    
    tool = CalcTaxTool()
    
    # 构建参数
    params = {
        "price": request.price,
        "area": request.area,
        "is_first_home": request.is_first_home,
        "house_age_years": request.house_age_years
    }
    if request.original_price is not None:
        params["original_price"] = request.original_price
    
    result = await tool.execute(**params)
    
    return APIResponse(code=0, message="success", data=result)


@router.post("/total_cost", response_model=APIResponse, summary="总成本计算")
async def calc_total_cost(request: TotalCostCalcRequest):
    """
    计算购房总成本
    
    汇总首付、贷款利息、税费和其他费用，返回初期投入和总成本。
    """
    logger.info(f"总成本计算请求: price={request.price}, down_payment={request.down_payment}")
    
    tool = CalcTotalCostTool()
    result = await tool.execute(
        price=request.price,
        down_payment=request.down_payment,
        total_interest=request.total_interest,
        taxes=request.taxes,
        decoration=request.decoration,
        furniture=request.furniture,
        other_fees=request.other_fees
    )
    
    return APIResponse(code=0, message="success", data=result)
