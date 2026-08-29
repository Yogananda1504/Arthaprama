"""
Pytest configuration and shared fixtures for Arthaprama IPO Analysis tests.

This module provides reusable test fixtures for IPO payloads, mock data,
and test client setup used across unit and integration tests.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

# =============================================================================
# FIXTURES FOR IPO TEST DATA
# =============================================================================


@pytest.fixture
def sample_growth_data() -> dict[str, Any]:
    """Sample growth data for testing."""
    return {
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


@pytest.fixture
def sample_risk_data() -> dict[str, Any]:
    """Sample risk data for testing."""
    return {
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


@pytest.fixture
def sample_valuation_data() -> dict[str, Any]:
    """Sample valuation data for testing."""
    return {
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


@pytest.fixture
def sample_ipo_data() -> dict[str, Any]:
    """Sample IPO-specific data for testing."""
    return {
        "ipo_dilution": 10,
        "promoter_holding_pre_ipo": 75,
        "promoter_holding_post_ipo": 60,
        "promoter_pledge_ratio": 0,
        "issue_size": 1000000000,
        "fresh_issue": 600000000,
        "offer_for_sale": 400000000,
        "lot_size": 30,
        "price_band_lower": 480,
        "price_band_upper": 500,
    }


@pytest.fixture
def sample_peer_data() -> dict[str, Any]:
    """Sample peer comparison data for testing."""
    return {
        "peer_median_pe": 25,
        "peer_median_ev_ebitda": 12,
        "peer_median_pb": 3,
        "peer_market_caps": [1500, 2500, 3000],
    }


@pytest.fixture
def valid_ipo_payload() -> dict[str, Any]:
    """Complete valid IPO analysis request payload."""
    return {
        "meta": {
            "company_name": "Example Tech Ltd",
            "sector": "Technology",
            "price_band_lower": 480,
            "price_band_upper": 500,
            "issue_size": 1000000000,
            "fresh_issue": 600000000,
            "offer_for_sale": 400000000,
        },
        "growth_data": {
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
        },
        "risk_data": {
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
        },
        "valuation_data": {
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
        },
        "ipo_data": {
            "ipo_dilution": 10,
            "promoter_holding_pre_ipo": 75,
            "promoter_holding_post_ipo": 60,
            "promoter_pledge_ratio": 0,
            "issue_size": 1000000000,
            "fresh_issue": 600000000,
            "offer_for_sale": 400000000,
            "lot_size": 30,
            "price_band_lower": 480,
            "price_band_upper": 500,
        },
        "peer_data": {
            "peer_median_pe": 25,
            "peer_median_ev_ebitda": 12,
            "peer_median_pb": 3,
            "peer_market_caps": [1500, 2500, 3000],
        },
        "profile": "balanced",
    }


@pytest.fixture
def invalid_ipo_payload_missing_fields() -> dict[str, Any]:
    """Invalid IPO payload with missing required fields."""
    return {
        "meta": {"company_name": "Test Corp"},  # Missing sector
        # Missing all other required fields
    }


@pytest.fixture
def invalid_ipo_payload_negative_values() -> dict[str, Any]:
    """Invalid IPO payload with negative values."""
    return {
        "meta": {
            "company_name": "Test Corp",
            "sector": "Tech",
        },
        "growth_data": {
            "revenue_current": -100,  # Negative revenue is invalid
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


@pytest.fixture
def invalid_profile_payload(valid_ipo_payload: dict[str, Any]) -> dict[str, Any]:
    """IPO payload with invalid profile."""
    payload = valid_ipo_payload.copy()
    payload["profile"] = "invalid_profile"
    return payload


# =============================================================================
# FASTAPI TEST CLIENT FIXTURE
# =============================================================================


@pytest.fixture
def client() -> TestClient:
    """Create test client for the FastAPI app."""
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client


# =============================================================================
# JSON FILE HELPER FIXTURES
# =============================================================================


@pytest.fixture
def json_file_content(valid_ipo_payload: dict[str, Any]) -> str:
    """JSON string representation of valid IPO payload."""
    return json.dumps(valid_ipo_payload)


@pytest.fixture
def invalid_json_content() -> str:
    """Invalid JSON string for testing."""
    return "{ invalid json content }"
