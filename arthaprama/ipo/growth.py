"""
IPO Growth Engine for Arthaprama.

This module implements all core pre-IPO compounding and margin calculation formulas
as defined in Section 1 of the IPO Analysis Framework. It tracks historical operational
momentum prior to listing.

All calculations use Decimal arithmetic for precision and return Decimal values
to maintain mathematical accuracy throughout the computation chain.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any


class GrowthCalculationError(Exception):
    """Exception raised when growth calculations encounter invalid inputs."""



def _to_decimal(value: Any) -> Decimal:
    """
    Safely convert a value to Decimal for precise arithmetic.

    Args:
        value: Any numeric value (int, float, str, Decimal).

    Returns:
        Decimal representation of the input value.

    Raises:
        GrowthCalculationError: If conversion fails.
    """
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise GrowthCalculationError(f"Cannot convert '{value}' to Decimal") from e


def _safe_divide(numerator: Decimal, denominator: Decimal, default: Decimal = Decimal(0)) -> Decimal:
    """
    Safely divide two Decimals, returning a default on division by zero.

    Args:
        numerator: The dividend.
        denominator: The divisor.
        default: Value to return if denominator is zero.

    Returns:
        Result of division or default value.
    """
    if denominator == 0:
        return default
    return numerator / denominator


def revenue_growth_yoy(current: Any, previous: Any, precision: int = 4) -> Decimal:
    """
    Calculate Year-over-Year Revenue Growth percentage.

    Formula: (Current - Previous) / Previous * 100

    Args:
        current: Current period revenue.
        previous: Previous period revenue.
        precision: Number of decimal places for result.

    Returns:
        Revenue growth as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If previous revenue is zero or inputs are invalid.

    Example:
        >>> revenue_growth_yoy(1200, 1000)
        Decimal('20.0000')
    """
    current_rev = _to_decimal(current)
    prev_rev = _to_decimal(previous)

    if prev_rev == 0:
        raise GrowthCalculationError("Previous revenue cannot be zero")

    growth = ((current_rev - prev_rev) / prev_rev) * Decimal(100)
    return growth.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def profit_growth_yoy(current_pat: Any, previous_pat: Any, precision: int = 4) -> Decimal:
    """
    Calculate Year-over-Year Profit After Tax (PAT) Growth percentage.

    Formula: (Current PAT - Previous PAT) / Previous PAT * 100

    Args:
        current_pat: Current period PAT.
        previous_pat: Previous period PAT.
        precision: Number of decimal places for result.

    Returns:
        PAT growth as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If previous PAT is zero or inputs are invalid.

    Example:
        >>> profit_growth_yoy(150, 100)
        Decimal('50.0000')
    """
    current_profit = _to_decimal(current_pat)
    prev_profit = _to_decimal(previous_pat)

    if prev_profit == 0:
        raise GrowthCalculationError("Previous PAT cannot be zero")

    growth = ((current_profit - prev_profit) / prev_profit) * Decimal(100)
    return growth.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ebitda_growth_yoy(current_ebitda: Any, previous_ebitda: Any, precision: int = 4) -> Decimal:
    """
    Calculate Year-over-Year EBITDA Growth percentage.

    Formula: (Current EBITDA - Previous EBITDA) / Previous EBITDA * 100

    Args:
        current_ebitda: Current period EBITDA.
        previous_ebitda: Previous period EBITDA.
        precision: Number of decimal places for result.

    Returns:
        EBITDA growth as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If previous EBITDA is zero or inputs are invalid.

    Example:
        >>> ebitda_growth_yoy(220, 200)
        Decimal('10.0000')
    """
    current_eb = _to_decimal(current_ebitda)
    prev_eb = _to_decimal(previous_ebitda)

    if prev_eb == 0:
        raise GrowthCalculationError("Previous EBITDA cannot be zero")

    growth = ((current_eb - prev_eb) / prev_eb) * Decimal(100)
    return growth.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def eps_growth_yoy(current_eps: Any, previous_eps: Any, precision: int = 4) -> Decimal:
    """
    Calculate Year-over-Year Earnings Per Share (EPS) Growth percentage.

    Formula: (Current EPS - Previous EPS) / Previous EPS * 100

    Args:
        current_eps: Current period EPS.
        previous_eps: Previous period EPS.
        precision: Number of decimal places for result.

    Returns:
        EPS growth as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If previous EPS is zero or inputs are invalid.

    Example:
        >>> eps_growth_yoy(25, 20)
        Decimal('25.0000')
    """
    current_earnings = _to_decimal(current_eps)
    prev_earnings = _to_decimal(previous_eps)

    if prev_earnings == 0:
        raise GrowthCalculationError("Previous EPS cannot be zero")

    growth = ((current_earnings - prev_earnings) / prev_earnings) * Decimal(100)
    return growth.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def revenue_cagr_3yr(current_rev: Any, rev_3yrs_ago: Any, precision: int = 4) -> Decimal:
    """
    Calculate 3-Year Revenue Compound Annual Growth Rate (CAGR).

    Formula: (Current_Rev / Rev_3yrs_Ago) ** (1/3) - 1

    Note: Result is expressed as a decimal (e.g., 0.15 for 15%).
          Multiply by 100 for percentage representation.

    Args:
        current_rev: Current period revenue.
        rev_3yrs_ago: Revenue from 3 years ago.
        precision: Number of decimal places for result.

    Returns:
        3-year CAGR as a decimal (Decimal).

    Raises:
        GrowthCalculationError: If revenue 3 years ago is zero/negative or inputs invalid.

    Example:
        >>> revenue_cagr_3yr(1331, 1000)  # 10% CAGR
        Decimal('0.1000')
    """
    current = _to_decimal(current_rev)
    past = _to_decimal(rev_3yrs_ago)

    if past <= 0:
        raise GrowthCalculationError("Revenue 3 years ago must be positive")
    if current < 0:
        raise GrowthCalculationError("Current revenue cannot be negative")

    # CAGR = (End Value / Start Value)^(1/n) - 1
    ratio = current / past
    # Use logarithm for precise power calculation with Decimal
    # ratio ** (1/3) = exp(ln(ratio) / 3)
    cagr = ratio ** (Decimal(1) / Decimal(3)) - Decimal(1)
    return cagr.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def pat_cagr_3yr(current_pat: Any, pat_3yrs_ago: Any, precision: int = 4) -> Decimal:
    """
    Calculate 3-Year PAT Compound Annual Growth Rate (CAGR).

    Formula: (Current_PAT / PAT_3yrs_Ago) ** (1/3) - 1

    Note: Result is expressed as a decimal (e.g., 0.15 for 15%).
          Multiply by 100 for percentage representation.

    Args:
        current_pat: Current period PAT.
        pat_3yrs_ago: PAT from 3 years ago.
        precision: Number of decimal places for result.

    Returns:
        3-year PAT CAGR as a decimal (Decimal).

    Raises:
        GrowthCalculationError: If PAT 3 years ago is zero/negative or inputs invalid.

    Example:
        >>> pat_cagr_3yr(1728, 1000)  # 20% CAGR
        Decimal('0.2000')
    """
    current = _to_decimal(current_pat)
    past = _to_decimal(pat_3yrs_ago)

    if past <= 0:
        raise GrowthCalculationError("PAT 3 years ago must be positive")
    if current < 0:
        raise GrowthCalculationError("Current PAT cannot be negative")

    ratio = current / past
    cagr = ratio ** (Decimal(1) / Decimal(3)) - Decimal(1)
    return cagr.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ebitda_margin(ebitda: Any, revenue: Any, precision: int = 4) -> Decimal:
    """
    Calculate EBITDA Margin percentage.

    Formula: EBITDA / Revenue * 100

    Args:
        ebitda: Earnings Before Interest, Taxes, Depreciation, and Amortization.
        revenue: Total revenue.
        precision: Number of decimal places for result.

    Returns:
        EBITDA margin as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If revenue is zero or inputs are invalid.

    Example:
        >>> ebitda_margin(150, 1000)
        Decimal('15.0000')
    """
    eb = _to_decimal(ebitda)
    rev = _to_decimal(revenue)

    if rev == 0:
        raise GrowthCalculationError("Revenue cannot be zero")

    margin = (eb / rev) * Decimal(100)
    return margin.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def pat_margin(pat: Any, revenue: Any, precision: int = 4) -> Decimal:
    """
    Calculate Profit After Tax (PAT) Margin percentage.

    Formula: PAT / Revenue * 100

    Args:
        pat: Profit After Tax.
        revenue: Total revenue.
        precision: Number of decimal places for result.

    Returns:
        PAT margin as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If revenue is zero or inputs are invalid.

    Example:
        >>> pat_margin(100, 1000)
        Decimal('10.0000')
    """
    profit = _to_decimal(pat)
    rev = _to_decimal(revenue)

    if rev == 0:
        raise GrowthCalculationError("Revenue cannot be zero")

    margin = (profit / rev) * Decimal(100)
    return margin.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def roe(pat: Any, avg_shareholders_equity: Any, precision: int = 4) -> Decimal:
    """
    Calculate Return on Equity (ROE) percentage.

    Formula: PAT / Average Shareholders Equity * 100

    Args:
        pat: Profit After Tax.
        avg_shareholders_equity: Average shareholders' equity over the period.
        precision: Number of decimal places for result.

    Returns:
        ROE as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If equity is zero or inputs are invalid.

    Example:
        >>> roe(150, 1000)
        Decimal('15.0000')
    """
    profit = _to_decimal(pat)
    equity = _to_decimal(avg_shareholders_equity)

    if equity == 0:
        raise GrowthCalculationError("Shareholders equity cannot be zero")

    return_on_equity = (profit / equity) * Decimal(100)
    return return_on_equity.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def roce(ebit: Any, capital_employed: Any, precision: int = 4) -> Decimal:
    """
    Calculate Return on Capital Employed (ROCE) percentage.

    Formula: EBIT / Capital Employed * 100

    Args:
        ebit: Earnings Before Interest and Taxes.
        capital_employed: Total capital employed.
        precision: Number of decimal places for result.

    Returns:
        ROCE as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If capital employed is zero or inputs are invalid.

    Example:
        >>> roce(180, 1000)
        Decimal('18.0000')
    """
    earnings = _to_decimal(ebit)
    capital = _to_decimal(capital_employed)

    if capital == 0:
        raise GrowthCalculationError("Capital employed cannot be zero")

    return_on_capital = (earnings / capital) * Decimal(100)
    return return_on_capital.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def cfo_growth(current_cfo: Any, previous_cfo: Any, precision: int = 4) -> Decimal:
    """
    Calculate Year-over-Year Cash Flow from Operations (CFO) Growth percentage.

    Formula: (Current_CFO - Previous_CFO) / Previous_CFO * 100

    Args:
        current_cfo: Current period CFO.
        previous_cfo: Previous period CFO.
        precision: Number of decimal places for result.

    Returns:
        CFO growth as a percentage (Decimal).

    Raises:
        GrowthCalculationError: If previous CFO is zero or inputs are invalid.

    Example:
        >>> cfo_growth(220, 200)
        Decimal('10.0000')
    """
    current_flow = _to_decimal(current_cfo)
    prev_flow = _to_decimal(previous_cfo)

    if prev_flow == 0:
        raise GrowthCalculationError("Previous CFO cannot be zero")

    growth = ((current_flow - prev_flow) / prev_flow) * Decimal(100)
    return growth.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def calculate_all_growth_metrics(financial_data: dict[str, Any], precision: int = 4) -> dict[str, Decimal]:
    """
    Calculate all growth metrics from a comprehensive financial data dictionary.

    This convenience function processes a complete set of financial data and
    returns all applicable growth metrics in a single call.

    Args:
        financial_data: Dictionary containing the following keys:
            - revenue_current, revenue_previous, revenue_3yrs_ago
            - pat_current, pat_previous, pat_3yrs_ago
            - ebitda_current, ebitda_previous
            - eps_current, eps_previous
            - ebit
            - cfo_current, cfo_previous
            - avg_shareholders_equity
            - capital_employed
        precision: Number of decimal places for all results.

    Returns:
        Dictionary mapping metric names to their calculated Decimal values.
    """
    results: dict[str, Decimal] = {}

    try:
        results["revenue_growth_yoy"] = revenue_growth_yoy(
            financial_data.get("revenue_current", 0),
            financial_data.get("revenue_previous", 0),
            precision,
        )
    except GrowthCalculationError:
        results["revenue_growth_yoy"] = Decimal(0)

    try:
        results["profit_growth_yoy"] = profit_growth_yoy(
            financial_data.get("pat_current", 0),
            financial_data.get("pat_previous", 0),
            precision,
        )
    except GrowthCalculationError:
        results["profit_growth_yoy"] = Decimal(0)

    try:
        results["ebitda_growth_yoy"] = ebitda_growth_yoy(
            financial_data.get("ebitda_current", 0),
            financial_data.get("ebitda_previous", 0),
            precision,
        )
    except GrowthCalculationError:
        results["ebitda_growth_yoy"] = Decimal(0)

    try:
        results["eps_growth_yoy"] = eps_growth_yoy(
            financial_data.get("eps_current", 0),
            financial_data.get("eps_previous", 0),
            precision,
        )
    except GrowthCalculationError:
        results["eps_growth_yoy"] = Decimal(0)

    try:
        results["revenue_cagr_3yr"] = revenue_cagr_3yr(
            financial_data.get("revenue_current", 0),
            financial_data.get("revenue_3yrs_ago", 0),
            precision,
        )
    except GrowthCalculationError:
        results["revenue_cagr_3yr"] = Decimal(0)

    try:
        results["pat_cagr_3yr"] = pat_cagr_3yr(
            financial_data.get("pat_current", 0),
            financial_data.get("pat_3yrs_ago", 0),
            precision,
        )
    except GrowthCalculationError:
        results["pat_cagr_3yr"] = Decimal(0)

    try:
        results["ebitda_margin"] = ebitda_margin(
            financial_data.get("ebitda_current", 0),
            financial_data.get("revenue_current", 0),
            precision,
        )
    except GrowthCalculationError:
        results["ebitda_margin"] = Decimal(0)

    try:
        results["pat_margin"] = pat_margin(
            financial_data.get("pat_current", 0),
            financial_data.get("revenue_current", 0),
            precision,
        )
    except GrowthCalculationError:
        results["pat_margin"] = Decimal(0)

    try:
        results["roe"] = roe(
            financial_data.get("pat_current", 0),
            financial_data.get("avg_shareholders_equity", 0),
            precision,
        )
    except GrowthCalculationError:
        results["roe"] = Decimal(0)

    try:
        results["roce"] = roce(
            financial_data.get("ebit", 0),
            financial_data.get("capital_employed", 0),
            precision,
        )
    except GrowthCalculationError:
        results["roce"] = Decimal(0)

    try:
        results["cfo_growth"] = cfo_growth(
            financial_data.get("cfo_current", 0),
            financial_data.get("cfo_previous", 0),
            precision,
        )
    except GrowthCalculationError:
        results["cfo_growth"] = Decimal(0)

    return results
