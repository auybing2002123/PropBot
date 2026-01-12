/**
 * 计算器 API
 */
import api from './index'
import type {
    LoanCalcParams,
    LoanCalcResult,
    TaxCalcParams,
    TaxCalcResult,
    TotalCostCalcParams,
    TotalCostCalcResult
} from '@/types/calculator'

/**
 * 贷款计算
 * @param params 贷款计算参数
 */
export async function calcLoan(params: LoanCalcParams): Promise<LoanCalcResult> {
    return api.post('/calc/loan', params)
}

/**
 * 税费计算
 * @param params 税费计算参数
 */
export async function calcTax(params: TaxCalcParams): Promise<TaxCalcResult> {
    return api.post('/calc/tax', params)
}

/**
 * 总成本计算
 * @param params 总成本计算参数
 */
export async function calcTotalCost(params: TotalCostCalcParams): Promise<TotalCostCalcResult> {
    return api.post('/calc/total_cost', params)
}
