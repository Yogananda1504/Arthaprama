"""Tests for MCP server tool wiring and SSE integration."""

from __future__ import annotations

import json
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Iterator
from unittest.mock import patch
from urllib.parse import urlparse

from fastapi.testclient import TestClient
import mcp.types as mcp_types

from backend.main import app
from backend import mcp_server


EXPECTED_TOOL_NAMES = {
    "calculate_ipo_growth",
    "evaluate_ipo_risk",
    "model_ipo_valuation",
    "generate_composite_ipo_score",
    "run_full_ipo_workflow",
}


def _read_sse_event(lines: Iterator[str]) -> tuple[str, str]:
    """Read a single SSE event from a line iterator."""
    event_name = ""
    data_parts: list[str] = []

    for line in lines:
        if line == "":
            if event_name or data_parts:
                return event_name, "\n".join(data_parts)
            continue

        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data_parts.append(line.split(":", 1)[1].lstrip())

    raise AssertionError("SSE stream closed before event was received")


def _normalize_endpoint_path(endpoint_url: str) -> str:
    """Normalize SSE endpoint URL to a TestClient-compatible path."""
    parsed = urlparse(endpoint_url)
    path = parsed.path or endpoint_url
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return path


class TestMCPToolWiring:
    """Unit tests that verify MCP tools invoke core domain functions."""

    def test_calculate_ipo_growth_invokes_growth_module(self) -> None:
        """Growth tool should call growth domain functions."""
        with patch.object(mcp_server.growth, "revenue_cagr_3yr", return_value=Decimal("0.1000")) as mock_cagr, patch.object(
            mcp_server.growth,
            "revenue_growth_yoy",
            return_value=Decimal("20.0000"),
        ) as mock_yoy:
            result = mcp_server.calculate_ipo_growth(
                historical_revenues=[100, 120, 145, 170],
                historical_ebitda_margins=[12, 13, 14, 15],
                industry_average_revenue_cagr_pct=11,
                industry_average_ebitda_margin_pct=13,
            )

        assert mock_cagr.call_count == 2
        assert mock_yoy.call_count == 3
        assert "revenue_cagr_pct" in result

    def test_evaluate_ipo_risk_invokes_risk_module(self) -> None:
        """Risk tool should call risk domain functions."""
        with patch.object(mcp_server.risk, "net_debt", return_value=Decimal("50.0000")) as mock_net_debt, patch.object(
            mcp_server.risk,
            "debt_to_equity",
            return_value=Decimal("0.3000"),
        ) as mock_dte, patch.object(
            mcp_server.risk,
            "net_debt_to_ebitda",
            return_value=Decimal("0.7000"),
        ) as mock_nd_ebitda, patch.object(
            mcp_server.risk,
            "interest_coverage",
            return_value=Decimal("8.0000"),
        ) as mock_ic:
            result = mcp_server.evaluate_ipo_risk(
                total_debt=150,
                shareholders_equity=500,
                cash_equivalents=100,
                ebitda=70,
                ebit=80,
                interest_expense=10,
                promoter_holding_post_ipo=62,
                promoter_pledge_ratio=0,
                litigation_cases=1,
                customer_concentration_pct=20,
            )

        mock_net_debt.assert_called_once()
        mock_dte.assert_called_once()
        mock_nd_ebitda.assert_called_once()
        mock_ic.assert_called_once()
        assert "risk_matrix" in result
        assert "penalties" in result

    def test_model_ipo_valuation_invokes_valuation_module(self) -> None:
        """Valuation tool should call valuation domain functions."""
        with patch.object(mcp_server.valuation, "post_ipo_eps", return_value=Decimal("10.0000")) as mock_eps, patch.object(
            mcp_server.valuation,
            "calculate_all_valuation_metrics",
            return_value={"pe_ratio": Decimal("15.0000"), "pe_premium_vs_peer": Decimal("5.0000")},
        ) as mock_calc, patch.object(
            mcp_server.valuation,
            "ipo_dilution",
            return_value=Decimal("12.0000"),
        ) as mock_dilution:
            result = mcp_server.model_ipo_valuation(
                price_band_lower=100,
                price_band_upper=120,
                shares_offered=100000,
                post_ipo_shares=1000000,
                projected_pat=10000000,
                projected_revenue=50000000,
                projected_ebitda=12000000,
                book_value=25000000,
                total_debt=1000000,
                cash_equivalents=500000,
                expected_eps_growth_pct=20,
                peer_median_pe=14,
                peer_median_ev_ebitda=8,
            )

        mock_eps.assert_called_once()
        mock_calc.assert_called_once()
        mock_dilution.assert_called_once()
        assert "valuation_metrics" in result
        assert "fair_value_band" in result

    def test_generate_composite_ipo_score_invokes_scoring_module(self) -> None:
        """Composite scoring tool should call scoring domain functions."""
        mocked_breakdown = SimpleNamespace(to_dict=lambda: {"total_score": 72.5})

        with patch.object(mcp_server.scoring, "generate_ipo_score", return_value=mocked_breakdown) as mock_score:
            result = mcp_server.generate_composite_ipo_score(
                growth_data={"input_data": {"revenue_current": 100, "revenue_previous": 80}},
                risk_data={"input_data": {"total_debt": 50, "shareholders_equity": 200}},
                valuation_data={"input_data": {"market_cap": 1000, "pat": 100}},
                ipo_data={"promoter_holding_post_ipo": 60, "promoter_pledge_ratio": 0},
            )

        mock_score.assert_called_once()
        assert result["rating_tier"] == "Moderate"

    def test_run_full_ipo_workflow_invokes_workflow_module(self) -> None:
        """Workflow tool should call full workflow domain function."""
        mock_workflow_result = SimpleNamespace(to_dict=lambda: {"composite_score": {"total_score": 81.0}, "success": True})

        with patch.object(mcp_server.workflow, "run_full_ipo_analysis", return_value=mock_workflow_result) as mock_run:
            result = mcp_server.run_full_ipo_workflow(
                meta={"company_name": "Example Ltd", "sector": "Technology"},
                growth_data={"revenue_current": 100, "revenue_previous": 90},
                risk_data={"total_debt": 10, "shareholders_equity": 100},
                valuation_data={"market_cap": 200, "pat": 15},
                ipo_data={"promoter_holding_post_ipo": 65, "promoter_pledge_ratio": 0},
            )

        mock_run.assert_called_once()
        assert result["rating_tier"] == "Strong"


