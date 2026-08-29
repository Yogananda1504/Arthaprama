"""
100-Point Scoring Matrix Engine for Arthaprama.

This module houses the master profile-aware 100-point scoring algorithm as
defined in Section 6 of the IPO Analysis Framework. It codifies the evaluation
engine dividing 100 points across four major financial pillars:

- Growth Scoring (Max 30 points)
- Risk Scoring (Max 30 points)
- Valuation Scoring (Max 30 points)
- IPO/Management Quality Inputs (Max 10 points)

The scoring engine accepts optional profile inputs from arthaprama.config
and dynamically reads weighted mapping parameters instead of fallback
hardcoded scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from arthaprama.config import InvestorProfile, get_profile
from arthaprama.ipo.growth import calculate_all_growth_metrics
from arthaprama.ipo.risk import calculate_all_risk_metrics
from arthaprama.ipo.valuation import calculate_all_valuation_metrics


@dataclass
class ScoreBreakdown:
    """
    Detailed breakdown of scores across all pillars.

    Attributes:
        growth_score: Score out of maximum growth weight (default 30).
        risk_score: Score out of maximum risk weight (default 30).
        valuation_score: Score out of maximum valuation weight (default 30).
        ipo_quality_score: Score out of maximum IPO quality weight (default 10).
        total_score: Sum of all pillar scores (out of 100).
        growth_details: Detailed metrics contributing to growth score.
        risk_details: Detailed metrics contributing to risk score.
        valuation_details: Detailed metrics contributing to valuation score.
        ipo_quality_details: Detailed metrics contributing to IPO quality score.
    """

    growth_score: Decimal = Decimal(0)
    risk_score: Decimal = Decimal(0)
    valuation_score: Decimal = Decimal(0)
    ipo_quality_score: Decimal = Decimal(0)
    total_score: Decimal = Decimal(0)
    growth_details: dict[str, Any] = field(default_factory=dict)
    risk_details: dict[str, Any] = field(default_factory=dict)
    valuation_details: dict[str, Any] = field(default_factory=dict)
    ipo_quality_details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert score breakdown to dictionary format."""
        return {
            "growth_score": float(self.growth_score),
            "risk_score": float(self.risk_score),
            "valuation_score": float(self.valuation_score),
            "ipo_quality_score": float(self.ipo_quality_score),
            "total_score": float(self.total_score),
            "growth_details": self.growth_details,
            "risk_details": self.risk_details,
            "valuation_details": self.valuation_details,
            "ipo_quality_details": self.ipo_quality_details,
        }


