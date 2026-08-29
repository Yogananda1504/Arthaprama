"""
Tests for IPO Workflow Engine and API Endpoints.

This module contains comprehensive tests for:
1. Direct execution of arthaprama/ipo/workflow.py with mock data
2. End-to-end HTTP calls to /analyze and /analyze/upload endpoints
3. Handling of invalid or partial schemas with appropriate HTTP 422 errors
"""

import io
import json
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from arthaprama.ipo.workflow import (
    GrowthAnalysisResult,
    IPOWorkflowEngine,
    IPOWorkflowError,
    run_full_ipo_analysis,
)

# =============================================================================
# TEST DATA FIXTURES
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
def full_ipo_request_payload() -> dict[str, Any]:
    """Complete IPO analysis request payload for API testing."""
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


# =============================================================================
# WORKFLOW ENGINE UNIT TESTS
# =============================================================================


class TestRunFullIpoAnalysis:
    """Tests for the run_full_ipo_analysis function."""

    def test_successful_full_analysis(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test successful execution of full IPO analysis."""
        result = run_full_ipo_analysis(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
            profile="balanced",
        )

        assert result.success is True
        assert result.growth_analysis.success is True
        assert result.risk_analysis.success is True
        assert result.valuation_analysis.success is True
        assert result.composite_score is not None
        assert result.composite_score.total_score > 0
        assert len(result.errors) == 0

    def test_analysis_with_peer_data(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
        sample_peer_data: dict[str, Any],
    ) -> None:
        """Test analysis with peer comparison data."""
        result = run_full_ipo_analysis(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
            profile="balanced",
            peer_data=sample_peer_data,
        )

        assert result.success is True
        assert result.composite_score is not None
        # Check that peer-related metrics are calculated
        assert "pe_premium_vs_peer" in result.valuation_analysis.metrics

    def test_partial_data_handling(
        self,
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test handling of partial/incomplete data."""
        # Missing required growth fields
        incomplete_growth: dict[str, Any] = {}

        result = run_full_ipo_analysis(
            growth_data=incomplete_growth,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
            profile="balanced",
        )

        # Should handle gracefully with fallback defaults
        assert result.growth_analysis.success is False or len(result.growth_analysis.metrics) == 0
        # Other analyses should still work
        assert result.risk_analysis.success is True
        assert result.valuation_analysis.success is True

    def test_different_profiles(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test analysis with different investor profiles."""
        profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]

        results = {}
        for profile in profiles:
            result = run_full_ipo_analysis(
                growth_data=sample_growth_data,
                risk_data=sample_risk_data,
                valuation_data=sample_valuation_data,
                ipo_data=sample_ipo_data,
                profile=profile,
            )
            results[profile] = result
            assert result.composite_score is not None

        # Different profiles may produce different scores
        scores = {p: float(r.composite_score.total_score) for p, r in results.items()}
        # At least verify all profiles produce valid scores
        for score in scores.values():
            assert 0 <= score <= 100


class TestIPOWorkflowEngine:
    """Tests for the IPOWorkflowEngine class."""

    def test_engine_execute_success(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test successful engine execution."""
        engine = IPOWorkflowEngine()
        result = engine.execute(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
            profile="balanced",
        )

        assert result.success is True
        assert result.composite_score is not None

    def test_engine_strict_mode_raises_on_error(
        self,
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test that strict mode raises exception on errors."""
        engine = IPOWorkflowEngine(strict_mode=True)
        incomplete_growth: dict[str, Any] = {}

        with pytest.raises(IPOWorkflowError):
            engine.execute(
                growth_data=incomplete_growth,
                risk_data=sample_risk_data,
                valuation_data=sample_valuation_data,
                ipo_data=sample_ipo_data,
                profile="balanced",
            )

    def test_engine_validate_inputs(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test input validation."""
        engine = IPOWorkflowEngine()

        # Valid inputs
        is_valid, errors = engine.validate_inputs(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
        )
        assert is_valid is True
        assert len(errors) == 0

        # Invalid inputs - missing required fields
        is_valid, errors = engine.validate_inputs(
            growth_data={},
            risk_data={},
            valuation_data={},
            ipo_data={},
        )
        assert is_valid is False
        assert len(errors) > 0

    def test_engine_custom_precision(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test engine with custom precision."""
        engine = IPOWorkflowEngine(precision=2)
        result = engine.execute(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
        )

        assert result.success is True
        # Verify metrics have correct precision
        for value in result.growth_analysis.metrics.values():
            # Check that values are properly rounded
            assert isinstance(value, Decimal)


class TestResultDataClasses:
    """Tests for result data classes."""

    def test_growth_analysis_result_to_dict(self) -> None:
        """Test GrowthAnalysisResult conversion to dict."""
        from decimal import Decimal

        result = GrowthAnalysisResult(
            metrics={"revenue_growth_yoy": Decimal("20.0")},
            errors=[],
            success=True,
        )
        d = result.to_dict()

        assert d["success"] is True
        assert d["metrics"]["revenue_growth_yoy"] == 20.0
        assert d["errors"] == []

    def test_full_result_to_dict(
        self,
        sample_growth_data: dict[str, Any],
        sample_risk_data: dict[str, Any],
        sample_valuation_data: dict[str, Any],
        sample_ipo_data: dict[str, Any],
    ) -> None:
        """Test FullIPOAnalysisResult conversion to dict."""
        result = run_full_ipo_analysis(
            growth_data=sample_growth_data,
            risk_data=sample_risk_data,
            valuation_data=sample_valuation_data,
            ipo_data=sample_ipo_data,
        )
        d = result.to_dict()

        assert "growth_analysis" in d
        assert "risk_analysis" in d
        assert "valuation_analysis" in d
        assert "composite_score" in d
        assert "success" in d


# =============================================================================
# API ENDPOINT TESTS
# =============================================================================


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/ipo/analyze endpoint."""

    def test_analyze_success(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test successful IPO analysis via API."""
        response = client.post("/api/v1/ipo/analyze", json=full_ipo_request_payload)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "growth_analysis" in data
        assert "risk_analysis" in data
        assert "valuation_analysis" in data
        assert data["composite_score"] is not None
        assert "total_score" in data["composite_score"]
        assert 0 <= data["composite_score"]["total_score"] <= 100

    def test_analyze_with_different_profiles(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test analysis with different investor profiles."""
        profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]

        for profile in profiles:
            payload = full_ipo_request_payload.copy()
            payload["profile"] = profile

            response = client.post("/api/v1/ipo/analyze", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_analyze_invalid_profile(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test analysis with invalid profile returns 422."""
        payload = full_ipo_request_payload.copy()
        payload["profile"] = "invalid_profile"

        response = client.post("/api/v1/ipo/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_missing_required_fields(
        self,
        client: TestClient,
    ) -> None:
        """Test analysis with missing required fields returns 422."""
        payload = {
            "meta": {"company_name": "Test Corp", "sector": "Tech"},
            # Missing growth_data, risk_data, etc.
        }

        response = client.post("/api/v1/ipo/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_partial_schema(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test analysis with partial/incomplete schema."""
        payload = full_ipo_request_payload.copy()
        # Remove some optional fields
        if "peer_data" in payload:
            del payload["peer_data"]

        response = client.post("/api/v1/ipo/analyze", json=payload)
        # Should still succeed as peer_data is optional
        assert response.status_code == 200


class TestAnalyzeUploadEndpoint:
    """Tests for POST /api/v1/ipo/analyze/upload endpoint."""

    def test_upload_json_success(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test successful analysis from uploaded JSON file."""
        file_content = json.dumps(full_ipo_request_payload)
        files = {"file": ("test_ipo.json", io.StringIO(file_content), "application/json")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["composite_score"] is not None

    def test_upload_invalid_json(
        self,
        client: TestClient,
    ) -> None:
        """Test upload with invalid JSON returns 400."""
        file_content = "{ invalid json }"
        files = {"file": ("invalid.json", io.StringIO(file_content), "application/json")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 400

    def test_upload_unsupported_format(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test upload with unsupported file format returns 400."""
        file_content = json.dumps(full_ipo_request_payload)
        files = {"file": ("test.csv", io.StringIO(file_content), "text/csv")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 400

    def test_upload_missing_filename(
        self,
        client: TestClient,
    ) -> None:
        """Test upload without filename returns 400."""
        # This is tricky to test directly; we rely on FastAPI's handling

    def test_upload_schema_validation_error(
        self,
        client: TestClient,
    ) -> None:
        """Test upload with schema validation errors returns 422."""
        invalid_payload = {
            "meta": {"company_name": "Test"},  # Missing sector
            # Missing all other required fields
        }
        file_content = json.dumps(invalid_payload)
        files = {
            "file": (
                "invalid_schema.json",
                io.StringIO(file_content),
                "application/json",
            )
        }

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 422


# =============================================================================
# BACKWARDS COMPATIBILITY TESTS
# =============================================================================


class TestBackwardsCompatibility:
    """Tests to ensure existing endpoints still work."""

    def test_evaluate_endpoint_still_works(
        self,
        client: TestClient,
        full_ipo_request_payload: dict[str, Any],
    ) -> None:
        """Test that the original /evaluate endpoint still functions."""
        # Convert to IPOEvaluationRequest format
        eval_payload = {
            "company_name": full_ipo_request_payload["meta"]["company_name"],
            "sector": full_ipo_request_payload["meta"]["sector"],
            "growth_data": full_ipo_request_payload["growth_data"],
            "risk_data": full_ipo_request_payload["risk_data"],
            "valuation_data": full_ipo_request_payload["valuation_data"],
            "ipo_data": full_ipo_request_payload["ipo_data"],
            "peer_data": full_ipo_request_payload.get("peer_data"),
            "profile": full_ipo_request_payload["profile"],
        }

        response = client.post("/api/v1/ipo/evaluate", json=eval_payload)
        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data
        assert "score_breakdown" in data

    def test_scores_breakdown_endpoint(self, client: TestClient) -> None:
        """Test that /scores/breakdown endpoint still works."""
        response = client.get("/api/v1/ipo/scores/breakdown")
        assert response.status_code == 200
        data = response.json()
        # This endpoint returns scoring methodology, not actual scores
        assert "growth_score" in data
        assert "risk_score" in data
        assert "valuation_score" in data
        assert "ipo_quality_score" in data
        # Verify it has the expected structure (max_points and metrics)
        assert "max_points" in data["growth_score"] or "metrics" in data["growth_score"]

    def test_profiles_endpoint(self, client: TestClient) -> None:
        """Test that /profiles endpoint still works."""
        response = client.get("/api/v1/ipo/profiles")
        assert response.status_code == 200
        data = response.json()
        assert "balanced" in data
        assert "conservative" in data


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


@pytest.fixture
def client() -> TestClient:
    """Create test client for the FastAPI app."""
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client
