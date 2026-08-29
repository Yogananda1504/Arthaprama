"""Model Context Protocol server exposing Arthaprama IPO analysis tools."""

from __future__ import annotations

from decimal import Decimal
from statistics import pstdev
from typing import Any, Sequence

from mcp.server.fastmcp import FastMCP

from arthaprama.ipo import growth, risk, scoring, valuation, workflow

mcp = FastMCP("Arthaprama IPO Intelligence Engine")


def _to_decimal(value: int | float | str | Decimal) -> Decimal:
    """Convert numeric input into ``Decimal`` for stable financial calculations."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _serialize(value: Any) -> Any:
    """Recursively convert decimals and nested objects into JSON-safe values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if hasattr(value, "to_dict"):
        return _serialize(value.to_dict())
    return value


def _score_tier(total_score: float) -> tuple[str, str]:
    """Map a 0-100 score to a rating tier and recommendation."""
    if total_score >= 80:
        return "Strong", "Attractive IPO profile. Consider with standard due diligence."
    if total_score >= 65:
        return "Moderate", "Reasonable fundamentals; validate assumptions before subscribing."
    if total_score >= 50:
        return "Watchlist", "Mixed signals; proceed only with higher risk tolerance."
    return "Weak", "High-risk setup; avoid unless thesis is highly specialized."


