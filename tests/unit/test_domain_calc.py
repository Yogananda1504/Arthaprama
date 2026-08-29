"""
Unit tests for core domain calculation logic in arthaprama/ipo/.

This module verifies the mathematical correctness of:
1. Growth calculations (growth.py)
2. Risk calculations (risk.py)
3. Valuation calculations (valuation.py)
4. Scoring calculations (scoring.py)
"""

from __future__ import annotations

import pytest
from decimal import Decimal

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
    _normalize_to_scale,
)


# =============================================================================
# GROWTH CALCULATION TESTS
# =============================================================================


class TestGrowthCalculations:
    """Tests for growth calculation functions."""

    def test_revenue_growth_yoy(self) -> None:
        """Test revenue growth YoY calculation."""
        result = revenue_growth_yoy(1200, 1000)
        assert result == Decimal("20.0000")

    def test_revenue_growth_yoy_zero_previous(self) -> None:
        """Test that zero previous revenue raises error."""
        with pytest.raises(GrowthCalculationError):
            revenue_growth_yoy(1200, 0)

    def test_profit_growth_yoy(self) -> None:
        """Test profit growth YoY calculation."""
        result = profit_growth_yoy(150, 100)
        assert result == Decimal("50.0000")

    def test_ebitda_growth_yoy(self) -> None:
        """Test EBITDA growth YoY calculation."""
        result = ebitda_growth_yoy(220, 200)
        assert result == Decimal("10.0000")

    def test_eps_growth_yoy(self) -> None:
        """Test EPS growth YoY calculation."""
        result = eps_growth_yoy(25, 20)
        assert result == Decimal("25.0000")

    def test_revenue_cagr_3yr(self) -> None:
        """Test 3-year revenue CAGR calculation."""
        # 10% CAGR: 1000 * 1.1^3 = 1331
        result = revenue_cagr_3yr(1331, 1000)
        assert abs(result - Decimal("0.1000")) < Decimal("0.0001")

    def test_pat_cagr_3yr(self) -> None:
        """Test 3-year PAT CAGR calculation."""
        # 20% CAGR: 1000 * 1.2^3 = 1728
        result = pat_cagr_3yr(1728, 1000)
        assert abs(result - Decimal("0.2000")) < Decimal("0.0001")

    def test_ebitda_margin(self) -> None:
        """Test EBITDA margin calculation."""
        result = ebitda_margin(150, 1000)
        assert result == Decimal("15.0000")

    def test_pat_margin(self) -> None:
        """Test PAT margin calculation."""
        result = pat_margin(100, 1000)
        assert result == Decimal("10.0000")

    def test_roe(self) -> None:
        """Test Return on Equity calculation."""
        result = roe(150, 1000)
        assert result == Decimal("15.0000")

    def test_roce(self) -> None:
        """Test ROCE calculation."""
        result = roce(180, 1000)
        assert result == Decimal("18.0000")

    def test_cfo_growth(self) -> None:
        """Test CFO growth calculation."""
        result = cfo_growth(220, 200)
        assert result == Decimal("10.0000")

    def test_calculate_all_growth_metrics(self) -> None:
        """Test comprehensive growth metrics calculation."""
        data = {
            "revenue_current": 1200,
            "revenue_previous": 1000,
            "revenue_3yrs_ago": 700,
            "pat_current": 150,
            "pat_previous": 100,
            "pat_3yrs_ago": 50,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
            "ebit": 180,
            "cfo_current": 180,
            "cfo_previous": 150,
            "avg_shareholders_equity": 800,
            "capital_employed": 900,
        }
        result = calculate_all_growth_metrics(data)
        assert "revenue_growth_yoy" in result
        assert "profit_growth_yoy" in result
        assert "ebitda_margin" in result
        assert "roe" in result
        assert "roce" in result


# =============================================================================
# RISK CALCULATION TESTS
# =============================================================================


