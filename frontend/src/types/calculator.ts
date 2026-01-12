/**
 * 计算器相关类型定义
 */

// 还款方式
export type RepaymentMethod = 'equal_payment' | 'equal_principal'

// 贷款计算请求参数
export interface LoanCalcParams {
    price: number              // 房屋总价（元）
    down_payment_ratio: number // 首付比例，如 0.3 表示 30%
    years: number              // 贷款年限（年）
    rate: number               // 年利率（%），如 4.2 表示 4.2%
    method: RepaymentMethod    // 还款方式
}

// 贷款计算结果
export interface LoanCalcResult {
    down_payment: number       // 首付金额（元）
    loan_amount: number        // 贷款金额（元）
    monthly_payment: number    // 月供（元）
    total_interest: number     // 总利息（元）
    total_payment: number      // 还款总额（元）
    first_month_payment?: number  // 首月还款（等额本金）
    monthly_decrease?: number     // 每月递减（等额本金）
}

// 税费计算请求参数
export interface TaxCalcParams {
    price: number              // 房屋总价（元）
    area: number               // 房屋面积（平方米）
    is_first_home: boolean     // 是否首套房
    house_age_years: number    // 房龄（年），新房填 0
    original_price?: number    // 原购买价格（元），用于计算增值税和个税
}

// 税费计算结果
export interface TaxCalcResult {
    deed_tax: number           // 契税（元）
    vat: number                // 增值税（元）
    income_tax: number         // 个税（元）
    agent_fee: number          // 中介费（元）
    registration_fee: number   // 登记费（元）
    total: number              // 总税费（元）
    details: TaxDetail[]       // 税费明细
}

// 税费明细项
export interface TaxDetail {
    name: string               // 税费名称
    amount: number             // 金额（元）
    rate?: string              // 税率说明
    note?: string              // 备注
}

// 总成本计算请求参数
export interface TotalCostCalcParams {
    price: number              // 房屋总价（元）
    down_payment: number       // 首付金额（元）
    total_interest: number     // 贷款总利息（元）
    taxes: number              // 税费总额（元）
    decoration?: number        // 装修费用（元）
    furniture?: number         // 家具家电费用（元）
    other_fees?: number        // 其他费用（元）
}

// 总成本计算结果
export interface TotalCostCalcResult {
    initial_cost: number       // 初期投入（首付+税费）
    loan_cost: number          // 贷款成本（本金+利息）
    other_cost: number         // 其他成本（装修+家具+其他）
    total_cost: number         // 购房总成本
    breakdown: CostBreakdown[] // 成本明细
}

// 成本明细项
export interface CostBreakdown {
    category: string           // 分类
    name: string               // 名称
    amount: number             // 金额（元）
}

// 首付比例选项
export const DOWN_PAYMENT_OPTIONS = [
    { label: '20%', value: 0.2 },
    { label: '30%', value: 0.3 },
    { label: '40%', value: 0.4 },
    { label: '50%', value: 0.5 }
]

// 贷款年限选项
export const LOAN_YEARS_OPTIONS = [
    { label: '10年', value: 10 },
    { label: '15年', value: 15 },
    { label: '20年', value: 20 },
    { label: '25年', value: 25 },
    { label: '30年', value: 30 }
]

// 还款方式选项
export const REPAYMENT_METHOD_OPTIONS = [
    { label: '等额本息', value: 'equal_payment' as RepaymentMethod },
    { label: '等额本金', value: 'equal_principal' as RepaymentMethod }
]

// 当前贷款利率（2025年1月）
export const CURRENT_RATES = {
    commercial_first: 3.4,     // 商贷首套
    commercial_second: 3.8,    // 商贷二套
    provident_below_5y: 2.35,  // 公积金5年以下
    provident_above_5y: 2.85   // 公积金5年以上
}