def _extract_input_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Allow passing either raw input dictionaries or prior MCP tool outputs."""
    if "input_data" in payload and isinstance(payload["input_data"], dict):
        return payload["input_data"]
    return payload


@mcp.tool(
    name="calculate_ipo_growth",
    description="Compute IPO growth trends, CAGR metrics, and stability against industry averages.",
)
def calculate_ipo_growth(
    historical_revenues: Sequence[float],
    historical_ebitda_margins: Sequence[float],
    industry_average_revenue_cagr_pct: float,
    industry_average_ebitda_margin_pct: float,
) -> dict[str, Any]:
    """
    Calculate IPO growth momentum and stability metrics.

    Args:
        historical_revenues: Chronological revenue values (oldest to latest), at least 3 points.
        historical_ebitda_margins: EBITDA margins in percentage aligned with revenue history.
        industry_average_revenue_cagr_pct: Industry benchmark revenue CAGR in percentage terms.
        industry_average_ebitda_margin_pct: Industry benchmark EBITDA margin percentage.

    Returns:
        Dictionary containing revenue and EBITDA CAGR, growth/margin stability statistics,
        and industry-relative deltas.
    """
    if len(historical_revenues) < 3:
        raise ValueError("historical_revenues must contain at least 3 data points")
    if len(historical_revenues) != len(historical_ebitda_margins):
        raise ValueError("historical_revenues and historical_ebitda_margins must have equal lengths")

    revenues = [_to_decimal(value) for value in historical_revenues]
    margins = [_to_decimal(value) for value in historical_ebitda_margins]
    ebitda_values = [(rev * margin) / Decimal("100") for rev, margin in zip(revenues, margins)]

    revenue_cagr = growth.revenue_cagr_3yr(revenues[-1], revenues[0]) * Decimal("100")
    ebitda_cagr = growth.revenue_cagr_3yr(ebitda_values[-1], ebitda_values[0]) * Decimal("100")
    yoy_growth_rates = [
        growth.revenue_growth_yoy(revenues[index], revenues[index - 1])
        for index in range(1, len(revenues))
    ]

    margin_mean = sum(margins) / Decimal(str(len(margins)))
    growth_stability = Decimal(str(pstdev([float(value) for value in yoy_growth_rates])))
    margin_stability = Decimal(str(pstdev([float(value) for value in margins])))

    result = {
        "revenue_cagr_pct": revenue_cagr,
        "ebitda_cagr_pct": ebitda_cagr,
        "average_ebitda_margin_pct": margin_mean,
        "revenue_growth_stability_stddev": growth_stability,
        "margin_stability_stddev": margin_stability,
        "industry_gap_revenue_cagr_pct": revenue_cagr - _to_decimal(industry_average_revenue_cagr_pct),
        "industry_gap_ebitda_margin_pct": margin_mean - _to_decimal(industry_average_ebitda_margin_pct),
        "input_data": {
            "revenue_current": revenues[-1],
            "revenue_previous": revenues[-2],
            "revenue_3yrs_ago": revenues[0],
            "ebitda_current": ebitda_values[-1],
            "ebitda_previous": ebitda_values[-2],
        },
    }
    return _serialize(result)


@mcp.tool(
    name="evaluate_ipo_risk",
    description="Evaluate leverage, governance, concentration, and litigation risks with penalties.",
)
def evaluate_ipo_risk(
    total_debt: float,
    shareholders_equity: float,
    cash_equivalents: float,
    ebitda: float,
    ebit: float,
    interest_expense: float,
    promoter_holding_post_ipo: float,
    promoter_pledge_ratio: float,
    litigation_cases: int,
    customer_concentration_pct: float,
) -> dict[str, Any]:
    """
    Build a consolidated IPO risk matrix from financial and governance indicators.

    Args:
        total_debt: Total debt outstanding.
        shareholders_equity: Total shareholders' equity.
        cash_equivalents: Cash and cash-equivalent reserves.
        ebitda: Earnings before interest, taxes, depreciation, and amortization.
        ebit: Earnings before interest and taxes.
        interest_expense: Total annual interest expense.
        promoter_holding_post_ipo: Promoter shareholding percentage after IPO.
        promoter_pledge_ratio: Percent of promoter shares pledged.
        litigation_cases: Count of active material litigation cases.
        customer_concentration_pct: Revenue concentration with largest customer in percentage.

    Returns:
        Dictionary containing risk metrics, penalty ledger, and normalized risk score.
    """
    net_debt_value = risk.net_debt(total_debt, cash_equivalents)
    debt_to_equity_value = risk.debt_to_equity(total_debt, shareholders_equity)
    net_debt_to_ebitda_value = risk.net_debt_to_ebitda(net_debt_value, ebitda)
    interest_coverage_value = risk.interest_coverage(ebit, interest_expense)

    penalties: dict[str, int] = {
        "leverage_penalty": 15 if debt_to_equity_value > Decimal("1") else 0,
        "net_debt_penalty": 15 if net_debt_to_ebitda_value > Decimal("3") else 0,
        "coverage_penalty": 20 if interest_coverage_value < Decimal("2") else 0,
        "promoter_holding_penalty": 10 if promoter_holding_post_ipo < 50 else 0,
        "promoter_pledge_penalty": 10 if promoter_pledge_ratio > 20 else 0,
        "customer_concentration_penalty": 10 if customer_concentration_pct > 30 else 0,
        "litigation_penalty": min(max(litigation_cases, 0) * 2, 15),
    }
    total_penalty = sum(penalties.values())
    normalized_risk_score = max(0, 100 - total_penalty)

    if normalized_risk_score >= 75:
        risk_tier = "Low Risk"
    elif normalized_risk_score >= 55:
        risk_tier = "Moderate Risk"
    else:
        risk_tier = "High Risk"

    result = {
        "risk_matrix": {
            "debt_to_equity": debt_to_equity_value,
            "net_debt": net_debt_value,
            "net_debt_to_ebitda": net_debt_to_ebitda_value,
            "interest_coverage": interest_coverage_value,
            "promoter_holding_post_ipo": _to_decimal(promoter_holding_post_ipo),
            "promoter_pledge_ratio": _to_decimal(promoter_pledge_ratio),
            "customer_concentration_pct": _to_decimal(customer_concentration_pct),
            "litigation_cases": litigation_cases,
        },
        "penalties": penalties,
        "total_penalty": total_penalty,
        "normalized_risk_score": normalized_risk_score,
        "risk_tier": risk_tier,
        "input_data": {
            "total_debt": _to_decimal(total_debt),
            "shareholders_equity": _to_decimal(shareholders_equity),
            "cash_equivalents": _to_decimal(cash_equivalents),
            "ebitda": _to_decimal(ebitda),
            "ebit": _to_decimal(ebit),
            "interest_expense": _to_decimal(interest_expense),
            "largest_customer_rev": _to_decimal(customer_concentration_pct),
            "total_rev": Decimal("100"),
        },
    }
    return _serialize(result)


@mcp.tool(
    name="model_ipo_valuation",
    description="Model price-band valuation, peer premium/discount, and fair-value range.",
)
def model_ipo_valuation(
    price_band_lower: float,
    price_band_upper: float,
    shares_offered: float,
    post_ipo_shares: float,
    projected_pat: float,
    projected_revenue: float,
    projected_ebitda: float,
    book_value: float,
    total_debt: float,
    cash_equivalents: float,
    expected_eps_growth_pct: float,
    peer_median_pe: float,
    peer_median_ev_ebitda: float,
    dcf_fair_value_lower: float | None = None,
    dcf_fair_value_upper: float | None = None,
) -> dict[str, Any]:
    """
    Produce IPO valuation analytics from price band, peer multiples, and DCF inputs.

    Args:
        price_band_lower: Lower bound of IPO price band.
        price_band_upper: Upper bound of IPO price band.
        shares_offered: Number of new shares offered in the IPO.
        post_ipo_shares: Post-issue total shares outstanding.
        projected_pat: Post-IPO projected PAT.
        projected_revenue: Post-IPO projected revenue.
        projected_ebitda: Post-IPO projected EBITDA.
        book_value: Post-IPO book value of equity.
        total_debt: Projected total debt.
        cash_equivalents: Projected cash balance.
        expected_eps_growth_pct: Forward EPS growth assumption in percent.
        peer_median_pe: Peer median P/E benchmark.
        peer_median_ev_ebitda: Peer median EV/EBITDA benchmark.
        dcf_fair_value_lower: Optional DCF-derived lower fair value.
        dcf_fair_value_upper: Optional DCF-derived upper fair value.

    Returns:
        Dictionary containing implied valuation ratios, peer premium/discount results,
        and consolidated fair-value bands.
    """
    price_mid = (_to_decimal(price_band_lower) + _to_decimal(price_band_upper)) / Decimal("2")
    post_ipo_shares_decimal = _to_decimal(post_ipo_shares)
    projected_pat_decimal = _to_decimal(projected_pat)

    valuation_data = {
        "market_cap": price_mid * post_ipo_shares_decimal,
        "pat": projected_pat_decimal,
        "book_value": _to_decimal(book_value),
        "revenue": _to_decimal(projected_revenue),
        "ebitda": _to_decimal(projected_ebitda),
        "eps": valuation.post_ipo_eps(projected_pat_decimal, post_ipo_shares_decimal),
        "ipo_price": price_mid,
        "total_debt": _to_decimal(total_debt),
        "cash_equivalents": _to_decimal(cash_equivalents),
        "free_cash_flow": projected_pat_decimal,
        "new_shares": _to_decimal(shares_offered),
        "post_ipo_shares": post_ipo_shares_decimal,
        "post_ipo_diluted_shares": post_ipo_shares_decimal,
        "post_ipo_pat": projected_pat_decimal,
        "expected_eps_growth_pct": _to_decimal(expected_eps_growth_pct),
    }
    peer_data = {
        "peer_median_pe": _to_decimal(peer_median_pe),
        "peer_median_ev_ebitda": _to_decimal(peer_median_ev_ebitda),
    }

    valuation_metrics = valuation.calculate_all_valuation_metrics(valuation_data, peer_data)

    peer_implied_price = (
        valuation_data["eps"] * _to_decimal(peer_median_pe) if _to_decimal(peer_median_pe) > 0 else Decimal("0")
    )
    lower_candidates = [
        _to_decimal(dcf_fair_value_lower) if dcf_fair_value_lower is not None else Decimal("0"),
        peer_implied_price * Decimal("0.90") if peer_implied_price > 0 else Decimal("0"),
    ]
    upper_candidates = [
        _to_decimal(dcf_fair_value_upper) if dcf_fair_value_upper is not None else Decimal("0"),
        peer_implied_price * Decimal("1.10") if peer_implied_price > 0 else Decimal("0"),
    ]

    valid_lowers = [value for value in lower_candidates if value > 0]
    valid_uppers = [value for value in upper_candidates if value > 0]
    fair_value_lower = min(valid_lowers) if valid_lowers else _to_decimal(price_band_lower)
    fair_value_upper = max(valid_uppers) if valid_uppers else _to_decimal(price_band_upper)
    fair_value_mid = (fair_value_lower + fair_value_upper) / Decimal("2")

    result = {
        "valuation_metrics": valuation_metrics,
        "price_band_analysis": {
            "price_band_lower": _to_decimal(price_band_lower),
            "price_band_upper": _to_decimal(price_band_upper),
            "price_band_mid": price_mid,
            "market_cap_lower": _to_decimal(price_band_lower) * post_ipo_shares_decimal,
            "market_cap_upper": _to_decimal(price_band_upper) * post_ipo_shares_decimal,
            "ipo_dilution_pct": valuation.ipo_dilution(shares_offered, post_ipo_shares),
        },
        "peer_discount_premium_pct": valuation_metrics.get("pe_premium_vs_peer", Decimal("0")),
        "fair_value_band": {
            "lower": fair_value_lower,
            "upper": fair_value_upper,
            "mid": fair_value_mid,
            "midpoint_premium_discount_pct": (
                ((price_mid - fair_value_mid) / fair_value_mid) * Decimal("100")
                if fair_value_mid > 0
                else Decimal("0")
            ),
        },
        "input_data": valuation_data,
        "peer_data": peer_data,
    }
    return _serialize(result)


@mcp.tool(
    name="generate_composite_ipo_score",
    description="Generate weighted composite IPO score, rating tier, and recommendation.",
)
def generate_composite_ipo_score(
    growth_data: dict[str, Any],
    risk_data: dict[str, Any],
    valuation_data: dict[str, Any],
    ipo_data: dict[str, Any],
    profile: str = "balanced",
    peer_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a profile-aware composite IPO score from growth, risk, and valuation inputs.

    Args:
        growth_data: Growth inputs or prior tool output containing ``input_data``.
        risk_data: Risk inputs or prior tool output containing ``input_data``.
        valuation_data: Valuation inputs or prior tool output containing ``input_data``.
        ipo_data: IPO quality factors such as dilution and promoter holdings.
        profile: Investor profile strategy (balanced, conservative, aggressive_growth, deep_value).
        peer_data: Optional peer benchmark inputs.

    Returns:
        Dictionary with numeric score breakdown, rating tier, and recommendation text.
    """
    normalized_growth_data = _extract_input_payload(growth_data)
    normalized_risk_data = _extract_input_payload(risk_data)
    normalized_valuation_data = _extract_input_payload(valuation_data)

    score_breakdown = scoring.generate_ipo_score(
        growth_data=normalized_growth_data,
        risk_data=normalized_risk_data,
        valuation_data=normalized_valuation_data,
        ipo_data=ipo_data,
        profile=profile,
        peer_data=peer_data,
    )

    score_dict = score_breakdown.to_dict()
    tier, recommendation = _score_tier(score_dict["total_score"])

    return {
        "composite_score": score_dict,
        "rating_tier": tier,
        "recommendation": recommendation,
        "profile": profile,
    }