class TestRiskCalculations:
    """Tests for risk calculation functions."""

    def test_debt_to_equity(self) -> None:
        """Test debt-to-equity ratio calculation."""
        result = debt_to_equity(500, 1000)
        assert result == Decimal("0.5000")

    def test_net_debt(self) -> None:
        """Test net debt calculation."""
        result = net_debt(500, 150)
        assert result == Decimal("350.0000")

    def test_net_debt_to_ebitda(self) -> None:
        """Test net debt to EBITDA calculation."""
        result = net_debt_to_ebitda(350, 100)
        assert result == Decimal("3.5000")

    def test_interest_coverage(self) -> None:
        """Test interest coverage ratio calculation."""
        result = interest_coverage(200, 50)
        assert result == Decimal("4.0000")

    def test_current_ratio(self) -> None:
        """Test current ratio calculation."""
        result = current_ratio(500, 250)
        assert result == Decimal("2.0000")

    def test_quick_ratio(self) -> None:
        """Test quick ratio calculation."""
        result = quick_ratio(500, 150, 250)
        assert result == Decimal("1.4000")

    def test_cfo_to_debt(self) -> None:
        """Test CFO to debt ratio calculation."""
        result = cfo_to_debt(150, 500)
        assert result == Decimal("0.3000")

    def test_cfo_to_pat(self) -> None:
        """Test CFO to PAT ratio calculation."""
        result = cfo_to_pat(150, 100)
        assert result == Decimal("1.5000")

    def test_free_cash_flow(self) -> None:
        """Test free cash flow calculation."""
        result = free_cash_flow(200, 80)
        assert result == Decimal("120.0000")

    def test_fcf_to_pat(self) -> None:
        """Test FCF to PAT ratio calculation."""
        result = fcf_to_pat(120, 100)
        assert result == Decimal("1.2000")

    def test_customer_concentration(self) -> None:
        """Test customer concentration calculation."""
        result = customer_concentration(300, 1000)
        assert result == Decimal("30.0000")

    def test_promoter_pledge_ratio(self) -> None:
        """Test promoter pledge ratio calculation."""
        result = promoter_pledge_ratio(200000, 1000000)
        assert result == Decimal("20.0000")

    def test_contingent_liabilities_to_nw(self) -> None:
        """Test contingent liabilities to net worth calculation."""
        result = contingent_liabilities_to_nw(50, 500)
        assert result == Decimal("10.0000")

    def test_calculate_all_risk_metrics(self) -> None:
        """Test comprehensive risk metrics calculation."""
        data = {
            "total_debt": 200,
            "shareholders_equity": 800,
            "cash_equivalents": 100,
            "ebitda": 200,
            "ebit": 180,
            "interest_expense": 20,
            "current_assets": 500,
            "current_liabilities": 250,
            "inventory": 100,
            "cfo": 180,
            "pat": 150,
            "capex": 50,
            "largest_customer_rev": 300,
            "total_rev": 1200,
            "pledged_shares": 0,
            "total_promoter_shares": 600000,
            "contingent_liabilities": 25,
            "net_worth": 800,
        }
        result = calculate_all_risk_metrics(data)
        assert "debt_to_equity" in result
        assert "net_debt" in result
        assert "interest_coverage" in result
        assert "current_ratio" in result


# =============================================================================
# VALUATION CALCULATION TESTS
# =============================================================================


class TestValuationCalculations:
    """Tests for valuation calculation functions."""

    def test_pe_ratio_direct(self) -> None:
        """Test P/E ratio calculation with direct values."""
        result = pe_ratio(
            market_cap=2000,
            pat=150,
            ipo_price=None,
            eps=None,
        )
        assert abs(result - Decimal("13.3333")) < Decimal("0.0001")

    def test_pb_ratio(self) -> None:
        """Test P/B ratio calculation."""
        result = pb_ratio(2000, 800)
        assert result == Decimal("2.5000")

    def test_ps_ratio(self) -> None:
        """Test P/S ratio calculation."""
        result = ps_ratio(2000, 1200)
        assert abs(result - Decimal("1.6667")) < Decimal("0.0001")

    def test_enterprise_value(self) -> None:
        """Test enterprise value calculation."""
        result = enterprise_value(2000, 200, 100)
        assert result == Decimal("2100.0000")

    def test_ev_to_ebitda(self) -> None:
        """Test EV/EBITDA calculation."""
        result = ev_to_ebitda(2100, 200)
        assert result == Decimal("10.5000")

    def test_ev_to_sales(self) -> None:
        """Test EV/Sales calculation."""
        result = ev_to_sales(2100, 1200)
        assert abs(result - Decimal("1.7500")) < Decimal("0.0001")

    def test_peg_ratio(self) -> None:
        """Test PEG ratio calculation."""
        result = peg_ratio(15, 20)
        assert result == Decimal("0.7500")

    def test_earnings_yield(self) -> None:
        """Test earnings yield calculation."""
        result = earnings_yield(25, 500)
        assert result == Decimal("5.0000")

    def test_price_to_fcf(self) -> None:
        """Test price to FCF calculation."""
        result = price_to_fcf(2000, 130)
        assert abs(result - Decimal("15.3846")) < Decimal("0.0001")

    def test_pe_premium_vs_peer(self) -> None:
        """Test P/E premium vs peer calculation."""
        result = pe_premium_vs_peer(15, 12)
        assert abs(result - Decimal("25.0000")) < Decimal("0.0001")

    def test_ev_ebitda_premium_vs_peer(self) -> None:
        """Test EV/EBITDA premium vs peer calculation."""
        result = ev_ebitda_premium_vs_peer(12, 10)
        assert result == Decimal("20.0000")

    def test_ipo_dilution(self) -> None:
        """Test IPO dilution calculation."""
        result = ipo_dilution(1000000, 10000000)
        assert result == Decimal("10.0000")

    def test_post_ipo_eps(self) -> None:
        """Test post-IPO EPS calculation."""
        result = post_ipo_eps(160, 10)
        assert result == Decimal("16.0000")

    def test_calculate_all_valuation_metrics(self) -> None:
        """Test comprehensive valuation metrics calculation."""
        data = {
            "market_cap": 2000,
            "pat": 150,
            "book_value": 800,
            "revenue": 1200,
            "ebitda": 200,
            "eps": 25,
            "ipo_price": 500,
            "total_debt": 200,
            "cash_equivalents": 100,
            "free_cash_flow": 130,
            "new_shares": 1000000,
            "post_ipo_shares": 10000000,
            "post_ipo_diluted_shares": 10500000,
            "post_ipo_pat": 160,
            "expected_eps_growth_pct": 20,
        }
        peer_data = {
            "peer_median_pe": 25,
            "peer_median_ev_ebitda": 12,
        }
        result = calculate_all_valuation_metrics(data, peer_data)
        assert "pe_ratio" in result
        assert "pb_ratio" in result
        assert "ev_to_ebitda" in result
        assert "pe_premium_vs_peer" in result


