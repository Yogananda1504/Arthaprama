"""
IPO Analysis Module for Arthaprama.

This module provides comprehensive analytical tools for evaluating Indian IPOs,
including growth metrics, risk assessment, valuation analysis, and composite scoring.
"""

from arthaprama.ipo.growth import (
    revenue_growth_yoy,
    profit_growth_yoy,
    ebitda_growth_yoy,
    eps_growth_yoy,
    revenue_cagr_3yr,
    pat_cagr_3yr,
    ebitda_margin,
    pat_margin,
    roe,
    roce,
    cfo_growth,
    calculate_all_growth_metrics,
    GrowthCalculationError,
)

from arthaprama.ipo.risk import (
    debt_to_equity,
    net_debt,
    net_debt_to_ebitda,
    interest_coverage,
    current_ratio,
    quick_ratio,
    cfo_to_debt,
    cfo_to_pat,
    free_cash_flow,
    fcf_to_pat,
    customer_concentration,
    promoter_pledge_ratio,
    contingent_liabilities_to_nw,
    calculate_all_risk_metrics,
    RiskCalculationError,
)

from arthaprama.ipo.valuation import (
    pe_ratio,
    pb_ratio,
    ps_ratio,
    ev_to_ebitda,
    ev_to_sales,
    peg_ratio,
    earnings_yield,
    price_to_fcf,
    enterprise_value,
    pe_premium_vs_peer,
    ev_ebitda_premium_vs_peer,
    ipo_dilution,
    post_ipo_eps,
    calculate_all_valuation_metrics,
    ValuationCalculationError,
)

from arthaprama.ipo.scoring import (
    generate_ipo_score,
    ScoreBreakdown,
)

from arthaprama.ipo.workflow import (
    run_full_ipo_analysis,
    IPOWorkflowEngine,
    IPOWorkflowError,
    GrowthAnalysisResult,
    RiskAnalysisResult,
    ValuationAnalysisResult,
    FullIPOAnalysisResult,
)

__all__ = [
    # Growth
    "revenue_growth_yoy",
    "profit_growth_yoy",
    "ebitda_growth_yoy",
    "eps_growth_yoy",
    "revenue_cagr_3yr",
    "pat_cagr_3yr",
    "ebitda_margin",
    "pat_margin",
    "roe",
    "roce",
    "cfo_growth",
    "calculate_all_growth_metrics",
    "GrowthCalculationError",
    # Risk
    "debt_to_equity",
    "net_debt",
    "net_debt_to_ebitda",
    "interest_coverage",
    "current_ratio",
    "quick_ratio",
    "cfo_to_debt",
    "cfo_to_pat",
    "free_cash_flow",
    "fcf_to_pat",
    "customer_concentration",
    "promoter_pledge_ratio",
    "contingent_liabilities_to_nw",
    "calculate_all_risk_metrics",
    "RiskCalculationError",
    # Valuation
    "pe_ratio",
    "pb_ratio",
    "ps_ratio",
    "ev_to_ebitda",
    "ev_to_sales",
    "peg_ratio",
    "earnings_yield",
    "price_to_fcf",
    "enterprise_value",
    "pe_premium_vs_peer",
    "ev_ebitda_premium_vs_peer",
    "ipo_dilution",
    "post_ipo_eps",
    "calculate_all_valuation_metrics",
    "ValuationCalculationError",
    # Scoring
    "generate_ipo_score",
    "ScoreBreakdown",
    # Workflow
    "run_full_ipo_analysis",
    "IPOWorkflowEngine",
    "IPOWorkflowError",
    "GrowthAnalysisResult",
    "RiskAnalysisResult",
    "ValuationAnalysisResult",
    "FullIPOAnalysisResult",
]