@mcp.tool(
    name="run_full_ipo_workflow",
    description="Run Arthaprama end-to-end IPO workflow and return a consolidated report.",
)
def run_full_ipo_workflow(
    meta: dict[str, Any],
    growth_data: dict[str, Any],
    risk_data: dict[str, Any],
    valuation_data: dict[str, Any],
    ipo_data: dict[str, Any],
    profile: str = "balanced",
    peer_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute the full IPO workflow pipeline in a single MCP tool invocation.

    Args:
        meta: IPO metadata payload (company, sector, issue details).
        growth_data: Inputs for growth analysis.
        risk_data: Inputs for risk analysis.
        valuation_data: Inputs for valuation analysis.
        ipo_data: IPO quality inputs.
        profile: Investor profile strategy used for scoring.
        peer_data: Optional peer benchmarks.

    Returns:
        Consolidated report including growth/risk/valuation analyses, composite score,
        and decision guidance.
    """
    full_result = workflow.run_full_ipo_analysis(
        growth_data=growth_data,
        risk_data=risk_data,
        valuation_data=valuation_data,
        ipo_data=ipo_data,
        profile=profile,
        peer_data=peer_data,
    )
    result_dict = _serialize(full_result.to_dict())

    total_score = (
        float(result_dict["composite_score"]["total_score"])
        if result_dict.get("composite_score") and result_dict["composite_score"].get("total_score") is not None
        else 0.0
    )
    tier, recommendation = _score_tier(total_score)

    return {
        "meta": meta,
        "analysis": result_dict,
        "rating_tier": tier,
        "recommendation": recommendation,
        "profile": profile,
    }


def create_mcp_sse_app() -> Any:
    """Create the ASGI app that serves MCP Server-Sent Events endpoints."""
    return mcp.sse_app()


if __name__ == "__main__":
    mcp.run(transport="stdio")
