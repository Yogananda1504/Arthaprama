"""
IPO Risk Assessment Engine for Arthaprama.

This module implements capital structure stress filters, cash flow quality ratios,
and promoter risk metrics as detailed in Section 2 of the IPO Analysis Framework.
It assesses capital structural resilience and corporate governance strain parameters.

All calculations use Decimal arithmetic for precision and return Decimal values
to maintain mathematical accuracy throughout the computation chain.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any


class RiskCalculationError(Exception):
    """Exception raised when risk calculations encounter invalid inputs."""

    pass


def _to_decimal(value: Any) -> Decimal:
    """
    Safely convert a value to Decimal for precise arithmetic.

    Args:
        value: Any numeric value (int, float, str, Decimal).

    Returns:
        Decimal representation of the input value.

    Raises:
        RiskCalculationError: If conversion fails.
    """
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise RiskCalculationError(f"Cannot convert '{value}' to Decimal") from e


def debt_to_equity(total_debt: Any, shareholders_equity: Any, precision: int = 4) -> Decimal:
    """
    Calculate Debt-to-Equity Ratio.

    Formula: Total Debt / Shareholders Equity

    This is a key leverage metric indicating the proportion of debt financing
    relative to equity financing.

    Args:
        total_debt: Total outstanding debt (short-term + long-term).
        shareholders_equity: Total shareholders' equity.
        precision: Number of decimal places for result.

    Returns:
        Debt-to-equity ratio (Decimal).

    Raises:
        RiskCalculationError: If equity is zero or inputs are invalid.

    Example:
        >>> debt_to_equity(500, 1000)
        Decimal('0.5000')
    """
    debt = _to_decimal(total_debt)
    equity = _to_decimal(shareholders_equity)

    if equity == 0:
        raise RiskCalculationError("Shareholders equity cannot be zero")

    ratio = debt / equity
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def net_debt(total_debt: Any, cash_equivalents: Any, precision: int = 4) -> Decimal:
    """
    Calculate Net Debt.

    Formula: Total Debt - Cash & Cash Equivalents

    Net debt represents the actual debt burden after accounting for liquid
    assets that could be used to pay down debt immediately.

    Args:
        total_debt: Total outstanding debt.
        cash_equivalents: Cash and cash equivalents on hand.
        precision: Number of decimal places for result.

    Returns:
        Net debt value (Decimal).

    Example:
        >>> net_debt(500, 150)
        Decimal('350.0000')
    """
    debt = _to_decimal(total_debt)
    cash = _to_decimal(cash_equivalents)

    net = debt - cash
    return net.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def net_debt_to_ebitda(net_debt_value: Any, ebitda: Any, precision: int = 4) -> Decimal:
    """
    Calculate Net Debt to EBITDA Ratio.

    Formula: Net Debt / EBITDA

    This ratio indicates how many years it would take to pay off debt using
    current EBITDA levels. A lower ratio indicates better debt servicing capacity.

    Args:
        net_debt_value: Net debt (Total Debt - Cash).
        ebitda: Earnings Before Interest, Taxes, Depreciation, and Amortization.
        precision: Number of decimal places for result.

    Returns:
        Net debt to EBITDA ratio (Decimal).

    Raises:
        RiskCalculationError: If EBITDA is zero or inputs are invalid.

    Example:
        >>> net_debt_to_ebitda(350, 100)
        Decimal('3.5000')
    """
    net_d = _to_decimal(net_debt_value)
    eb = _to_decimal(ebitda)

    if eb == 0:
        raise RiskCalculationError("EBITDA cannot be zero")

    ratio = net_d / eb
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def interest_coverage(ebit: Any, interest_expense: Any, precision: int = 4) -> Decimal:
    """
    Calculate Interest Coverage Ratio.

    Formula: EBIT / Interest Expense

    This ratio measures a company's ability to meet its interest obligations
    from operating earnings. Higher values indicate better coverage.

    Args:
        ebit: Earnings Before Interest and Taxes.
        interest_expense: Annual interest expense.
        precision: Number of decimal places for result.

    Returns:
        Interest coverage ratio (Decimal).

    Raises:
        RiskCalculationError: If interest expense is zero or inputs are invalid.

    Example:
        >>> interest_coverage(200, 50)
        Decimal('4.0000')
    """
    earnings = _to_decimal(ebit)
    interest = _to_decimal(interest_expense)

    if interest == 0:
        raise RiskCalculationError("Interest expense cannot be zero")

    ratio = earnings / interest
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def current_ratio(current_assets: Any, current_liabilities: Any, precision: int = 4) -> Decimal:
    """
    Calculate Current Ratio.

    Formula: Current Assets / Current Liabilities

    This liquidity ratio measures a company's ability to pay short-term
    obligations with short-term assets.

    Args:
        current_assets: Total current assets.
        current_liabilities: Total current liabilities.
        precision: Number of decimal places for result.

    Returns:
        Current ratio (Decimal).

    Raises:
        RiskCalculationError: If current liabilities are zero or inputs are invalid.

    Example:
        >>> current_ratio(500, 250)
        Decimal('2.0000')
    """
    assets = _to_decimal(current_assets)
    liabilities = _to_decimal(current_liabilities)

    if liabilities == 0:
        raise RiskCalculationError("Current liabilities cannot be zero")

    ratio = assets / liabilities
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def quick_ratio(
    current_assets: Any,
    inventory: Any,
    current_liabilities: Any,
    precision: int = 4,
) -> Decimal:
    """
    Calculate Quick Ratio (Acid-Test Ratio).

    Formula: (Current Assets - Inventory) / Current Liabilities

    This is a more stringent liquidity measure than the current ratio,
    excluding inventory which may not be easily convertible to cash.

    Args:
        current_assets: Total current assets.
        inventory: Inventory value.
        current_liabilities: Total current liabilities.
        precision: Number of decimal places for result.

    Returns:
        Quick ratio (Decimal).

    Raises:
        RiskCalculationError: If current liabilities are zero or inputs are invalid.

    Example:
        >>> quick_ratio(500, 150, 250)
        Decimal('1.4000')
    """
    assets = _to_decimal(current_assets)
    inv = _to_decimal(inventory)
    liabilities = _to_decimal(current_liabilities)

    if liabilities == 0:
        raise RiskCalculationError("Current liabilities cannot be zero")

    quick_assets = assets - inv
    ratio = quick_assets / liabilities
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def cfo_to_debt(cfo: Any, total_debt: Any, precision: int = 4) -> Decimal:
    """
    Calculate Cash Flow from Operations to Total Debt Ratio.

    Formula: Operating Cash Flow / Total Debt

    This ratio indicates the company's ability to repay total debt from
    operating cash flows.

    Args:
        cfo: Cash Flow from Operations.
        total_debt: Total outstanding debt.
        precision: Number of decimal places for result.

    Returns:
        CFO to debt ratio (Decimal).

    Raises:
        RiskCalculationError: If total debt is zero or inputs are invalid.

    Example:
        >>> cfo_to_debt(150, 500)
        Decimal('0.3000')
    """
    cash_flow = _to_decimal(cfo)
    debt = _to_decimal(total_debt)

    if debt == 0:
        raise RiskCalculationError("Total debt cannot be zero")

    ratio = cash_flow / debt
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def cfo_to_pat(cfo: Any, pat: Any, precision: int = 4) -> Decimal:
    """
    Calculate Cash Flow from Operations to PAT Ratio.

    Formula: Operating Cash Flow / PAT

    This ratio measures the quality of accounting profits. A ratio > 1
    indicates that cash earnings exceed accounting earnings, which is positive.

    Args:
        cfo: Cash Flow from Operations.
        pat: Profit After Tax.
        precision: Number of decimal places for result.

    Returns:
        CFO to PAT ratio (Decimal).

    Raises:
        RiskCalculationError: If PAT is zero or inputs are invalid.

    Example:
        >>> cfo_to_pat(150, 100)
        Decimal('1.5000')
    """
    cash_flow = _to_decimal(cfo)
    profit = _to_decimal(pat)

    if profit == 0:
        raise RiskCalculationError("PAT cannot be zero")

    ratio = cash_flow / profit
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def free_cash_flow(cfo: Any, capex: Any, precision: int = 4) -> Decimal:
    """
    Calculate Free Cash Flow (FCF).

    Formula: CFO - Capital Expenditure

    FCF represents the cash available to shareholders after maintaining
    or expanding the asset base.

    Args:
        cfo: Cash Flow from Operations.
        capex: Capital Expenditure.
        precision: Number of decimal places for result.

    Returns:
        Free cash flow value (Decimal).

    Example:
        >>> free_cash_flow(200, 80)
        Decimal('120.0000')
    """
    cash_flow = _to_decimal(cfo)
    capital_exp = _to_decimal(capex)

    fcf = cash_flow - capital_exp
    return fcf.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def fcf_to_pat(fcf: Any, pat: Any, precision: int = 4) -> Decimal:
    """
    Calculate Free Cash Flow to PAT Ratio.

    Formula: Free Cash Flow / PAT

    This ratio indicates how much of accounting profit converts to
    actual free cash available to shareholders.

    Args:
        fcf: Free Cash Flow.
        pat: Profit After Tax.
        precision: Number of decimal places for result.

    Returns:
        FCF to PAT ratio (Decimal).

    Raises:
        RiskCalculationError: If PAT is zero or inputs are invalid.

    Example:
        >>> fcf_to_pat(120, 100)
        Decimal('1.2000')
    """
    free_cf = _to_decimal(fcf)
    profit = _to_decimal(pat)

    if profit == 0:
        raise RiskCalculationError("PAT cannot be zero")

    ratio = free_cf / profit
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def customer_concentration(largest_customer_rev: Any, total_rev: Any, precision: int = 4) -> Decimal:
    """
    Calculate Customer Concentration Ratio.

    Formula: Largest Customer Revenue / Total Revenue * 100

    This ratio measures dependency on a single customer. High concentration
    represents a significant business risk.

    Args:
        largest_customer_rev: Revenue from largest customer.
        total_rev: Total revenue.
        precision: Number of decimal places for result.

    Returns:
        Customer concentration as a percentage (Decimal).

    Raises:
        RiskCalculationError: If total revenue is zero or inputs are invalid.

    Example:
        >>> customer_concentration(300, 1000)
        Decimal('30.0000')
    """
    largest = _to_decimal(largest_customer_rev)
    total = _to_decimal(total_rev)

    if total == 0:
        raise RiskCalculationError("Total revenue cannot be zero")

    concentration = (largest / total) * Decimal("100")
    return concentration.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def promoter_pledge_ratio(pledged_shares: Any, total_promoter_shares: Any, precision: int = 4) -> Decimal:
    """
    Calculate Promoter Pledge Ratio.

    Formula: Pledged Promoter Shares / Promoter Shares * 100

    This is a crucial operational stress marker indicating what portion
    of promoter holdings are pledged as collateral for loans.

    Args:
        pledged_shares: Number of shares pledged by promoters.
        total_promoter_shares: Total shares held by promoters.
        precision: Number of decimal places for result.

    Returns:
        Promoter pledge ratio as a percentage (Decimal).

    Raises:
        RiskCalculationError: If promoter shares are zero or inputs are invalid.

    Example:
        >>> promoter_pledge_ratio(200000, 1000000)
        Decimal('20.0000')
    """
    pledged = _to_decimal(pledged_shares)
    total = _to_decimal(total_promoter_shares)

    if total == 0:
        raise RiskCalculationError("Total promoter shares cannot be zero")

    ratio = (pledged / total) * Decimal("100")
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def contingent_liabilities_to_nw(contingent_libs: Any, net_worth: Any, precision: int = 4) -> Decimal:
    """
    Calculate Contingent Liabilities to Net Worth Ratio.

    Formula: Contingent Liabilities / Net Worth * 100

    This ratio measures potential off-balance-sheet risks relative to
    the company's net worth.

    Args:
        contingent_libs: Total contingent liabilities.
        net_worth: Company net worth.
        precision: Number of decimal places for result.

    Returns:
        Contingent liabilities to net worth as a percentage (Decimal).

    Raises:
        RiskCalculationError: If net worth is zero or inputs are invalid.

    Example:
        >>> contingent_liabilities_to_nw(50, 500)
        Decimal('10.0000')
    """
    contingent = _to_decimal(contingent_libs)
    nw = _to_decimal(net_worth)

    if nw == 0:
        raise RiskCalculationError("Net worth cannot be zero")

    ratio = (contingent / nw) * Decimal("100")
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def calculate_all_risk_metrics(financial_data: dict[str, Any], precision: int = 4) -> dict[str, Decimal]:
    """
    Calculate all risk metrics from a comprehensive financial data dictionary.

    This convenience function processes a complete set of financial data and
    returns all applicable risk metrics in a single call.

    Args:
        financial_data: Dictionary containing the following keys:
            - total_debt, shareholders_equity
            - cash_equivalents
            - ebitda, ebit, interest_expense
            - current_assets, current_liabilities, inventory
            - cfo, pat, capex
            - largest_customer_rev, total_rev
            - pledged_shares, total_promoter_shares
            - contingent_liabilities, net_worth
        precision: Number of decimal places for all results.

    Returns:
        Dictionary mapping metric names to their calculated Decimal values.
    """
    results: dict[str, Decimal] = {}

    try:
        results["debt_to_equity"] = debt_to_equity(
            financial_data.get("total_debt", 0),
            financial_data.get("shareholders_equity", 0),
            precision,
        )
    except RiskCalculationError:
        results["debt_to_equity"] = Decimal("0")

    try:
        net_d = net_debt(
            financial_data.get("total_debt", 0),
            financial_data.get("cash_equivalents", 0),
            precision,
        )
        results["net_debt"] = net_d
    except RiskCalculationError:
        results["net_debt"] = Decimal("0")

    try:
        results["net_debt_to_ebitda"] = net_debt_to_ebitda(
            results["net_debt"],
            financial_data.get("ebitda", 0),
            precision,
        )
    except RiskCalculationError:
        results["net_debt_to_ebitda"] = Decimal("0")

    try:
        results["interest_coverage"] = interest_coverage(
            financial_data.get("ebit", 0),
            financial_data.get("interest_expense", 0),
            precision,
        )
    except RiskCalculationError:
        results["interest_coverage"] = Decimal("0")

    try:
        results["current_ratio"] = current_ratio(
            financial_data.get("current_assets", 0),
            financial_data.get("current_liabilities", 0),
            precision,
        )
    except RiskCalculationError:
        results["current_ratio"] = Decimal("0")

    try:
        results["quick_ratio"] = quick_ratio(
            financial_data.get("current_assets", 0),
            financial_data.get("inventory", 0),
            financial_data.get("current_liabilities", 0),
            precision,
        )
    except RiskCalculationError:
        results["quick_ratio"] = Decimal("0")

    try:
        results["cfo_to_debt"] = cfo_to_debt(
            financial_data.get("cfo", 0),
            financial_data.get("total_debt", 0),
            precision,
        )
    except RiskCalculationError:
        results["cfo_to_debt"] = Decimal("0")

    try:
        results["cfo_to_pat"] = cfo_to_pat(
            financial_data.get("cfo", 0),
            financial_data.get("pat", 0),
            precision,
        )
    except RiskCalculationError:
        results["cfo_to_pat"] = Decimal("0")

    try:
        fcf = free_cash_flow(
            financial_data.get("cfo", 0),
            financial_data.get("capex", 0),
            precision,
        )
        results["free_cash_flow"] = fcf
    except RiskCalculationError:
        results["free_cash_flow"] = Decimal("0")

    try:
        results["fcf_to_pat"] = fcf_to_pat(
            results["free_cash_flow"],
            financial_data.get("pat", 0),
            precision,
        )
    except RiskCalculationError:
        results["fcf_to_pat"] = Decimal("0")

    try:
        results["customer_concentration"] = customer_concentration(
            financial_data.get("largest_customer_rev", 0),
            financial_data.get("total_rev", 0),
            precision,
        )
    except RiskCalculationError:
        results["customer_concentration"] = Decimal("0")

    try:
        results["promoter_pledge_ratio"] = promoter_pledge_ratio(
            financial_data.get("pledged_shares", 0),
            financial_data.get("total_promoter_shares", 0),
            precision,
        )
    except RiskCalculationError:
        results["promoter_pledge_ratio"] = Decimal("0")

    try:
        results["contingent_liabilities_to_nw"] = contingent_liabilities_to_nw(
            financial_data.get("contingent_liabilities", 0),
            financial_data.get("net_worth", 0),
            precision,
        )
    except RiskCalculationError:
        results["contingent_liabilities_to_nw"] = Decimal("0")

    return results
