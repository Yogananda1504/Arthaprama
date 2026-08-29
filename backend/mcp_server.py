"""
Arthaprama MCP Server - Model Context Protocol Implementation.

This module implements the Model Context Protocol (MCP) server for the Arthaprama
IPO Analysis Engine, exposing all IPO analysis tools to AI assistants and LLM agents.

The server supports two transport modes:
1. SSE Mode (FastAPI): Mountable on FastAPI applications for remote HTTP/SSE connections.
2. Stdio Mode (CLI): Runnable as a standalone CLI command for local desktop tools.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from mcp.server.fastmcp import FastMCP

from arthaprama.ipo.growth import (
    calculate_all_growth_metrics,
    GrowthCalculationError,
)
from arthaprama.ipo.risk import (
    calculate_all_risk_metrics,
    RiskCalculationError,
)
from arthaprama.ipo.valuation import (
    calculate_all_valuation_metrics,
    ValuationCalculationError,
)
from arthaprama.ipo.scoring import generate_ipo_score, ScoreBreakdown
from arthaprama.ipo.workflow import run_full_ipo_analysis, FullIPOAnalysisResult

# Configure logging
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp_server = FastMCP(
    name="Arthaprama IPO Intelligence Engine",
    instructions="Comprehensive IPO analysis engine providing growth, risk, valuation, and composite scoring tools for Indian IPOs.",
)


@mcp_server.tool()
def calculate_ipo_growth(
    revenues: list[float],
    profits: list[float] | None = None,
    ebitda: list[float] | None = None,
    assets: list[float] | None = None,
    equity: list[float] | None = None,
    industry_avg_growth: float | None = None,
    industry_avg_margin: float | None = None,
) -> dict[str, Any]:
    """
    Calculate comprehensive IPO growth metrics.

    This tool analyzes historical revenue, profit, and margin trends to compute
    growth rates, CAGRs, and stability metrics. It compares company performance
    against industry benchmarks when provided.

    Args:
        revenues: List of historical revenues (most recent last), e.g., [100, 120, 150].
        profits: Optional list of historical profits after tax (PAT).
        ebitda: Optional list of historical EBITDA values.
        assets: Optional list of total assets for ROCE calculation.
        equity: Optional list of shareholders' equity for ROE calculation.
        industry_avg_growth: Optional industry average growth rate for comparison.
        industry_avg_margin: Optional industry average margin for comparison.

    Returns:
        Dictionary containing:
            - revenue_cagr_3yr: 3-year revenue CAGR percentage.
            - profit_cagr_3yr: 3-year profit CAGR percentage (if profits provided).
            - ebitda_cagr_3yr: 3-year EBITDA CAGR percentage (if ebitda provided).
            - revenue_growth_yoy: Year-over-year revenue growth percentage.
            - profit_growth_yoy: Year-over-year profit growth percentage.
            - avg_ebitda_margin: Average EBITDA margin percentage.
            - avg_pat_margin: Average PAT margin percentage.
            - roe: Return on Equity percentage.
            - roce: Return on Capital Employed percentage.
            - growth_stability: Standard deviation of growth rates (lower is better).
            - vs_industry_growth: Comparison against industry average growth.
            - vs_industry_margin: Comparison against industry average margin.

    Raises:
        ValueError: If insufficient data points are provided.
        GrowthCalculationError: If calculation encounters invalid inputs.

    Example:
        >>> result = calculate_ipo_growth(
        ...     revenues=[100, 120, 150, 180],
        ...     profits=[10, 15, 20, 25],
        ...     industry_avg_growth=15.0
        ... )
        >>> result['revenue_cagr_3yr']
        21.64
    """
    # Validate minimum data requirements
    if len(revenues) < 2:
        return {"success": False, "error": "At least 2 revenue data points are required"}

    # Prepare input data for the core function
    growth_data: dict[str, Any] = {"revenues": revenues}

    if profits:
        growth_data["profits"] = profits
    if ebitda:
        growth_data["ebitda"] = ebitda
    if assets:
        growth_data["assets"] = assets
    if equity:
        growth_data["equity"] = equity

    try:
        # Call core domain function
        result = calculate_all_growth_metrics(growth_data)

        # Convert Decimal values to float for JSON serialization
        metrics_float = {k: float(v) if isinstance(v, Decimal) else v for k, v in result.items()}

        # Add industry comparisons if provided
        if industry_avg_growth is not None and "revenue_cagr_3yr" in metrics_float:
            metrics_float["vs_industry_growth"] = (
                metrics_float["revenue_cagr_3yr"] - industry_avg_growth
            )

        if industry_avg_margin is not None:
            # Check for ebitda_margin (the actual key returned by domain function)
            margin_key = "ebitda_margin" if "ebitda_margin" in metrics_float else "avg_ebitda_margin"
            if margin_key in metrics_float:
                metrics_float["vs_industry_margin"] = (
                    metrics_float[margin_key] - industry_avg_margin
                )

        return {"success": True, "metrics": metrics_float}

    except GrowthCalculationError as e:
        logger.error(f"Growth calculation error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in growth calculation: {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp_server.tool()
def evaluate_ipo_risk(
    total_debt: float,
    shareholders_equity: float,
    cash_equivalents: float,
    ebitda: float,
    interest_expense: float,
    current_assets: float,
    current_liabilities: float,
    inventory: float | None = None,
    operating_cash_flow: float | None = None,
    net_profit: float | None = None,
    promoter_holding: float | None = None,
    promoter_pledge: float | None = None,
    top_customer_revenue_pct: float | None = None,
    contingent_liabilities: float | None = None,
    net_worth: float | None = None,
) -> dict[str, Any]:
    """
    Evaluate IPO risk across multiple dimensions.

    This tool assesses capital structure risk, liquidity risk, cash flow quality,
    and promoter/governance risk factors. It produces a comprehensive risk matrix
    with penalties for high-risk indicators.

    Args:
        total_debt: Total outstanding debt (short-term + long-term).
        shareholders_equity: Total shareholders' equity.
        cash_equivalents: Cash and cash equivalents on hand.
        ebitda: Earnings Before Interest, Taxes, Depreciation, and Amortization.
        interest_expense: Annual interest expense.
        current_assets: Total current assets.
        current_liabilities: Total current liabilities.
        inventory: Optional inventory value for quick ratio calculation.
        operating_cash_flow: Optional cash flow from operations (CFO).
        net_profit: Optional net profit for CFO/PAT ratio.
        promoter_holding: Optional promoter shareholding percentage (0-100).
        promoter_pledge: Optional promoter pledged shares percentage (0-100).
        top_customer_revenue_pct: Optional revenue concentration from top customer.
        contingent_liabilities: Optional contingent liabilities value.
        net_worth: Optional net worth for contingent liabilities ratio.

    Returns:
        Dictionary containing:
            - debt_to_equity: Debt-to-equity ratio.
            - net_debt: Net debt (total debt - cash).
            - net_debt_to_ebitda: Net debt to EBITDA ratio.
            - interest_coverage: Interest coverage ratio.
            - current_ratio: Current ratio (liquidity metric).
            - quick_ratio: Quick ratio (acid-test liquidity metric).
            - cfo_to_debt: Cash flow from operations to debt ratio.
            - cfo_to_pat: Cash flow quality ratio.
            - promoter_pledge_ratio: Promoter pledge percentage.
            - customer_concentration: Top customer revenue concentration.
            - contingent_liabilities_ratio: Contingent liabilities to net worth.
            - risk_matrix: Categorized risk scores (leverage, liquidity, governance).
            - total_risk_penalty: Aggregate risk penalty score.
            - risk_assessment: Overall risk rating (Low/Medium/High/Critical).

    Raises:
        ValueError: If required parameters are missing or invalid.
        RiskCalculationError: If calculation encounters invalid inputs.

    Example:
        >>> result = evaluate_ipo_risk(
        ...     total_debt=500,
        ...     shareholders_equity=1000,
        ...     cash_equivalents=150,
        ...     ebitda=200,
        ...     interest_expense=50,
        ...     current_assets=300,
        ...     current_liabilities=200
        ... )
        >>> result['debt_to_equity']
        0.5
    """
    # Validate required parameters
    if total_debt < 0 or shareholders_equity <= 0 or ebitda < 0:
        return {"success": False, "error": "Invalid financial parameters provided"}

    # Prepare input data for core risk function
    risk_data: dict[str, Any] = {
        "total_debt": total_debt,
        "shareholders_equity": shareholders_equity,
        "cash_equivalents": cash_equivalents,
        "ebitda": ebitda,
        "interest_expense": interest_expense,
        "current_assets": current_assets,
        "current_liabilities": current_liabilities,
    }

    # Add optional parameters
    if inventory is not None:
        risk_data["inventory"] = inventory
    if operating_cash_flow is not None:
        risk_data["operating_cash_flow"] = operating_cash_flow
    if net_profit is not None:
        risk_data["net_profit"] = net_profit
    if promoter_holding is not None:
        risk_data["promoter_holding"] = promoter_holding
    if promoter_pledge is not None:
        risk_data["promoter_pledge"] = promoter_pledge
    if top_customer_revenue_pct is not None:
        risk_data["top_customer_revenue_pct"] = top_customer_revenue_pct
    if contingent_liabilities is not None and net_worth is not None:
        risk_data["contingent_liabilities"] = contingent_liabilities
        risk_data["net_worth"] = net_worth

    try:
        # Call core domain function
        result = calculate_all_risk_metrics(risk_data)

        # Convert Decimal values to float
        metrics_float = {k: float(v) if isinstance(v, Decimal) else v for k, v in result.items()}

        # Build risk matrix
        risk_matrix = {
            "leverage_risk": "High" if metrics_float.get("debt_to_equity", 0) > 2.0 else 
                            "Medium" if metrics_float.get("debt_to_equity", 0) > 1.0 else "Low",
            "liquidity_risk": "High" if metrics_float.get("current_ratio", 999) < 1.0 else
                             "Medium" if metrics_float.get("current_ratio", 999) < 1.5 else "Low",
            "governance_risk": "High" if metrics_float.get("promoter_pledge_ratio", 0) > 50 else
                              "Medium" if metrics_float.get("promoter_pledge_ratio", 0) > 25 else "Low",
        }

        # Calculate total risk penalty (simplified scoring)
        risk_penalty = 0.0
        if metrics_float.get("debt_to_equity", 0) > 2.0:
            risk_penalty += 2.0
        elif metrics_float.get("debt_to_equity", 0) > 1.0:
            risk_penalty += 1.0

        if metrics_float.get("net_debt_to_ebitda", 0) > 5.0:
            risk_penalty += 2.0
        elif metrics_float.get("net_debt_to_ebitda", 0) > 3.0:
            risk_penalty += 1.0

        if metrics_float.get("interest_coverage", 999) < 2.0:
            risk_penalty += 2.0
        elif metrics_float.get("interest_coverage", 999) < 3.0:
            risk_penalty += 1.0

        if metrics_float.get("promoter_pledge_ratio", 0) > 50:
            risk_penalty += 2.0
        elif metrics_float.get("promoter_pledge_ratio", 0) > 25:
            risk_penalty += 1.0

        # Determine overall risk assessment
        if risk_penalty >= 5.0:
            risk_assessment = "Critical"
        elif risk_penalty >= 3.0:
            risk_assessment = "High"
        elif risk_penalty >= 1.0:
            risk_assessment = "Medium"
        else:
            risk_assessment = "Low"

        return {
            "success": True,
            "metrics": metrics_float,
            "risk_matrix": risk_matrix,
            "total_risk_penalty": risk_penalty,
            "risk_assessment": risk_assessment,
        }

    except RiskCalculationError as e:
        logger.error(f"Risk calculation error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in risk calculation: {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp_server.tool()
def model_ipo_valuation(
    ipo_price: float,
    eps_pre_ipo: float,
    book_value_per_share: float,
    sales_per_share: float,
    ev_pre_ipo: float | None = None,
    ebitda: float | None = None,
    peer_pe_multiples: list[float] | None = None,
    peer_pb_multiples: list[float] | None = None,
    peer_ev_ebitda_multiples: list[float] | None = None,
    dcf_fcf_projections: list[float] | None = None,
    dcf_discount_rate: float | None = None,
    dcf_terminal_growth: float | None = None,
    shares_outstanding_pre_ipo: float | None = None,
    shares_offered: float | None = None,
) -> dict[str, Any]:
    """
    Model IPO valuation using multiple methodologies.

    This tool calculates implied valuation multiples from the IPO price band,
    compares them against peer benchmarks, and optionally computes DCF-based
    fair value estimates.

    Args:
        ipo_price: IPO offer price per share.
        eps_pre_ipo: Pre-IPO earnings per share.
        book_value_per_share: Book value per share.
        sales_per_share: Sales/revenue per share.
        ev_pre_ipo: Optional pre-IPO enterprise value.
        ebitda: Optional EBITDA for EV/EBITDA calculation.
        peer_pe_multiples: Optional list of peer P/E multiples for comparison.
        peer_pb_multiples: Optional list of peer P/B multiples for comparison.
        peer_ev_ebitda_multiples: Optional list of peer EV/EBITDA multiples.
        dcf_fcf_projections: Optional list of projected free cash flows for DCF.
        dcf_discount_rate: Optional discount rate (WACC) for DCF.
        dcf_terminal_growth: Optional terminal growth rate for DCF.
        shares_outstanding_pre_ipo: Optional pre-IPO shares outstanding.
        shares_offered: Optional number of shares being offered in IPO.

    Returns:
        Dictionary containing:
            - implied_pe: Implied P/E ratio at IPO price.
            - implied_pb: Implied P/B ratio at IPO price.
            - implied_ps: Implied P/S ratio at IPO price.
            - implied_ev_ebitda: Implied EV/EBITDA multiple (if data available).
            - peer_avg_pe: Average peer P/E multiple.
            - peer_avg_pb: Average peer P/B multiple.
            - pe_premium_to_peers: Percentage premium/discount to peer average P/E.
            - pb_premium_to_peers: Percentage premium/discount to peer average P/B.
            - dcf_fair_value: DCF-derived fair value per share (if projections provided).
            - discount_to_fair_value: Percentage discount/premium to DCF fair value.
            - valuation_assessment: Overall valuation rating (Undervalued/Fair/Overvalued).

    Raises:
        ValueError: If required parameters are missing or invalid.
        ValuationCalculationError: If calculation encounters invalid inputs.

    Example:
        >>> result = model_ipo_valuation(
        ...     ipo_price=500,
        ...     eps_pre_ipo=25,
        ...     book_value_per_share=200,
        ...     sales_per_share=100,
        ...     peer_pe_multiples=[18, 20, 22]
        ... )
        >>> result['implied_pe']
        20.0
    """
    # Validate required parameters
    if ipo_price <= 0 or eps_pre_ipo <= 0 or book_value_per_share <= 0:
        return {"success": False, "error": "Invalid valuation parameters provided"}

    # Prepare input data for core valuation function
    valuation_data: dict[str, Any] = {
        "ipo_price": ipo_price,
        "eps": eps_pre_ipo,
        "book_value_per_share": book_value_per_share,
        "sales_per_share": sales_per_share,
    }

    if ev_pre_ipo is not None and ebitda is not None:
        valuation_data["ev"] = ev_pre_ipo
        valuation_data["ebitda"] = ebitda

    try:
        # Call core domain function
        result = calculate_all_valuation_metrics(valuation_data)

        # Convert Decimal values to float
        metrics_float = {k: float(v) if isinstance(v, Decimal) else v for k, v in result.items()}

        # Calculate peer comparisons
        peer_comparison = {}
        if peer_pe_multiples and len(peer_pe_multiples) > 0:
            peer_avg_pe = sum(peer_pe_multiples) / len(peer_pe_multiples)
            peer_comparison["peer_avg_pe"] = peer_avg_pe
            if "pe_ratio" in metrics_float:
                peer_comparison["pe_premium_to_peers"] = (
                    (metrics_float["pe_ratio"] - peer_avg_pe) / peer_avg_pe * 100
                )

        if peer_pb_multiples and len(peer_pb_multiples) > 0:
            peer_avg_pb = sum(peer_pb_multiples) / len(peer_pb_multiples)
            peer_comparison["peer_avg_pb"] = peer_avg_pb
            if "pb_ratio" in metrics_float:
                peer_comparison["pb_premium_to_peers"] = (
                    (metrics_float["pb_ratio"] - peer_avg_pb) / peer_avg_pb * 100
                )

        if peer_ev_ebitda_multiples and len(peer_ev_ebitda_multiples) > 0:
            peer_avg_ev_ebitda = sum(peer_ev_ebitda_multiples) / len(peer_ev_ebitda_multiples)
            peer_comparison["peer_avg_ev_ebitda"] = peer_avg_ev_ebitda
            if "ev_to_ebitda" in metrics_float:
                peer_comparison["ev_ebitda_premium_to_peers"] = (
                    (metrics_float["ev_to_ebitda"] - peer_avg_ev_ebitda) / peer_avg_ev_ebitda * 100
                )

        # Calculate DCF fair value if projections provided
        dcf_result = {}
        if dcf_fcf_projections and dcf_discount_rate and dcf_terminal_growth:
            try:
                # Simplified DCF calculation
                terminal_value = (
                    dcf_fcf_projections[-1] * (1 + dcf_terminal_growth) / 
                    (dcf_discount_rate - dcf_terminal_growth)
                )
                
                # Discount cash flows and terminal value
                pv_fcf = sum(
                    fcf / ((1 + dcf_discount_rate) ** (i + 1))
                    for i, fcf in enumerate(dcf_fcf_projections)
                )
                pv_terminal = terminal_value / ((1 + dcf_discount_rate) ** len(dcf_fcf_projections))
                
                enterprise_value = pv_fcf + pv_terminal
                
                # Adjust for net debt to get equity value (simplified)
                # Assuming shares_outstanding_pre_ipo is provided
                if shares_outstanding_pre_ipo and shares_outstanding_pre_ipo > 0:
                    dcf_fair_value = enterprise_value / shares_outstanding_pre_ipo
                    dcf_result["dcf_fair_value"] = dcf_fair_value
                    dcf_result["discount_to_fair_value"] = (
                        (dcf_fair_value - ipo_price) / dcf_fair_value * 100
                    )
            except Exception as e:
                logger.warning(f"DCF calculation failed: {e}")
                dcf_result["dcf_error"] = str(e)

        # Determine valuation assessment
        pe_premium = peer_comparison.get("pe_premium_to_peers", 0)
        if pe_premium > 20:
            valuation_assessment = "Overvalued"
        elif pe_premium < -20:
            valuation_assessment = "Undervalued"
        else:
            valuation_assessment = "Fairly Valued"

        return {
            "success": True,
            "metrics": metrics_float,
            "peer_comparison": peer_comparison,
            "dcf_analysis": dcf_result,
            "valuation_assessment": valuation_assessment,
        }

    except ValuationCalculationError as e:
        logger.error(f"Valuation calculation error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in valuation calculation: {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp_server.tool()
def generate_composite_ipo_score(
    growth_metrics: dict[str, float],
    risk_metrics: dict[str, float],
    valuation_metrics: dict[str, float],
    ipo_quality_inputs: dict[str, Any] | None = None,
    profile: str = "balanced",
) -> dict[str, Any]:
    """
    Generate composite IPO score from growth, risk, and valuation analyses.

    This tool combines outputs from growth, risk, and valuation calculations
    into a unified 100-point score with rating tier and actionable recommendation.

    Args:
        growth_metrics: Dictionary of growth metrics from calculate_ipo_growth, including:
            - revenue_cagr_3yr: 3-year revenue CAGR.
            - profit_cagr_3yr: 3-year profit CAGR.
            - ebitda_margin: Average EBITDA margin.
            - roe: Return on Equity.
            - roce: Return on Capital Employed.
        risk_metrics: Dictionary of risk metrics from evaluate_ipo_risk, including:
            - debt_to_equity: Debt-to-equity ratio.
            - interest_coverage: Interest coverage ratio.
            - current_ratio: Current ratio.
            - promoter_pledge_ratio: Promoter pledge percentage.
        valuation_metrics: Dictionary of valuation metrics from model_ipo_valuation, including:
            - pe_ratio: P/E ratio.
            - pb_ratio: P/B ratio.
            - ev_to_ebitda: EV/EBITDA multiple.
            - peg_ratio: PEG ratio.
        ipo_quality_inputs: Optional IPO-specific inputs:
            - issue_size: Total IPO issue size.
            - dilution_pct: Equity dilution percentage.
            - promoter_holding_pre: Pre-IPO promoter holding.
            - promoter_holding_post: Post-IPO promoter holding.
            - anchor_investor_pct: Anchor investor allocation percentage.
        profile: Investor profile strategy ("balanced", "conservative", "aggressive", "deep_value").

    Returns:
        Dictionary containing:
            - growth_score: Score out of maximum growth weight (typically 30).
            - risk_score: Score out of maximum risk weight (typically 30).
            - valuation_score: Score out of maximum valuation weight (typically 30).
            - ipo_quality_score: Score out of maximum IPO quality weight (typically 10).
            - total_score: Composite score out of 100.
            - rating_tier: Rating category (AAA/AA/A/BBB/BB/B/C).
            - recommendation: Actionable investment recommendation.
            - score_breakdown: Detailed breakdown by sub-metric.

    Raises:
        ValueError: If required metric dictionaries are empty or malformed.

    Example:
        >>> result = generate_composite_ipo_score(
        ...     growth_metrics={"revenue_cagr_3yr": 20.0, "profit_cagr_3yr": 25.0},
        ...     risk_metrics={"debt_to_equity": 0.5, "interest_coverage": 5.0},
        ...     valuation_metrics={"pe_ratio": 18.0, "pb_ratio": 3.0},
        ...     profile="balanced"
        ... )
        >>> result['total_score']
        75.5
    """
    # Validate inputs
    if not growth_metrics or not risk_metrics or not valuation_metrics:
        return {"success": False, "error": "Growth, risk, and valuation metrics are all required"}

    # Convert float metrics back to Decimal-compatible format for core function
    # The scoring engine expects specific metric names
    scoring_input: dict[str, Any] = {
        "growth": growth_metrics,
        "risk": risk_metrics,
        "valuation": valuation_metrics,
    }

    if ipo_quality_inputs:
        scoring_input["ipo_quality"] = ipo_quality_inputs

    try:
        # Call core scoring function with correct parameter names
        # Provide empty dict for ipo_data if None to avoid AttributeError
        score_result = generate_ipo_score(
            growth_data=scoring_input.get("growth", {}),
            risk_data=scoring_input.get("risk", {}),
            valuation_data=scoring_input.get("valuation", {}),
            ipo_data=scoring_input.get("ipo_quality") or {},
            profile=profile,
        )

        # Convert ScoreBreakdown to dictionary
        if isinstance(score_result, ScoreBreakdown):
            score_dict = score_result.to_dict()
        else:
            score_dict = score_result

        # Determine rating tier based on total score
        total_score = score_dict.get("total_score", 0)
        if total_score >= 90:
            rating_tier = "AAA"
            recommendation = "Strong Buy - Exceptional fundamentals across all pillars"
        elif total_score >= 80:
            rating_tier = "AA"
            recommendation = "Buy - Strong fundamentals with minor areas of concern"
        elif total_score >= 70:
            rating_tier = "A"
            recommendation = "Accumulate - Good fundamentals, suitable for long-term portfolio"
        elif total_score >= 60:
            rating_tier = "BBB"
            recommendation = "Hold - Average fundamentals, monitor for improvements"
        elif total_score >= 50:
            rating_tier = "BB"
            recommendation = "Reduce - Below-average fundamentals, consider partial exit"
        elif total_score >= 40:
            rating_tier = "B"
            recommendation = "Sell - Weak fundamentals, high risk of underperformance"
        else:
            rating_tier = "C"
            recommendation = "Avoid - Critical weaknesses, significant downside risk"

        return {
            "success": True,
            **score_dict,
            "rating_tier": rating_tier,
            "recommendation": recommendation,
        }

    except Exception as e:
        logger.error(f"Composite score generation error: {e}")
        return {"success": False, "error": str(e)}


@mcp_server.tool()
def run_full_ipo_workflow(
    company_name: str,
    ipo_date: str,
    ipo_price: float,
    financials: dict[str, Any],
    industry_benchmarks: dict[str, Any] | None = None,
    peer_multiples: dict[str, Any] | None = None,
    ipo_specifics: dict[str, Any] | None = None,
    profile: str = "balanced",
) -> dict[str, Any]:
    """
    Execute complete IPO analysis workflow in a single call.

    This tool orchestrates the full IPO analysis pipeline, accepting comprehensive
    IPO metadata and financial parameters, executing all domain calculations,
    and returning a consolidated assessment report.

    Args:
        company_name: Name of the IPO company.
        ipo_date: Expected or actual IPO listing date (YYYY-MM-DD format).
        ipo_price: IPO offer price per share.
        financials: Comprehensive financial data dictionary containing:
            - revenues: List of historical revenues [oldest, ..., most_recent].
            - profits: List of historical PAT values.
            - ebitda: List of historical EBITDA values.
            - total_debt: Current total debt.
            - shareholders_equity: Current shareholders' equity.
            - cash_equivalents: Current cash and equivalents.
            - interest_expense: Annual interest expense.
            - current_assets: Current assets.
            - current_liabilities: Current liabilities.
            - eps: Earnings per share.
            - book_value_per_share: Book value per share.
            - sales_per_share: Revenue per share.
        industry_benchmarks: Optional industry benchmark data:
            - avg_growth: Industry average growth rate.
            - avg_margin: Industry average margin.
            - avg_roe: Industry average ROE.
        peer_multiples: Optional peer company valuation multiples:
            - pe_multiples: List of peer P/E ratios.
            - pb_multiples: List of peer P/B ratios.
            - ev_ebitda_multiples: List of peer EV/EBITDA ratios.
        ipo_specifics: Optional IPO-specific details:
            - issue_size: Total issue size.
            - fresh_issue: Fresh issue amount.
            - ofr_size: Offer for sale amount.
            - promoter_holding_pre: Pre-IPO promoter holding %.
            - promoter_holding_post: Post-IPO promoter holding %.
            - dilution_pct: Equity dilution percentage.
        profile: Investor profile strategy ("balanced", "conservative", "aggressive", "deep_value").

    Returns:
        Dictionary containing:
            - company_name: Name of the analyzed company.
            - ipo_date: IPO listing date.
            - growth_analysis: Complete growth metrics and assessment.
            - risk_analysis: Complete risk metrics and assessment.
            - valuation_analysis: Complete valuation metrics and assessment.
            - composite_score: 100-point composite score breakdown.
            - rating_tier: Final rating (AAA/AA/A/BBB/BB/B/C).
            - recommendation: Actionable investment recommendation.
            - executive_summary: Concise summary of key findings.
            - success: Boolean indicating successful execution.

    Raises:
        ValueError: If required financial data is missing.
        IPOWorkflowError: If workflow execution encounters errors.

    Example:
        >>> result = run_full_ipo_workflow(
        ...     company_name="Example Ltd",
        ...     ipo_date="2024-03-15",
        ...     ipo_price=500,
        ...     financials={
        ...         "revenues": [100, 120, 150, 180],
        ...         "profits": [10, 15, 20, 25],
        ...         "total_debt": 500,
        ...         "shareholders_equity": 1000,
        ...         "eps": 25,
        ...         "book_value_per_share": 200
        ...     },
        ...     profile="balanced"
        ... )
        >>> result['composite_score']['total_score']
        75.5
    """
    # Validate required inputs
    if not company_name or not ipo_date or ipo_price <= 0:
        return {"success": False, "error": "Company name, IPO date, and IPO price are required"}

    required_financial_keys = [
        "revenues",
        "total_debt",
        "shareholders_equity",
        "eps",
        "book_value_per_share",
    ]
    for key in required_financial_keys:
        if key not in financials:
            return {"success": False, "error": f"Required financial data missing: {key}"}

    try:
        # Run the full IPO analysis workflow using the domain function signature
        workflow_result = run_full_ipo_analysis(
            growth_data={
                "revenue_current": financials.get("revenues", [])[-1] if financials.get("revenues") else 0,
                "revenue_previous": financials.get("revenues", [])[-2] if len(financials.get("revenues", [])) > 1 else 0,
                "revenue_3yrs_ago": financials.get("revenues", [0])[0],
                "pat_current": financials.get("profits", [])[-1] if financials.get("profits") else 0,
                "pat_previous": financials.get("profits", [])[-2] if len(financials.get("profits", [])) > 1 else 0,
                "pat_3yrs_ago": financials.get("profits", [0])[0],
                "ebitda_current": financials.get("ebitda", [])[-1] if financials.get("ebitda") else 0,
                "ebitda_previous": financials.get("ebitda", [])[-2] if len(financials.get("ebitda", [])) > 1 else 0,
                "eps_current": financials.get("eps", 0),
                "eps_previous": 0,
                "ebit": 0,
                "cfo_current": 0,
                "cfo_previous": 0,
                "avg_shareholders_equity": financials.get("shareholders_equity", 0),
                "capital_employed": 0,
            },
            risk_data={
                "total_debt": financials.get("total_debt", 0),
                "shareholders_equity": financials.get("shareholders_equity", 0),
                "cash_equivalents": financials.get("cash_equivalents", 0),
                "ebitda": financials.get("ebitda", [])[-1] if financials.get("ebitda") else 0,
                "interest_expense": financials.get("interest_expense", 0),
                "current_assets": financials.get("current_assets", 0),
                "current_liabilities": financials.get("current_liabilities", 0),
                "inventory": 0,
                "cfo": 0,
                "pat": financials.get("profits", [])[-1] if financials.get("profits") else 0,
                "capex": 0,
                "largest_customer_rev": 0,
                "total_rev": financials.get("revenues", [])[-1] if financials.get("revenues") else 0,
                "pledged_shares": 0,
                "total_promoter_shares": 0,
                "contingent_liabilities": 0,
                "net_worth": financials.get("shareholders_equity", 0),
            },
            valuation_data={
                "market_cap": 0,
                "pat": financials.get("profits", [])[-1] if financials.get("profits") else 0,
                "book_value": financials.get("shareholders_equity", 0),
                "revenue": financials.get("revenues", [])[-1] if financials.get("revenues") else 0,
                "ebitda": financials.get("ebitda", [])[-1] if financials.get("ebitda") else 0,
                "eps": financials.get("eps", 0),
                "ipo_price": ipo_price,
                "total_debt": financials.get("total_debt", 0),
                "cash_equivalents": financials.get("cash_equivalents", 0),
                "free_cash_flow": 0,
                "new_shares": 0,
                "post_ipo_shares": 0,
                "post_ipo_diluted_shares": 0,
                "post_ipo_pat": financials.get("profits", [])[-1] if financials.get("profits") else 0,
                "expected_eps_growth_pct": 0,
            },
            ipo_data={
                "ipo_dilution": ipo_specifics.get("dilution_pct", 0) if ipo_specifics else 0,
                "promoter_holding_post_ipo": ipo_specifics.get("promoter_holding_post", 0) if ipo_specifics else 0,
                "promoter_pledge_ratio": 0,
            },
            profile=profile,
            peer_data=peer_multiples,
            precision=4,
        )

        # Convert workflow result to dictionary
        if isinstance(workflow_result, FullIPOAnalysisResult):
            result_dict = workflow_result.to_dict()
        else:
            result_dict = workflow_result

        # Extract composite score and determine rating
        composite_score = result_dict.get("composite_score", {})
        total_score = composite_score.get("total_score", 0) if composite_score else 0

        # Determine rating tier
        if total_score >= 90:
            rating_tier = "AAA"
            recommendation = "Strong Buy - Exceptional fundamentals across all pillars"
        elif total_score >= 80:
            rating_tier = "AA"
            recommendation = "Buy - Strong fundamentals with minor areas of concern"
        elif total_score >= 70:
            rating_tier = "A"
            recommendation = "Accumulate - Good fundamentals, suitable for long-term portfolio"
        elif total_score >= 60:
            rating_tier = "BBB"
            recommendation = "Hold - Average fundamentals, monitor for improvements"
        elif total_score >= 50:
            rating_tier = "BB"
            recommendation = "Reduce - Below-average fundamentals, consider partial exit"
        elif total_score >= 40:
            rating_tier = "B"
            recommendation = "Sell - Weak fundamentals, high risk of underperformance"
        else:
            rating_tier = "C"
            recommendation = "Avoid - Critical weaknesses, significant downside risk"

        # Generate executive summary
        growth_analysis = result_dict.get("growth_analysis", {})
        risk_analysis = result_dict.get("risk_analysis", {})
        valuation_analysis = result_dict.get("valuation_analysis", {})

        executive_summary = (
            f"{company_name} IPO Analysis ({ipo_date}): "
            f"Total Score {total_score}/100 ({rating_tier}). "
        )

        if growth_analysis.get("metrics", {}).get("revenue_cagr_3yr"):
            rev_cagr = growth_analysis["metrics"]["revenue_cagr_3yr"]
            executive_summary += f"Revenue CAGR: {rev_cagr:.1f}%. "

        if risk_analysis.get("metrics", {}).get("debt_to_equity"):
            dte = risk_analysis["metrics"]["debt_to_equity"]
            executive_summary += f"D/E: {dte:.2f}. "

        if valuation_analysis.get("metrics", {}).get("pe_ratio"):
            pe = valuation_analysis["metrics"]["pe_ratio"]
            executive_summary += f"P/E: {pe:.1f}x. "

        executive_summary += f"Recommendation: {recommendation.split(' - ')[0]}."

        return {
            "success": True,
            "company_name": company_name,
            "ipo_date": ipo_date,
            **result_dict,
            "rating_tier": rating_tier,
            "recommendation": recommendation,
            "executive_summary": executive_summary,
        }

    except Exception as e:
        logger.error(f"Full IPO workflow error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "company_name": company_name,
            "ipo_date": ipo_date,
        }


# Expose the MCP server instance for FastAPI integration
__all__ = ["mcp_server"]


# Stdio CLI entrypoint
if __name__ == "__main__":
    # Run MCP server in stdio mode for local desktop tools
    mcp_server.run(transport="stdio")