# =============================================================================
# SCORING CALCULATION TESTS
# =============================================================================


class TestScoringCalculations:
    """Tests for scoring calculation functions."""

    def test_normalize_to_scale_middle(self) -> None:
        """Test normalization to scale at middle value."""
        result = _normalize_to_scale(
            value=Decimal("50"),
            min_val=Decimal("0"),
            max_val=Decimal("100"),
            scale=Decimal("10"),
        )
        assert result == Decimal("5.00")

    def test_normalize_to_scale_min(self) -> None:
        """Test normalization to scale at minimum value."""
        result = _normalize_to_scale(
            value=Decimal("0"),
            min_val=Decimal("0"),
            max_val=Decimal("100"),
            scale=Decimal("10"),
        )
        assert result == Decimal("0.00")

    def test_normalize_to_scale_max(self) -> None:
        """Test normalization to scale at maximum value."""
        result = _normalize_to_scale(
            value=Decimal("100"),
            min_val=Decimal("0"),
            max_val=Decimal("100"),
            scale=Decimal("10"),
        )
        assert result == Decimal("10.00")

    def test_generate_ipo_score_balanced(self) -> None:
        """Test IPO score generation with balanced profile."""
        growth_data = {
            "revenue_current": 1200,
            "revenue_previous": 1000,
            "pat_current": 150,
            "pat_previous": 100,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
        }
        risk_data = {
            "total_debt": 200,
            "shareholders_equity": 800,
            "cash_equivalents": 100,
        }
        valuation_data = {
            "market_cap": 2000,
            "pat": 150,
            "book_value": 800,
            "revenue": 1200,
        }
        ipo_data = {
            "promoter_holding_post_ipo": 60,
            "promoter_pledge_ratio": 0,
        }

        result = generate_ipo_score(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile="balanced",
        )

        assert isinstance(result, ScoreBreakdown)
        assert result.total_score >= 0
        assert result.total_score <= 100
        assert result.growth_score >= 0
        assert result.risk_score >= 0
        assert result.valuation_score >= 0
        assert result.ipo_quality_score >= 0

    def test_generate_ipo_score_different_profiles(self) -> None:
        """Test IPO score generation with different profiles."""
        growth_data = {
            "revenue_current": 1200,
            "revenue_previous": 1000,
            "pat_current": 150,
            "pat_previous": 100,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
        }
        risk_data = {
            "total_debt": 200,
            "shareholders_equity": 800,
            "cash_equivalents": 100,
        }
        valuation_data = {
            "market_cap": 2000,
            "pat": 150,
            "book_value": 800,
            "revenue": 1200,
        }
        ipo_data = {
            "promoter_holding_post_ipo": 60,
            "promoter_pledge_ratio": 0,
        }

        profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]
        results = {}

        for profile in profiles:
            result = generate_ipo_score(
                growth_data=growth_data,
                risk_data=risk_data,
                valuation_data=valuation_data,
                ipo_data=ipo_data,
                profile=profile,
            )
            results[profile] = result
            assert result.total_score >= 0
            assert result.total_score <= 100