def _normalize_to_scale(value: Decimal, min_val: Decimal, max_val: Decimal, scale: Decimal) -> Decimal:
    """
    Normalize a value to a given scale based on min/max bounds.

    Args:
        value: The value to normalize.
        min_val: Minimum acceptable value.
        max_val: Maximum acceptable value.
        scale: The target scale (e.g., 10 for scoring out of 10).

    Returns:
        Normalized score on the given scale.
    """
    if max_val == min_val:
        return scale / Decimal(2)

    # Calculate position between min and max
    range_val = max_val - min_val
    position = (value - min_val) / range_val

    # Clamp position between 0 and 1
    position = max(Decimal(0), min(Decimal(1), position))

    return (position * scale).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _calculate_growth_score(
    growth_metrics: dict[str, Decimal],
    thresholds: dict[str, Decimal],
    max_points: Decimal,
) -> tuple[Decimal, dict[str, Any]]:
    """
    Calculate growth pillar score based on metrics and thresholds.

    Args:
        growth_metrics: Dictionary of calculated growth metrics.
        thresholds: Threshold configuration from investor profile.
        max_points: Maximum points available for growth pillar.

    Returns:
        Tuple of (score, details dictionary).
    """
    details: dict[str, Any] = {}
    sub_scores: list[Decimal] = []

    # Revenue Growth YoY (weight: 2 within growth)
    rev_growth = growth_metrics.get("revenue_growth_yoy", Decimal(0))
    details["revenue_growth_yoy"] = {
        "value": float(rev_growth),
        "threshold": float(thresholds.get("min_revenue_growth", Decimal(10))),
    }
    sub_scores.append(_normalize_to_scale(rev_growth, Decimal(0), Decimal(50), Decimal(2)))

    # Profit Growth YoY (weight: 3 within growth)
    profit_growth = growth_metrics.get("profit_growth_yoy", Decimal(0))
    details["profit_growth_yoy"] = {
        "value": float(profit_growth),
        "threshold": float(thresholds.get("min_profit_growth", Decimal(15))),
    }
    sub_scores.append(_normalize_to_scale(profit_growth, Decimal(0), Decimal(50), Decimal(3)))

    # EBITDA Growth YoY (weight: 2 within growth)
    ebitda_growth = growth_metrics.get("ebitda_growth_yoy", Decimal(0))
    details["ebitda_growth_yoy"] = {
        "value": float(ebitda_growth),
        "threshold": float(thresholds.get("min_ebitda_growth", Decimal(10))),
    }
    sub_scores.append(_normalize_to_scale(ebitda_growth, Decimal(0), Decimal(50), Decimal(2)))

    # EPS Growth YoY (weight: 2 within growth)
    eps_growth = growth_metrics.get("eps_growth_yoy", Decimal(0))
    details["eps_growth_yoy"] = {
        "value": float(eps_growth),
        "threshold": float(thresholds.get("min_eps_growth", Decimal(10))),
    }
    sub_scores.append(_normalize_to_scale(eps_growth, Decimal(0), Decimal(50), Decimal(2)))

    # Revenue CAGR 3yr (weight: 3 within growth)
    rev_cagr = growth_metrics.get("revenue_cagr_3yr", Decimal(0)) * Decimal(100)
    details["revenue_cagr_3yr"] = {
        "value": float(rev_cagr),
        "threshold": float(thresholds.get("min_cagr", Decimal(15))),
    }
    sub_scores.append(_normalize_to_scale(rev_cagr, Decimal(0), Decimal(50), Decimal(3)))

    # PAT CAGR 3yr (weight: 3 within growth)
    pat_cagr = growth_metrics.get("pat_cagr_3yr", Decimal(0)) * Decimal(100)
    details["pat_cagr_3yr"] = {
        "value": float(pat_cagr),
        "threshold": float(thresholds.get("min_cagr", Decimal(15))),
    }
    sub_scores.append(_normalize_to_scale(pat_cagr, Decimal(0), Decimal(50), Decimal(3)))

    # EBITDA Margin (weight: 2 within growth)
    ebitda_margin = growth_metrics.get("ebitda_margin", Decimal(0))
    details["ebitda_margin"] = {
        "value": float(ebitda_margin),
        "threshold": float(thresholds.get("min_ebitda_margin", Decimal(10))),
    }
    sub_scores.append(_normalize_to_scale(ebitda_margin, Decimal(0), Decimal(40), Decimal(2)))

    # PAT Margin (weight: 2 within growth)
    pat_margin = growth_metrics.get("pat_margin", Decimal(0))
    details["pat_margin"] = {
        "value": float(pat_margin),
        "threshold": float(thresholds.get("min_pat_margin", Decimal(5))),
    }
    sub_scores.append(_normalize_to_scale(pat_margin, Decimal(0), Decimal(30), Decimal(2)))

    # ROE (weight: 3 within growth)
    roe = growth_metrics.get("roe", Decimal(0))
    details["roe"] = {
        "value": float(roe),
        "threshold": float(thresholds.get("min_roe", Decimal(15))),
    }
    sub_scores.append(_normalize_to_scale(roe, Decimal(0), Decimal(40), Decimal(3)))

    # ROCE (weight: 3 within growth)
    roce = growth_metrics.get("roce", Decimal(0))
    details["roce"] = {
        "value": float(roce),
        "threshold": float(thresholds.get("min_roce", Decimal(15))),
    }
    sub_scores.append(_normalize_to_scale(roce, Decimal(0), Decimal(40), Decimal(3)))

    # CFO Growth (weight: 2 within growth)
    cfo_growth = growth_metrics.get("cfo_growth", Decimal(0))
    details["cfo_growth"] = {
        "value": float(cfo_growth),
        "threshold": float(thresholds.get("min_cfo_growth", Decimal(10))),
    }
    sub_scores.append(_normalize_to_scale(cfo_growth, Decimal(0), Decimal(50), Decimal(2)))

    total = sum(sub_scores)
    # Scale to max_points
    normalized_score = _normalize_to_scale(total, Decimal(0), Decimal(27), max_points)

    return normalized_score, details


