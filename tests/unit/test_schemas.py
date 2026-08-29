"""
Unit tests for Pydantic schema validation in backend/schemas.py.

This module verifies that:
1. Required fields are properly enforced
2. Value ranges and constraints are validated
3. Type enforcement works correctly
4. Invalid payloads are rejected with appropriate errors
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.schemas import (
    FullIPOAnalysisRequest,
    GrowthDataInput,
    IPOSpecificDataInput,
    PeerDataInput,
    RiskDataInput,
    ValuationDataInput,
)

# =============================================================================
# GROWTH DATA INPUT SCHEMA TESTS
# =============================================================================


class TestGrowthDataInput:
    """Tests for GrowthDataInput schema validation."""

    def test_valid_growth_data(self) -> None:
        """Test valid growth data passes validation."""
        data = {
            "revenue_current": 1200,
            "revenue_previous": 1000,
            "pat_current": 150,
            "pat_previous": 100,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
        }
        result = GrowthDataInput(**data)
        assert result.revenue_current == 1200
        assert result.pat_current == 150

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise ValidationError."""
        data = {
            "revenue_current": 1200,
            # Missing revenue_previous, pat_current, etc.
        }
        with pytest.raises(ValidationError):
            GrowthDataInput(**data)

    def test_negative_revenue_rejected(self) -> None:
        """Test that negative revenue values are rejected."""
        data = {
            "revenue_current": -100,
            "revenue_previous": 1000,
            "pat_current": 150,
            "pat_previous": 100,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
        }
        with pytest.raises(ValidationError):
            GrowthDataInput(**data)

    def test_decimal_conversion(self) -> None:
        """Test that numeric values are converted to Decimal."""
        from decimal import Decimal

        data = {
            "revenue_current": 1200.50,
            "revenue_previous": 1000,
            "pat_current": 150,
            "pat_previous": 100,
            "ebitda_current": 200,
            "ebitda_previous": 180,
            "eps_current": 25,
            "eps_previous": 20,
        }
        result = GrowthDataInput(**data)
        assert isinstance(result.revenue_current, Decimal)


# =============================================================================
# RISK DATA INPUT SCHEMA TESTS
# =============================================================================


class TestRiskDataInput:
    """Tests for RiskDataInput schema validation."""

    def test_valid_risk_data(self) -> None:
        """Test valid risk data passes validation."""
        data = {
            "total_debt": 200,
            "shareholders_equity": 800,
            "cash_equivalents": 100,
        }
        result = RiskDataInput(**data)
        assert result.total_debt == 200
        assert result.shareholders_equity == 800

    def test_all_fields_optional(self) -> None:
        """Test that all risk data fields are optional with defaults."""
        result = RiskDataInput()
        assert result.total_debt == 0
        assert result.shareholders_equity == 0

    def test_negative_debt_rejected(self) -> None:
        """Test that negative debt values are rejected."""
        data = {"total_debt": -100}
        with pytest.raises(ValidationError):
            RiskDataInput(**data)


# =============================================================================
# VALUATION DATA INPUT SCHEMA TESTS
# =============================================================================


class TestValuationDataInput:
    """Tests for ValuationDataInput schema validation."""

    def test_valid_valuation_data(self) -> None:
        """Test valid valuation data passes validation."""
        data = {
            "market_cap": 2000,
            "pat": 150,
            "book_value": 800,
        }
        result = ValuationDataInput(**data)
        assert result.market_cap == 2000

    def test_missing_market_cap(self) -> None:
        """Test that missing required market_cap raises ValidationError."""
        data = {
            "pat": 150,
            # Missing market_cap
        }
        with pytest.raises(ValidationError):
            ValuationDataInput(**data)

    def test_negative_market_cap_rejected(self) -> None:
        """Test that negative market cap is rejected."""
        data = {"market_cap": -100}
        with pytest.raises(ValidationError):
            ValuationDataInput(**data)


# =============================================================================
# IPO SPECIFIC DATA INPUT SCHEMA TESTS
# =============================================================================