class TestMCPSSEIntegration:
    """Integration tests for SSE transport and MCP tool discovery."""

    def test_sse_connection_lifecycle_and_tool_listing(self) -> None:
        """SSE should initialize and return complete tool listing."""
        with TestClient(app) as client:
            with client.stream("GET", "/sse") as sse_response:
                assert sse_response.status_code == 200
                assert sse_response.headers["content-type"].startswith("text/event-stream")

                lines = sse_response.iter_lines()
                event_name, endpoint_data = _read_sse_event(lines)
                assert event_name == "endpoint"

                endpoint_path = _normalize_endpoint_path(endpoint_data)

                initialize_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": mcp_types.LATEST_PROTOCOL_VERSION,
                        "capabilities": {},
                        "clientInfo": {"name": "pytest", "version": "1.0.0"},
                    },
                }
                init_response = client.post(endpoint_path, json=initialize_request)
                assert init_response.status_code == 202

                while True:
                    event_name, message_data = _read_sse_event(lines)
                    if event_name != "message":
                        continue

                    payload = json.loads(message_data)
                    if payload.get("id") == 1:
                        assert "result" in payload
                        break

                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {},
                }
                initialized_response = client.post(endpoint_path, json=initialized_notification)
                assert initialized_response.status_code == 202

                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {},
                }
                tools_response = client.post(endpoint_path, json=list_tools_request)
                assert tools_response.status_code == 202

                while True:
                    event_name, message_data = _read_sse_event(lines)
                    if event_name != "message":
                        continue

                    payload = json.loads(message_data)
                    if payload.get("id") != 2:
                        continue

                    tool_names = {tool["name"] for tool in payload["result"]["tools"]}
                    assert EXPECTED_TOOL_NAMES.issubset(tool_names)
                    break
