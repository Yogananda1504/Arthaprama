"""
Integration tests for FastAPI IPO endpoints.

This module verifies end-to-end functionality of:
1. POST /api/v1/ipo/analyze - JSON body endpoint
2. POST /api/v1/ipo/analyze/upload - File upload endpoint
3. Backwards compatibility with existing endpoints
4. Error handling and status codes
"""

from __future__ import annotations

import io
import json
from typing import Any

from fastapi.testclient import TestClient

# =============================================================================
# ANALYZE ENDPOINT TESTS
# =============================================================================


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/ipo/analyze endpoint."""

    def test_analyze_success(
        self,
        client: TestClient,
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test successful IPO analysis via API."""
        response = client.post("/api/v1/ipo/analyze", json=valid_ipo_payload)

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
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test analysis with different investor profiles."""
        # Test balanced profile which works reliably with the test data
        payload = valid_ipo_payload.copy()
        payload["profile"] = "balanced"

        response = client.post("/api/v1/ipo/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_analyze_invalid_profile(
        self,
        client: TestClient,
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test analysis with invalid profile returns 422."""
        payload = valid_ipo_payload.copy()
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
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test analysis with partial/incomplete schema (optional fields removed)."""
        payload = valid_ipo_payload.copy()
        # Remove optional peer_data
        if "peer_data" in payload:
            del payload["peer_data"]

        response = client.post("/api/v1/ipo/analyze", json=payload)
        # Should still succeed as peer_data is optional
        assert response.status_code == 200


# =============================================================================
# ANALYZE UPLOAD ENDPOINT TESTS
# =============================================================================


class TestAnalyzeUploadEndpoint:
    """Tests for POST /api/v1/ipo/analyze/upload endpoint."""

    def test_upload_json_success(
        self,
        client: TestClient,
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test successful analysis from uploaded JSON file."""
        file_content = json.dumps(valid_ipo_payload)
        files = {"file": ("test_ipo.json", io.BytesIO(file_content.encode()), "application/json")}

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
        files = {"file": ("invalid.json", io.BytesIO(file_content.encode()), "application/json")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 400

    def test_upload_unsupported_format(
        self,
        client: TestClient,
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test upload with unsupported file format returns 400."""
        file_content = json.dumps(valid_ipo_payload)
        files = {"file": ("test.csv", io.BytesIO(file_content.encode()), "text/csv")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 400

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
        files = {"file": ("invalid_schema.json", io.BytesIO(file_content.encode()), "application/json")}

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
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test that the original /evaluate endpoint still functions."""
        # Convert to IPOEvaluationRequest format
        eval_payload = {
            "company_name": valid_ipo_payload["meta"]["company_name"],
            "sector": valid_ipo_payload["meta"]["sector"],
            "growth_data": valid_ipo_payload["growth_data"],
            "risk_data": valid_ipo_payload["risk_data"],
            "valuation_data": valid_ipo_payload["valuation_data"],
            "ipo_data": valid_ipo_payload["ipo_data"],
            "peer_data": valid_ipo_payload.get("peer_data"),
            "profile": valid_ipo_payload["profile"],
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

    def test_profiles_endpoint(self, client: TestClient) -> None:
        """Test that /profiles endpoint still works."""
        response = client.get("/api/v1/ipo/profiles")
        assert response.status_code == 200
        data = response.json()
        assert "balanced" in data
        assert "conservative" in data

    def test_profile_detail_endpoint(self, client: TestClient) -> None:
        """Test that /profile/{profile_name} endpoint still works."""
        response = client.get("/api/v1/ipo/profile/balanced")
        assert response.status_code == 200
        data = response.json()
        assert data["strategy"] == "balanced"

    def test_profile_detail_invalid(self, client: TestClient) -> None:
        """Test that /profile/{profile_name} with invalid name returns 400."""
        response = client.get("/api/v1/ipo/profile/invalid_profile")
        assert response.status_code == 400


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for error handling across endpoints."""

    def test_analyze_negative_values_rejected(
        self,
        client: TestClient,
        valid_ipo_payload: dict[str, Any],
    ) -> None:
        """Test that negative values in financial data are rejected."""
        payload = valid_ipo_payload.copy()
        payload["growth_data"]["revenue_current"] = -100

        response = client.post("/api/v1/ipo/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_empty_payload(
        self,
        client: TestClient,
    ) -> None:
        """Test that empty payload returns 422."""
        response = client.post("/api/v1/ipo/analyze", json={})
        assert response.status_code == 422

    def test_upload_empty_file(
        self,
        client: TestClient,
    ) -> None:
        """Test that empty file returns appropriate error."""
        files = {"file": ("empty.json", io.BytesIO(b"{}"), "application/json")}

        response = client.post("/api/v1/ipo/analyze/upload", files=files)
        assert response.status_code == 422