class TestIPOSpecificDataInput:
    """Tests for IPOSpecificDataInput schema validation."""

    def test_valid_ipo_data(self) -> None:
        """Test valid IPO data passes validation."""
        data = {
            "ipo_dilution": 10,
            "promoter_holding_pre_ipo": 75,
            "promoter_holding_post_ipo": 60,
            "promoter_pledge_ratio": 0,
        }
        result = IPOSpecificDataInput(**data)
        assert result.ipo_dilution == 10
        assert result.promoter_holding_post_ipo == 60

    def test_dilution_percentage_bounds(self) -> None:
        """Test that dilution percentage must be between 0 and 100."""
        # Valid
        data = {"ipo_dilution": 50}
        result = IPOSpecificDataInput(**data)
        assert result.ipo_dilution == 50

        # Invalid - exceeds 100
        data_invalid = {"ipo_dilution": 150}
        with pytest.raises(ValidationError):
            IPOSpecificDataInput(**data_invalid)

    def test_promoter_holding_bounds(self) -> None:
        """Test that promoter holding percentages must be between 0 and 100."""
        # Valid
        data = {"promoter_holding_pre_ipo": 75, "promoter_holding_post_ipo": 60}
        result = IPOSpecificDataInput(**data)
        assert result.promoter_holding_pre_ipo == 75

        # Invalid - exceeds 100
        data_invalid = {"promoter_holding_pre_ipo": 150}
        with pytest.raises(ValidationError):
            IPOSpecificDataInput(**data_invalid)


# =============================================================================
# PEER DATA INPUT SCHEMA TESTS
# =============================================================================


class TestPeerDataInput:
    """Tests for PeerDataInput schema validation."""

    def test_valid_peer_data(self) -> None:
        """Test valid peer data passes validation."""
        data = {
            "peer_median_pe": 25,
            "peer_median_ev_ebitda": 12,
        }
        result = PeerDataInput(**data)
        assert result.peer_median_pe == 25

    def test_all_fields_optional(self) -> None:
        """Test that all peer data fields are optional."""
        result = PeerDataInput()
        assert result.peer_median_pe == 0
        assert result.peer_market_caps == []


# =============================================================================
# FULL IPO ANALYSIS REQUEST SCHEMA TESTS
# =============================================================================


class TestFullIPOAnalysisRequest:
    """Tests for FullIPOAnalysisRequest schema validation."""

    def test_valid_full_request(self) -> None:
        """Test valid full IPO analysis request passes validation."""
        data = {
            "meta": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
                "price_band_lower": 480,
                "price_band_upper": 500,
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {
                "total_debt": 200,
                "shareholders_equity": 800,
            },
            "valuation_data": {
                "market_cap": 2000,
            },
            "ipo_data": {},
            "profile": "balanced",
        }
        result = FullIPOAnalysisRequest(**data)
        assert result.meta.company_name == "Example Tech Ltd"
        assert result.profile == "balanced"

    def test_missing_meta(self) -> None:
        """Test that missing meta field raises ValidationError."""
        data = {
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {},
            "ipo_data": {},
        }
        with pytest.raises(ValidationError):
            FullIPOAnalysisRequest(**data)

    def test_missing_sector_in_meta(self) -> None:
        """Test that missing sector in meta raises ValidationError."""
        data = {
            "meta": {
                "company_name": "Test Corp",
                # Missing sector
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {},
            "ipo_data": {},
        }
        with pytest.raises(ValidationError):
            FullIPOAnalysisRequest(**data)

    def test_invalid_profile_rejected(self) -> None:
        """Test that invalid profile names are rejected."""
        data = {
            "meta": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {},
            "ipo_data": {},
            "profile": "invalid_profile",
        }
        with pytest.raises(ValidationError) as exc_info:
            FullIPOAnalysisRequest(**data)
        assert "Invalid profile" in str(exc_info.value)

    def test_valid_profiles_accepted(self) -> None:
        """Test that all valid profiles are accepted."""
        valid_profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]

        base_data = {
            "meta": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {"market_cap": 2000},
            "ipo_data": {},
        }

        for profile in valid_profiles:
            data = {**base_data, "profile": profile}
            result = FullIPOAnalysisRequest(**data)
            assert result.profile == profile

    def test_peer_data_optional(self) -> None:
        """Test that peer_data is optional."""
        data = {
            "meta": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {"market_cap": 2000},
            "ipo_data": {},
            # No peer_data
        }
        result = FullIPOAnalysisRequest(**data)
        assert result.peer_data is None

    def test_case_insensitive_profile(self) -> None:
        """Test that profile names are case-insensitive."""
        data = {
            "meta": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
            },
            "growth_data": {
                "revenue_current": 1200,
                "revenue_previous": 1000,
                "pat_current": 150,
                "pat_previous": 100,
                "ebitda_current": 200,
                "ebitda_previous": 180,
                "eps_current": 25,
                "eps_previous": 20,
            },
            "risk_data": {},
            "valuation_data": {"market_cap": 2000},
            "ipo_data": {},
            "profile": "BALANCED",
        }
        result = FullIPOAnalysisRequest(**data)
        assert result.profile == "balanced"