def _calculate_risk_score(
    risk_metrics: dict[str, Decimal],
    thresholds: dict[str, Decimal],
    max_points: Decimal,
) -> tuple[Decimal, dict[str, Any]]:
    """
    Calculate risk pillar score based on metrics and thresholds.

    Lower risk = Higher score. Inverse relationship for most metrics.

    Args:
        risk_metrics: Dictionary of calculated risk metrics.
        thresholds: Threshold configuration from investor profile.
        max_points: Maximum points available for risk pillar.

    Returns:
        Tuple of (score, details dictionary).
    """
    details: dict[str, Any] = {}
    sub_scores: list[Decimal] = []

    # Debt-to-Equity (lower is better, weight: 4)
    dte = risk_metrics.get("debt_to_equity", Decimal(0))
    max_dte = thresholds.get("max_debt_to_equity", Decimal("2.0"))
    details["debt_to_equity"] = {"value": float(dte), "threshold": float(max_dte)}
    # Inverse scoring: 0 DTE = full points, max_dte = 0 points
    dte_score = max(Decimal(0), (max_dte - dte) / max_dte) * Decimal(4)
    sub_scores.append(dte_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Net Debt to EBITDA (lower is better, weight: 3)
    nd_ebitda = risk_metrics.get("net_debt_to_ebitda", Decimal(0))
    max_nd = Decimal(5)  # Industry standard max
    details["net_debt_to_ebitda"] = {
        "value": float(nd_ebitda),
        "threshold": float(max_nd),
    }
    nd_score = max(Decimal(0), (max_nd - nd_ebitda) / max_nd) * Decimal(3)
    sub_scores.append(nd_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Interest Coverage (higher is better, weight: 4)
    ic = risk_metrics.get("interest_coverage", Decimal(0))
    min_ic = thresholds.get("min_interest_coverage", Decimal("2.0"))
    details["interest_coverage"] = {"value": float(ic), "threshold": float(min_ic)}
    ic_score = _normalize_to_scale(ic, Decimal(0), Decimal(10), Decimal(4))
    sub_scores.append(ic_score)

    # Current Ratio (higher is better up to a point, weight: 3)
    cr = risk_metrics.get("current_ratio", Decimal(0))
    min_cr = thresholds.get("min_current_ratio", Decimal("1.5"))
    details["current_ratio"] = {"value": float(cr), "threshold": float(min_cr)}
    cr_score = _normalize_to_scale(cr, Decimal(0), Decimal(4), Decimal(3))
    sub_scores.append(cr_score)

    # Quick Ratio (weight: 2)
    qr = risk_metrics.get("quick_ratio", Decimal(0))
    details["quick_ratio"] = {"value": float(qr), "threshold": 1.0}
    qr_score = _normalize_to_scale(qr, Decimal(0), Decimal(3), Decimal(2))
    sub_scores.append(qr_score)

    # CFO to Debt (higher is better, weight: 3)
    cfo_d = risk_metrics.get("cfo_to_debt", Decimal(0))
    details["cfo_to_debt"] = {"value": float(cfo_d), "threshold": 0.3}
    cfo_d_score = _normalize_to_scale(cfo_d, Decimal(0), Decimal(1), Decimal(3))
    sub_scores.append(cfo_d_score)

    # CFO to PAT (quality of earnings, weight: 3)
    cfo_p = risk_metrics.get("cfo_to_pat", Decimal(0))
    details["cfo_to_pat"] = {"value": float(cfo_p), "threshold": 1.0}
    cfo_p_score = _normalize_to_scale(cfo_p, Decimal(0), Decimal(2), Decimal(3))
    sub_scores.append(cfo_p_score)

    # FCF to PAT (weight: 2)
    fcf_p = risk_metrics.get("fcf_to_pat", Decimal(0))
    details["fcf_to_pat"] = {"value": float(fcf_p), "threshold": 0.8}
    fcf_p_score = _normalize_to_scale(fcf_p, Decimal(0), Decimal("1.5"), Decimal(2))
    sub_scores.append(fcf_p_score)

    # Customer Concentration (lower is better, weight: 2)
    cc = risk_metrics.get("customer_concentration", Decimal(0))
    max_cc = thresholds.get("max_customer_concentration", Decimal(50))
    details["customer_concentration"] = {"value": float(cc), "threshold": float(max_cc)}
    cc_score = max(Decimal(0), (max_cc - cc) / max_cc) * Decimal(2)
    sub_scores.append(cc_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Promoter Pledge (lower is better, weight: 3)
    pp = risk_metrics.get("promoter_pledge_ratio", Decimal(0))
    max_pp = thresholds.get("max_promoter_pledge", Decimal(20))
    details["promoter_pledge_ratio"] = {"value": float(pp), "threshold": float(max_pp)}
    pp_score = max(Decimal(0), (max_pp - pp) / max_pp) * Decimal(3)
    sub_scores.append(pp_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Contingent Liabilities to NW (lower is better, weight: 2)
    cl_nw = risk_metrics.get("contingent_liabilities_to_nw", Decimal(0))
    max_cl = Decimal(50)
    details["contingent_liabilities_to_nw"] = {
        "value": float(cl_nw),
        "threshold": float(max_cl),
    }
    cl_score = max(Decimal(0), (max_cl - cl_nw) / max_cl) * Decimal(2)
    sub_scores.append(cl_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    total = sum(sub_scores)
    normalized_score = _normalize_to_scale(total, Decimal(0), Decimal(28), max_points)

    return normalized_score, details


def _calculate_valuation_score(
    valuation_metrics: dict[str, Decimal],
    thresholds: dict[str, Decimal],
    max_points: Decimal,
) -> tuple[Decimal, dict[str, Any]]:
    """
    Calculate valuation pillar score based on metrics and thresholds.

    Lower valuations = Higher score (value investing approach).

    Args:
        valuation_metrics: Dictionary of calculated valuation metrics.
        thresholds: Threshold configuration from investor profile.
        max_points: Maximum points available for valuation pillar.

    Returns:
        Tuple of (score, details dictionary).
    """
    details: dict[str, Any] = {}
    sub_scores: list[Decimal] = []

    # P/E Ratio (lower is better, weight: 5)
    pe = valuation_metrics.get("pe_ratio", Decimal(0))
    max_pe = thresholds.get("max_pe_ratio", Decimal(40))
    details["pe_ratio"] = {"value": float(pe), "threshold": float(max_pe)}
    pe_score = max(Decimal(0), (max_pe - pe) / max_pe) * Decimal(5)
    sub_scores.append(pe_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # P/B Ratio (lower is better, weight: 3)
    pb = valuation_metrics.get("pb_ratio", Decimal(0))
    max_pb = Decimal(10)
    details["pb_ratio"] = {"value": float(pb), "threshold": float(max_pb)}
    pb_score = max(Decimal(0), (max_pb - pb) / max_pb) * Decimal(3)
    sub_scores.append(pb_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # P/S Ratio (lower is better, weight: 3)
    ps = valuation_metrics.get("ps_ratio", Decimal(0))
    max_ps = Decimal(15)
    details["ps_ratio"] = {"value": float(ps), "threshold": float(max_ps)}
    ps_score = max(Decimal(0), (max_ps - ps) / max_ps) * Decimal(3)
    sub_scores.append(ps_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # EV/EBITDA (lower is better, weight: 5)
    ev_eb = valuation_metrics.get("ev_to_ebitda", Decimal(0))
    max_ev_eb = Decimal(20)
    details["ev_to_ebitda"] = {"value": float(ev_eb), "threshold": float(max_ev_eb)}
    ev_eb_score = max(Decimal(0), (max_ev_eb - ev_eb) / max_ev_eb) * Decimal(5)
    sub_scores.append(ev_eb_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # PEG Ratio (lower is better, weight: 5)
    peg = valuation_metrics.get("peg_ratio", Decimal(0))
    max_peg = thresholds.get("max_peg_ratio", Decimal("2.0"))
    details["peg_ratio"] = {"value": float(peg), "threshold": float(max_peg)}
    peg_score = max(Decimal(0), (max_peg - peg) / max_peg) * Decimal(5)
    sub_scores.append(peg_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Earnings Yield (higher is better, weight: 3)
    ey = valuation_metrics.get("earnings_yield", Decimal(0))
    details["earnings_yield"] = {"value": float(ey), "threshold": 3.0}
    ey_score = _normalize_to_scale(ey, Decimal(0), Decimal(15), Decimal(3))
    sub_scores.append(ey_score)

    # Price to FCF (lower is better, weight: 3)
    p_fcf = valuation_metrics.get("price_to_fcf", Decimal(0))
    max_p_fcf = Decimal(30)
    details["price_to_fcf"] = {"value": float(p_fcf), "threshold": float(max_p_fcf)}
    p_fcf_score = max(Decimal(0), (max_p_fcf - p_fcf) / max_p_fcf) * Decimal(3)
    sub_scores.append(p_fcf_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # P/E Premium vs Peer (lower/negative is better, weight: 3)
    pe_premium = valuation_metrics.get("pe_premium_vs_peer", Decimal(0))
    details["pe_premium_vs_peer"] = {"value": float(pe_premium), "threshold": 0}
    # Negative premium (discount) gets full points
    pe_prem_score = max(Decimal(0), (Decimal(50) - pe_premium) / Decimal(50)) * Decimal(3)
    sub_scores.append(pe_prem_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    total = sum(sub_scores)
    normalized_score = _normalize_to_scale(total, Decimal(0), Decimal(30), max_points)

    return normalized_score, details


def _calculate_ipo_quality_score(
    ipo_data: dict[str, Any],
    thresholds: dict[str, Decimal],
    max_points: Decimal,
) -> tuple[Decimal, dict[str, Any]]:
    """
    Calculate IPO/Management quality pillar score.

    This includes IPO-specific factors like dilution, promoter holdings, etc.

    Args:
        ipo_data: Dictionary containing IPO-specific data.
        thresholds: Threshold configuration from investor profile.
        max_points: Maximum points available for IPO quality pillar.

    Returns:
        Tuple of (score, details dictionary).
    """
    details: dict[str, Any] = {}
    sub_scores: list[Decimal] = []

    # IPO Dilution (lower is better, weight: 3)
    dilution = ipo_data.get("ipo_dilution", Decimal(0))
    if isinstance(dilution, (int, float)):
        dilution = Decimal(str(dilution))
    max_dilution = Decimal(25)  # Max acceptable dilution
    details["ipo_dilution"] = {
        "value": float(dilution),
        "threshold": float(max_dilution),
    }
    dilution_score = max(Decimal(0), (max_dilution - dilution) / max_dilution) * Decimal(3)
    sub_scores.append(dilution_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Promoter Holding Post-IPO (higher is better, weight: 4)
    promoter_holding = ipo_data.get("promoter_holding_post_ipo", Decimal(0))
    if isinstance(promoter_holding, (int, float)):
        promoter_holding = Decimal(str(promoter_holding))
    details["promoter_holding_post_ipo"] = {
        "value": float(promoter_holding),
        "threshold": 50.0,
    }
    ph_score = _normalize_to_scale(promoter_holding, Decimal(0), Decimal(100), Decimal(4))
    sub_scores.append(ph_score)

    # Promoter Pledge (already in risk, but also relevant here, weight: 3)
    pledge = ipo_data.get("promoter_pledge_ratio", Decimal(0))
    if isinstance(pledge, (int, float)):
        pledge = Decimal(str(pledge))
    max_pledge = thresholds.get("max_promoter_pledge", Decimal(20))
    details["promoter_pledge_ratio"] = {
        "value": float(pledge),
        "threshold": float(max_pledge),
    }
    pledge_score = max(Decimal(0), (max_pledge - pledge) / max_pledge) * Decimal(3)
    sub_scores.append(pledge_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    total = sum(sub_scores)
    normalized_score = _normalize_to_scale(total, Decimal(0), Decimal(10), max_points)

    return normalized_score, details


def generate_ipo_score(
    growth_data: dict[str, Any],
    risk_data: dict[str, Any],
    valuation_data: dict[str, Any],
    ipo_data: dict[str, Any],
    profile: str | InvestorProfile | None = None,
    peer_data: dict[str, Any] | None = None,
) -> ScoreBreakdown:
    """
    Generate comprehensive 100-point IPO evaluation score.

    This is the flagship evaluation wrapper that codifies Section 6 of the
    IPO Analysis Framework. It processes mathematical scores using the active
    profile weight ceilings across all four pillars.

    Args:
        growth_data: Financial data for growth calculations including:
            - revenue_current, revenue_previous, revenue_3yrs_ago
            - pat_current, pat_previous, pat_3yrs_ago
            - ebitda_current, ebitda_previous
            - eps_current, eps_previous
            - ebit, cfo_current, cfo_previous
            - avg_shareholders_equity, capital_employed
        risk_data: Financial data for risk calculations including:
            - total_debt, shareholders_equity, cash_equivalents
            - ebitda, ebit, interest_expense
            - current_assets, current_liabilities, inventory
            - cfo, pat, capex
            - largest_customer_rev, total_rev
            - pledged_shares, total_promoter_shares
            - contingent_liabilities, net_worth
        valuation_data: Financial data for valuation calculations including:
            - market_cap, pat, book_value, revenue
            - ebitda, eps, ipo_price
            - total_debt, cash_equivalents
            - free_cash_flow
            - new_shares, post_ipo_shares, post_ipo_diluted_shares, post_ipo_pat
            - expected_eps_growth_pct
        ipo_data: IPO-specific data including:
            - ipo_dilution, promoter_holding_post_ipo, promoter_pledge_ratio
        profile: Optional investor profile (string name or InvestorProfile instance).
                 If None, uses balanced profile.
        peer_data: Optional peer comparison data for relative valuation.

    Returns:
        ScoreBreakdown object with detailed scores across all pillars.

    Example:
        >>> result = generate_ipo_score(
        ...     growth_data={"revenue_current": 1200, "revenue_previous": 1000, ...},
        ...     risk_data={"total_debt": 200, "shareholders_equity": 800, ...},
        ...     valuation_data={"market_cap": 2000, "pat": 100, ...},
        ...     ipo_data={"promoter_holding_post_ipo": 60},
        ...     profile="conservative"
        ... )
        >>> print(result.total_score)
        72.5
    """
    # Resolve profile
    if profile is None:
        investor_profile = get_profile("balanced")
    elif isinstance(profile, str):
        investor_profile = get_profile(profile)
    else:
        investor_profile = profile

    # Get weights and thresholds for IPO asset type
    weights = investor_profile.get_weights_for_asset("ipo")
    thresholds = investor_profile.get_thresholds_for_asset("ipo")

    # Calculate all metrics
    growth_metrics = calculate_all_growth_metrics(growth_data)
    risk_metrics = calculate_all_risk_metrics(risk_data)
    valuation_metrics = calculate_all_valuation_metrics(valuation_data, peer_data)

    # Calculate pillar scores
    growth_score, growth_details = _calculate_growth_score(growth_metrics, thresholds, weights["growth"])

    risk_score, risk_details = _calculate_risk_score(risk_metrics, thresholds, weights["risk"])

    valuation_score, valuation_details = _calculate_valuation_score(valuation_metrics, thresholds, weights["valuation"])

    ipo_quality_score, ipo_quality_details = _calculate_ipo_quality_score(ipo_data, thresholds, weights["ipo_quality"])

    # Calculate total score
    total_score = (growth_score + risk_score + valuation_score + ipo_quality_score).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return ScoreBreakdown(
        growth_score=growth_score,
        risk_score=risk_score,
        valuation_score=valuation_score,
        ipo_quality_score=ipo_quality_score,
        total_score=total_score,
        growth_details={
            "metrics": {k: float(v) for k, v in growth_metrics.items()},
            "scoring": growth_details,
        },
        risk_details={
            "metrics": {k: float(v) for k, v in risk_metrics.items()},
            "scoring": risk_details,
        },
        valuation_details={
            "metrics": {k: float(v) for k, v in valuation_metrics.items()},
            "scoring": valuation_details,
        },
        ipo_quality_details={
            "metrics": {k: float(v) if isinstance(v, Decimal) else v for k, v in ipo_data.items()},
            "scoring": ipo_quality_details,
        },
    )
