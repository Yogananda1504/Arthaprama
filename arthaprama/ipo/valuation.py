"""
IPO Valuation Engine for Arthaprama.

This module implements absolute, relative, and IPO-specific structural pricing
mechanics defined across Sections 3, 4, and 5 of the IPO Analysis Framework.
It includes peer-benchmarking arrays, absolute valuations, and IPO dilution algebra.

All calculations use Decimal arithmetic for precision and return Decimal values
to maintain mathematical accuracy throughout the computation chain.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any


class ValuationCalculationError(Exception):
    """Exception raised when valuation calculations encounter invalid inputs."""

    pass


def _to_decimal(value: Any) -> Decimal:
    """
    Safely convert a value to Decimal for precise arithmetic.

    Args:
        value: Any numeric value (int, float, str, Decimal).

    Returns:
        Decimal representation of the input value.

    Raises:
        ValuationCalculationError: If conversion fails.
    """
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise ValuationCalculationError(f"Cannot convert '{value}' to Decimal") from e


# =============================================================================
# ABSOLUTE VALUATION METRICS (Section 3)
# =============================================================================


def pe_ratio(
    market_cap: Any | None = None,
    pat: Any | None = None,
    ipo_price: Any | None = None,
    eps: Any | None = None,
    precision: int = 4,
) -> Decimal:
    """
    Calculate Price-to-Earnings (P/E) Ratio.

    Formula: Market Cap / PAT OR IPO Price / EPS

    This is the most common valuation multiple indicating how much investors
    are willing to pay per unit of earnings.

    Args:
        market_cap: Market capitalization (optional if using ipo_price/eps).
        pat: Profit After Tax (optional if using ipo_price/eps).
        ipo_price: IPO offer price per share (optional if using market_cap/pat).
        eps: Earnings Per Share (optional if using market_cap/pat).
        precision: Number of decimal places for result.

    Returns:
        P/E ratio (Decimal).

    Raises:
        ValuationCalculationError: If denominator is zero or inputs are invalid.

    Example:
        >>> pe_ratio(market_cap=1000, pat=50)
        Decimal('20.0000')
        >>> pe_ratio(ipo_price=500, eps=25)
        Decimal('20.0000')
    """
    if market_cap is not None and pat is not None:
        cap = _to_decimal(market_cap)
        profit = _to_decimal(pat)
        if profit == 0:
            raise ValuationCalculationError("PAT cannot be zero")
        ratio = cap / profit
    elif ipo_price is not None and eps is not None:
        price = _to_decimal(ipo_price)
        earnings = _to_decimal(eps)
        if earnings == 0:
            raise ValuationCalculationError("EPS cannot be zero")
        ratio = price / earnings
    else:
        raise ValuationCalculationError("Must provide either (market_cap, pat) or (ipo_price, eps)")

    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def pb_ratio(market_cap: Any, book_value: Any, precision: int = 4) -> Decimal:
    """
    Calculate Price-to-Book (P/B) Ratio.

    Formula: Market Cap / Book Value

    This ratio compares market value to accounting book value, useful for
    asset-heavy businesses.

    Args:
        market_cap: Market capitalization.
        book_value: Book value of equity.
        precision: Number of decimal places for result.

    Returns:
        P/B ratio (Decimal).

    Raises:
        ValuationCalculationError: If book value is zero or inputs are invalid.

    Example:
        >>> pb_ratio(1000, 500)
        Decimal('2.0000')
    """
    cap = _to_decimal(market_cap)
    bv = _to_decimal(book_value)

    if bv == 0:
        raise ValuationCalculationError("Book value cannot be zero")

    ratio = cap / bv
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ps_ratio(market_cap: Any, revenue: Any, precision: int = 4) -> Decimal:
    """
    Calculate Price-to-Sales (P/S) Ratio.

    Formula: Market Cap / Revenue

    This ratio is useful for valuing companies with low or negative earnings.

    Args:
        market_cap: Market capitalization.
        revenue: Total revenue.
        precision: Number of decimal places for result.

    Returns:
        P/S ratio (Decimal).

    Raises:
        ValuationCalculationError: If revenue is zero or inputs are invalid.

    Example:
        >>> ps_ratio(1000, 800)
        Decimal('1.2500')
    """
    cap = _to_decimal(market_cap)
    rev = _to_decimal(revenue)

    if rev == 0:
        raise ValuationCalculationError("Revenue cannot be zero")

    ratio = cap / rev
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ev_to_ebitda(enterprise_value: Any, ebitda: Any, precision: int = 4) -> Decimal:
    """
    Calculate Enterprise Value to EBITDA Ratio.

    Formula: Enterprise Value / EBITDA

    This ratio provides a debt-neutral valuation metric useful for comparing
    companies with different capital structures.

    Args:
        enterprise_value: Enterprise Value.
        ebitda: Earnings Before Interest, Taxes, Depreciation, and Amortization.
        precision: Number of decimal places for result.

    Returns:
        EV/EBITDA ratio (Decimal).

    Raises:
        ValuationCalculationError: If EBITDA is zero or inputs are invalid.

    Example:
        >>> ev_to_ebitda(1200, 100)
        Decimal('12.0000')
    """
    ev = _to_decimal(enterprise_value)
    eb = _to_decimal(ebitda)

    if eb == 0:
        raise ValuationCalculationError("EBITDA cannot be zero")

    ratio = ev / eb
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ev_to_sales(enterprise_value: Any, revenue: Any, precision: int = 4) -> Decimal:
    """
    Calculate Enterprise Value to Sales Ratio.

    Formula: Enterprise Value / Revenue

    This ratio is useful for comparing companies with different leverage levels.

    Args:
        enterprise_value: Enterprise Value.
        revenue: Total revenue.
        precision: Number of decimal places for result.

    Returns:
        EV/Sales ratio (Decimal).

    Raises:
        ValuationCalculationError: If revenue is zero or inputs are invalid.

    Example:
        >>> ev_to_sales(1200, 800)
        Decimal('1.5000')
    """
    ev = _to_decimal(enterprise_value)
    rev = _to_decimal(revenue)

    if rev == 0:
        raise ValuationCalculationError("Revenue cannot be zero")

    ratio = ev / rev
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def peg_ratio(pe: Any, expected_eps_growth_pct: Any, precision: int = 4) -> Decimal:
    """
    Calculate Price/Earnings to Growth (PEG) Ratio.

    Formula: P/E Ratio / Expected EPS Growth Rate (%)

    This ratio adjusts P/E for growth expectations. A PEG < 1 may indicate
    undervaluation relative to growth prospects.

    Args:
        pe: Price-to-Earnings ratio.
        expected_eps_growth_pct: Expected EPS growth rate as percentage (e.g., 20 for 20%).
        precision: Number of decimal places for result.

    Returns:
        PEG ratio (Decimal).

    Raises:
        ValuationCalculationError: If growth rate is zero or inputs are invalid.

    Example:
        >>> peg_ratio(20, 25)
        Decimal('0.8000')
    """
    pe_val = _to_decimal(pe)
    growth = _to_decimal(expected_eps_growth_pct)

    if growth == 0:
        raise ValuationCalculationError("Expected EPS growth cannot be zero")

    ratio = pe_val / growth
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def earnings_yield(eps: Any, ipo_price: Any, precision: int = 4) -> Decimal:
    """
    Calculate Earnings Yield.

    Formula: EPS / IPO Price * 100

    This is the inverse of P/E ratio, showing earnings as a percentage of price.
    Useful for comparing against bond yields or cost of capital.

    Args:
        eps: Earnings Per Share.
        ipo_price: IPO offer price per share.
        precision: Number of decimal places for result.

    Returns:
        Earnings yield as a percentage (Decimal).

    Raises:
        ValuationCalculationError: If IPO price is zero or inputs are invalid.

    Example:
        >>> earnings_yield(25, 500)
        Decimal('5.0000')
    """
    earnings = _to_decimal(eps)
    price = _to_decimal(ipo_price)

    if price == 0:
        raise ValuationCalculationError("IPO price cannot be zero")

    yield_val = (earnings / price) * Decimal("100")
    return yield_val.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def price_to_fcf(market_cap: Any, free_cash_flow: Any, precision: int = 4) -> Decimal:
    """
    Calculate Price to Free Cash Flow Ratio.

    Formula: Market Cap / Free Cash Flow

    This ratio shows how many years of current FCF the market cap represents.

    Args:
        market_cap: Market capitalization.
        free_cash_flow: Free Cash Flow.
        precision: Number of decimal places for result.

    Returns:
        Price/FCF ratio (Decimal).

    Raises:
        ValuationCalculationError: If FCF is zero or inputs are invalid.

    Example:
        >>> price_to_fcf(1000, 80)
        Decimal('12.5000')
    """
    cap = _to_decimal(market_cap)
    fcf = _to_decimal(free_cash_flow)

    if fcf == 0:
        raise ValuationCalculationError("Free cash flow cannot be zero")

    ratio = cap / fcf
    return ratio.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def enterprise_value(market_cap: Any, total_debt: Any, cash: Any, precision: int = 4) -> Decimal:
    """
    Calculate Enterprise Value (EV).

    Formula: Market Cap + Total Debt - Cash

    Enterprise Value represents the theoretical takeover price of a company,
    including debt obligations net of cash.

    Args:
        market_cap: Market capitalization.
        total_debt: Total outstanding debt.
        cash: Cash and cash equivalents.
        precision: Number of decimal places for result.

    Returns:
        Enterprise Value (Decimal).

    Example:
        >>> enterprise_value(1000, 300, 100)
        Decimal('1200.0000')
    """
    cap = _to_decimal(market_cap)
    debt = _to_decimal(total_debt)
    cash_val = _to_decimal(cash)

    ev = cap + debt - cash_val
    return ev.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


# =============================================================================
# RELATIVE VALUATION METRICS (Section 4)
# =============================================================================


def pe_premium_vs_peer(ipo_pe: Any, peer_median_pe: Any, precision: int = 4) -> Decimal:
    """
    Calculate P/E Premium/Discount vs Peer Median.

    Formula: (IPO P/E - Peer Median P/E) / Peer Median P/E * 100

    This shows whether the IPO is priced at a premium or discount relative
    to comparable listed peers.

    Args:
        ipo_pe: IPO's P/E ratio.
        peer_median_pe: Median P/E of peer group.
        precision: Number of decimal places for result.

    Returns:
        Premium/discount as a percentage (Decimal). Positive = premium, Negative = discount.

    Raises:
        ValuationCalculationError: If peer median P/E is zero or inputs are invalid.

    Example:
        >>> pe_premium_vs_peer(25, 20)
        Decimal('25.0000')  # 25% premium
    """
    ipo = _to_decimal(ipo_pe)
    peer = _to_decimal(peer_median_pe)

    if peer == 0:
        raise ValuationCalculationError("Peer median P/E cannot be zero")

    premium = ((ipo - peer) / peer) * Decimal("100")
    return premium.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def ev_ebitda_premium_vs_peer(ipo_ev_ebitda: Any, peer_median: Any, precision: int = 4) -> Decimal:
    """
    Calculate EV/EBITDA Premium/Discount vs Peer Median.

    Formula: (IPO EV/EBITDA - Peer Median) / Peer Median * 100

    This shows whether the IPO's EV/EBITDA multiple is at a premium or discount
    relative to comparable listed peers.

    Args:
        ipo_ev_ebitda: IPO's EV/EBITDA ratio.
        peer_median: Median EV/EBITDA of peer group.
        precision: Number of decimal places for result.

    Returns:
        Premium/discount as a percentage (Decimal). Positive = premium, Negative = discount.

    Raises:
        ValuationCalculationError: If peer median is zero or inputs are invalid.

    Example:
        >>> ev_ebitda_premium_vs_peer(12, 10)
        Decimal('20.0000')  # 20% premium
    """
    ipo = _to_decimal(ipo_ev_ebitda)
    peer = _to_decimal(peer_median)

    if peer == 0:
        raise ValuationCalculationError("Peer median EV/EBITDA cannot be zero")

    premium = ((ipo - peer) / peer) * Decimal("100")
    return premium.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


# =============================================================================
# IPO-SPECIFIC FACTORS (Section 5)
# =============================================================================


def ipo_dilution(new_shares: Any, post_ipo_shares: Any, precision: int = 4) -> Decimal:
    """
    Calculate IPO Dilution Percentage.

    Formula: New Shares / Post-IPO Shares * 100

    This measures the dilution impact of new shares issued in the IPO on
    existing shareholders.

    Args:
        new_shares: Number of new shares being issued.
        post_ipo_shares: Total shares outstanding after IPO.
        precision: Number of decimal places for result.

    Returns:
        Dilution percentage (Decimal).

    Raises:
        ValuationCalculationError: If post-IPO shares is zero or inputs are invalid.

    Example:
        >>> ipo_dilution(1000000, 10000000)
        Decimal('10.0000')  # 10% dilution
    """
    new = _to_decimal(new_shares)
    post = _to_decimal(post_ipo_shares)

    if post == 0:
        raise ValuationCalculationError("Post-IPO shares cannot be zero")

    dilution = (new / post) * Decimal("100")
    return dilution.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def post_ipo_eps(post_ipo_pat: Any, post_ipo_diluted_shares: Any, precision: int = 4) -> Decimal:
    """
    Calculate Post-IPO Earnings Per Share.

    Formula: Post-IPO PAT / Post-IPO Diluted Shares

    This ensures developers avoid relying on pre-IPO/historical share counts
    when evaluating IPO valuations.

    Args:
        post_ipo_pat: PAT after IPO (considering fresh capital deployment).
        post_ipo_diluted_shares: Total diluted shares outstanding post-IPO.
        precision: Number of decimal places for result.

    Returns:
        Post-IPO EPS (Decimal).

    Raises:
        ValuationCalculationError: If diluted shares is zero or inputs are invalid.

    Example:
        >>> post_ipo_eps(100, 10)
        Decimal('10.0000')
    """
    pat = _to_decimal(post_ipo_pat)
    shares = _to_decimal(post_ipo_diluted_shares)

    if shares == 0:
        raise ValuationCalculationError("Diluted shares cannot be zero")

    eps = pat / shares
    return eps.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def calculate_all_valuation_metrics(
    financial_data: dict[str, Any],
    peer_data: dict[str, Any] | None = None,
    precision: int = 4,
) -> dict[str, Decimal]:
    """
    Calculate all valuation metrics from comprehensive financial data.

    This convenience function processes a complete set of financial data and
    returns all applicable valuation metrics in a single call.

    Args:
        financial_data: Dictionary containing the following keys:
            - market_cap, pat, book_value, revenue
            - ebitda, ebit, interest_expense
            - eps, ipo_price
            - total_debt, cash_equivalents
            - free_cash_flow
            - new_shares, post_ipo_shares, post_ipo_diluted_shares, post_ipo_pat
            - expected_eps_growth_pct
        peer_data: Optional dictionary containing peer median values:
            - peer_median_pe, peer_median_ev_ebitda
        precision: Number of decimal places for all results.

    Returns:
        Dictionary mapping metric names to their calculated Decimal values.
    """
    results: dict[str, Decimal] = {}
    peer = peer_data or {}

    # Calculate Enterprise Value first (needed for other metrics)
    try:
        ev = enterprise_value(
            financial_data.get("market_cap", 0),
            financial_data.get("total_debt", 0),
            financial_data.get("cash_equivalents", 0),
            precision,
        )
        results["enterprise_value"] = ev
    except ValuationCalculationError:
        results["enterprise_value"] = Decimal("0")

    # Absolute Valuation Metrics
    try:
        results["pe_ratio"] = pe_ratio(
            market_cap=financial_data.get("market_cap"),
            pat=financial_data.get("pat"),
            ipo_price=financial_data.get("ipo_price"),
            eps=financial_data.get("eps"),
            precision=precision,
        )
    except ValuationCalculationError:
        results["pe_ratio"] = Decimal("0")

    try:
        results["pb_ratio"] = pb_ratio(
            financial_data.get("market_cap", 0),
            financial_data.get("book_value", 0),
            precision,
        )
    except ValuationCalculationError:
        results["pb_ratio"] = Decimal("0")

    try:
        results["ps_ratio"] = ps_ratio(
            financial_data.get("market_cap", 0),
            financial_data.get("revenue", 0),
            precision,
        )
    except ValuationCalculationError:
        results["ps_ratio"] = Decimal("0")

    try:
        results["ev_to_ebitda"] = ev_to_ebitda(
            results["enterprise_value"],
            financial_data.get("ebitda", 0),
            precision,
        )
    except ValuationCalculationError:
        results["ev_to_ebitda"] = Decimal("0")

    try:
        results["ev_to_sales"] = ev_to_sales(
            results["enterprise_value"],
            financial_data.get("revenue", 0),
            precision,
        )
    except ValuationCalculationError:
        results["ev_to_sales"] = Decimal("0")

    try:
        results["peg_ratio"] = peg_ratio(
            results["pe_ratio"],
            financial_data.get("expected_eps_growth_pct", 0),
            precision,
        )
    except ValuationCalculationError:
        results["peg_ratio"] = Decimal("0")

    try:
        results["earnings_yield"] = earnings_yield(
            financial_data.get("eps", 0),
            financial_data.get("ipo_price", 0),
            precision,
        )
    except ValuationCalculationError:
        results["earnings_yield"] = Decimal("0")

    try:
        results["price_to_fcf"] = price_to_fcf(
            financial_data.get("market_cap", 0),
            financial_data.get("free_cash_flow", 0),
            precision,
        )
    except ValuationCalculationError:
        results["price_to_fcf"] = Decimal("0")

    # Relative Valuation Metrics
    if peer.get("peer_median_pe"):
        try:
            results["pe_premium_vs_peer"] = pe_premium_vs_peer(
                results["pe_ratio"],
                peer["peer_median_pe"],
                precision,
            )
        except ValuationCalculationError:
            results["pe_premium_vs_peer"] = Decimal("0")
    else:
        results["pe_premium_vs_peer"] = Decimal("0")

    if peer.get("peer_median_ev_ebitda"):
        try:
            results["ev_ebitda_premium_vs_peer"] = ev_ebitda_premium_vs_peer(
                results["ev_to_ebitda"],
                peer["peer_median_ev_ebitda"],
                precision,
            )
        except ValuationCalculationError:
            results["ev_ebitda_premium_vs_peer"] = Decimal("0")
    else:
        results["ev_ebitda_premium_vs_peer"] = Decimal("0")

    # IPO-Specific Metrics
    try:
        results["ipo_dilution"] = ipo_dilution(
            financial_data.get("new_shares", 0),
            financial_data.get("post_ipo_shares", 0),
            precision,
        )
    except ValuationCalculationError:
        results["ipo_dilution"] = Decimal("0")

    try:
        results["post_ipo_eps"] = post_ipo_eps(
            financial_data.get("post_ipo_pat", 0),
            financial_data.get("post_ipo_diluted_shares", 0),
            precision,
        )
    except ValuationCalculationError:
        results["post_ipo_eps"] = Decimal("0")

    return results
