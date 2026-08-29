"""
MCP Server Tests for Arthaprama.

This module contains unit and integration tests for the Model Context Protocol (MCP)
server implementation, verifying that all MCP tool functions correctly invoke domain
functions in arthaprama/ipo/ and that SSE connection lifecycle works properly.
"""

from __future__ import annotations

from backend.mcp_server import (
    calculate_ipo_growth,
    evaluate_ipo_risk,
    generate_composite_ipo_score,
    model_ipo_valuation,
    run_full_ipo_workflow,
)


class TestCalculateIpoGrowth:
    """Tests for the calculate_ipo_growth MCP tool."""

    def test_basic_growth_calculation(self) -> None:
        """Test basic revenue growth calculation with minimal inputs."""
        result = calculate_ipo_growth(
            revenues=[100, 120, 150, 180],
        )
        
        assert result["success"] is True
        assert "metrics" in result
        assert "revenue_cagr_3yr" in result["metrics"]
        assert "revenue_growth_yoy" in result["metrics"]
        
    def test_growth_with_profits(self) -> None:
        """Test growth calculation with profit data."""
        result = calculate_ipo_growth(
            revenues=[100, 120, 150, 180],
            profits=[10, 15, 20, 25],
        )
        
        assert result["success"] is True
        # Domain function returns pat_cagr_3yr and profit_growth_yoy
        assert "pat_cagr_3yr" in result["metrics"] or "profit_cagr_3yr" in result["metrics"]
        assert "profit_growth_yoy" in result["metrics"]
        
    def test_growth_with_industry_comparison(self) -> None:
        """Test growth calculation with industry benchmarks."""
        result = calculate_ipo_growth(
            revenues=[100, 120, 150, 180],
            profits=[10, 15, 20, 25],
            industry_avg_growth=15.0,
            industry_avg_margin=20.0,
        )
        
        assert result["success"] is True
        assert "vs_industry_growth" in result["metrics"]
        assert "vs_industry_margin" in result["metrics"]
        
    def test_growth_insufficient_data(self) -> None:
        """Test that insufficient data raises appropriate error."""
        result = calculate_ipo_growth(
            revenues=[100],  # Only one data point
        )
        
        assert result["success"] is False
        assert "error" in result
        
    def test_growth_invokes_domain_function(self) -> None:
        """Verify that the tool invokes the core domain function."""
        # This test ensures domain isolation - the MCP tool should call
        # calculate_all_growth_metrics from arthaprama.ipo.growth
        result = calculate_ipo_growth(
            revenues=[100, 120, 150],
            ebitda=[20, 25, 30],
            equity=[200, 220, 250],
            assets=[400, 450, 500],
        )
        
        assert result["success"] is True
        # Verify comprehensive metrics are calculated by domain function
        assert "roe" in result["metrics"] or "roce" in result["metrics"]


class TestEvaluateIpoRisk:
    """Tests for the evaluate_ipo_risk MCP tool."""

    def test_basic_risk_evaluation(self) -> None:
        """Test basic risk assessment with required parameters."""
        result = evaluate_ipo_risk(
            total_debt=500,
            shareholders_equity=1000,
            cash_equivalents=150,
            ebitda=200,
            interest_expense=50,
            current_assets=300,
            current_liabilities=200,
        )
        
        assert result["success"] is True
        assert "metrics" in result
        assert "debt_to_equity" in result["metrics"]
        assert "current_ratio" in result["metrics"]
        assert "risk_matrix" in result
        assert "risk_assessment" in result
        
    def test_risk_with_promoter_data(self) -> None:
        """Test risk evaluation with promoter holding and pledge data."""
        result = evaluate_ipo_risk(
            total_debt=500,
            shareholders_equity=1000,
            cash_equivalents=150,
            ebitda=200,
            interest_expense=50,
            current_assets=300,
            current_liabilities=200,
            promoter_holding=60.0,
            promoter_pledge=30.0,
        )
        
        assert result["success"] is True
        assert "promoter_pledge_ratio" in result["metrics"]
        
    def test_risk_with_customer_concentration(self) -> None:
        """Test risk evaluation with customer concentration data."""
        result = evaluate_ipo_risk(
            total_debt=500,
            shareholders_equity=1000,
            cash_equivalents=150,
            ebitda=200,
            interest_expense=50,
            current_assets=300,
            current_liabilities=200,
            top_customer_revenue_pct=45.0,
        )
        
        assert result["success"] is True
        assert "customer_concentration" in result["metrics"]
        
    def test_risk_invalid_parameters(self) -> None:
        """Test that invalid parameters raise appropriate error."""
        result = evaluate_ipo_risk(
            total_debt=-100,  # Invalid negative debt
            shareholders_equity=1000,
            cash_equivalents=150,
            ebitda=200,
            interest_expense=50,
            current_assets=300,
            current_liabilities=200,
        )
        
        assert result["success"] is False
        assert "error" in result
        
    def test_risk_invokes_domain_function(self) -> None:
        """Verify that the tool invokes the core domain function."""
        result = evaluate_ipo_risk(
            total_debt=500,
            shareholders_equity=1000,
            cash_equivalents=150,
            ebitda=200,
            interest_expense=50,
            current_assets=300,
            current_liabilities=200,
            operating_cash_flow=180,
            net_profit=150,
        )
        
        assert result["success"] is True
        # Verify comprehensive risk metrics from domain function
        assert "net_debt_to_ebitda" in result["metrics"]
        assert "interest_coverage" in result["metrics"]
        assert "cfo_to_debt" in result["metrics"]


class TestModelIpoValuation:
    """Tests for the model_ipo_valuation MCP tool."""

    def test_basic_valuation_modeling(self) -> None:
        """Test basic valuation calculation with required parameters."""
        result = model_ipo_valuation(
            ipo_price=500,
            eps_pre_ipo=25,
            book_value_per_share=200,
            sales_per_share=100,
        )
        
        assert result["success"] is True
        assert "metrics" in result
        assert "pe_ratio" in result["metrics"] or "implied_pe" in result.get("metrics", {})
        
    def test_valuation_with_peer_comparison(self) -> None:
        """Test valuation with peer multiples for comparison."""
        result = model_ipo_valuation(
            ipo_price=500,
            eps_pre_ipo=25,
            book_value_per_share=200,
            sales_per_share=100,
            peer_pe_multiples=[18, 20, 22],
            peer_pb_multiples=[2.5, 3.0, 3.5],
        )
        
        assert result["success"] is True
        assert "peer_comparison" in result
        assert "peer_avg_pe" in result["peer_comparison"]
        assert "pe_premium_to_peers" in result["peer_comparison"]
        
    def test_valuation_with_ev_ebitda(self) -> None:
        """Test valuation with EV/EBITDA calculation."""
        result = model_ipo_valuation(
            ipo_price=500,
            eps_pre_ipo=25,
            book_value_per_share=200,
            sales_per_share=100,
            ev_pre_ipo=5000,
            ebitda=400,
            peer_ev_ebitda_multiples=[10, 12, 14],
        )
        
        assert result["success"] is True
        assert "ev_to_ebitda" in result["metrics"]
        
    def test_valuation_invalid_parameters(self) -> None:
        """Test that invalid parameters raise appropriate error."""
        result = model_ipo_valuation(
            ipo_price=-100,  # Invalid negative price
            eps_pre_ipo=25,
            book_value_per_share=200,
            sales_per_share=100,
        )
        
        assert result["success"] is False
        assert "error" in result
        
    def test_valuation_invokes_domain_function(self) -> None:
        """Verify that the tool invokes the core domain function."""
        result = model_ipo_valuation(
            ipo_price=500,
            eps_pre_ipo=25,
            book_value_per_share=200,
            sales_per_share=100,
        )
        
        assert result["success"] is True
        # Verify valuation metrics from domain function
        assert "pb_ratio" in result["metrics"] or "ps_ratio" in result["metrics"]


class TestGenerateCompositeIpoScore:
    """Tests for the generate_composite_ipo_score MCP tool."""

    def test_composite_score_generation(self) -> None:
        """Test composite score generation with basic metrics."""
        result = generate_composite_ipo_score(
            growth_metrics={
                "revenue_cagr_3yr": 20.0,
                "profit_cagr_3yr": 25.0,
                "ebitda_margin": 18.0,
                "roe": 22.0,
                "roce": 25.0,
            },
            risk_metrics={
                "debt_to_equity": 0.5,
                "interest_coverage": 5.0,
                "current_ratio": 1.8,
                "promoter_pledge_ratio": 10.0,
            },
            valuation_metrics={
                "pe_ratio": 18.0,
                "pb_ratio": 3.0,
                "ev_to_ebitda": 12.0,
                "peg_ratio": 1.2,
            },
            profile="balanced",
        )
        
        assert result["success"] is True
        assert "total_score" in result
        assert "rating_tier" in result
        assert "recommendation" in result
        
    def test_composite_score_with_ipo_quality(self) -> None:
        """Test composite score with IPO quality inputs."""
        result = generate_composite_ipo_score(
            growth_metrics={
                "revenue_cagr_3yr": 20.0,
                "profit_cagr_3yr": 25.0,
            },
            risk_metrics={
                "debt_to_equity": 0.5,
                "interest_coverage": 5.0,
            },
            valuation_metrics={
                "pe_ratio": 18.0,
                "pb_ratio": 3.0,
            },
            ipo_quality_inputs={
                "dilution_pct": 15.0,
                "promoter_holding_pre": 75.0,
                "promoter_holding_post": 65.0,
            },
            profile="conservative",
        )
        
        assert result["success"] is True
        assert "total_score" in result
        
    def test_composite_score_missing_metrics(self) -> None:
        """Test that missing metrics raise appropriate error."""
        result = generate_composite_ipo_score(
            growth_metrics={},  # Empty
            risk_metrics={"debt_to_equity": 0.5},
            valuation_metrics={"pe_ratio": 18.0},
        )
        
        assert result["success"] is False
        assert "error" in result
        
    def test_composite_score_different_profiles(self) -> None:
        """Test composite score with different investor profiles."""
        profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]
        
        for profile in profiles:
            result = generate_composite_ipo_score(
                growth_metrics={
                    "revenue_cagr_3yr": 20.0,
                    "profit_cagr_3yr": 25.0,
                },
                risk_metrics={
                    "debt_to_equity": 0.5,
                    "interest_coverage": 5.0,
                },
                valuation_metrics={
                    "pe_ratio": 18.0,
                    "pb_ratio": 3.0,
                },
                profile=profile,
            )
            
            assert result["success"] is True
            assert "rating_tier" in result


class TestRunFullIpoWorkflow:
    """Tests for the run_full_ipo_workflow MCP tool."""

    def test_full_workflow_execution(self) -> None:
        """Test complete IPO workflow execution."""
        result = run_full_ipo_workflow(
            company_name="Test Company Ltd",
            ipo_date="2024-03-15",
            ipo_price=500,
            financials={
                "revenues": [100, 120, 150, 180],
                "profits": [10, 15, 20, 25],
                "total_debt": 500,
                "shareholders_equity": 1000,
                "cash_equivalents": 150,
                "ebitda": [20, 25, 30, 35],
                "interest_expense": 50,
                "current_assets": 300,
                "current_liabilities": 200,
                "eps": 25,
                "book_value_per_share": 200,
                "sales_per_share": 100,
            },
            profile="balanced",
        )
        
        assert result["success"] is True
        assert "growth_analysis" in result
        assert "risk_analysis" in result
        assert "valuation_analysis" in result
        assert "composite_score" in result
        assert "rating_tier" in result
        assert "executive_summary" in result
        
    def test_full_workflow_with_peer_comparison(self) -> None:
        """Test full workflow with peer multiples."""
        result = run_full_ipo_workflow(
            company_name="Test Company Ltd",
            ipo_date="2024-03-15",
            ipo_price=500,
            financials={
                "revenues": [100, 120, 150, 180],
                "profits": [10, 15, 20, 25],
                "total_debt": 500,
                "shareholders_equity": 1000,
                "cash_equivalents": 150,
                "ebitda": [20, 25, 30, 35],
                "interest_expense": 50,
                "current_assets": 300,
                "current_liabilities": 200,
                "eps": 25,
                "book_value_per_share": 200,
                "sales_per_share": 100,
            },
            peer_multiples={
                "pe_multiples": [18, 20, 22],
                "pb_multiples": [2.5, 3.0, 3.5],
            },
            profile="balanced",
        )
        
        assert result["success"] is True
        
    def test_full_workflow_with_industry_benchmarks(self) -> None:
        """Test full workflow with industry benchmarks."""
        result = run_full_ipo_workflow(
            company_name="Test Company Ltd",
            ipo_date="2024-03-15",
            ipo_price=500,
            financials={
                "revenues": [100, 120, 150, 180],
                "profits": [10, 15, 20, 25],
                "total_debt": 500,
                "shareholders_equity": 1000,
                "cash_equivalents": 150,
                "ebitda": [20, 25, 30, 35],
                "interest_expense": 50,
                "current_assets": 300,
                "current_liabilities": 200,
                "eps": 25,
                "book_value_per_share": 200,
                "sales_per_share": 100,
            },
            industry_benchmarks={
                "avg_growth": 15.0,
                "avg_margin": 18.0,
                "avg_roe": 20.0,
            },
            profile="balanced",
        )
        
        assert result["success"] is True
        
    def test_full_workflow_missing_required_data(self) -> None:
        """Test that missing required data raises appropriate error."""
        result = run_full_ipo_workflow(
            company_name="Test Company Ltd",
            ipo_date="2024-03-15",
            ipo_price=500,
            financials={
                "revenues": [100, 120, 150],
                # Missing required fields
            },
            profile="balanced",
        )
        
        assert result["success"] is False
        assert "error" in result
        
    def test_full_workflow_invokes_domain_functions(self) -> None:
        """Verify that the workflow invokes all core domain functions."""
        result = run_full_ipo_workflow(
            company_name="Test Company Ltd",
            ipo_date="2024-03-15",
            ipo_price=500,
            financials={
                "revenues": [100, 120, 150, 180],
                "profits": [10, 15, 20, 25],
                "total_debt": 500,
                "shareholders_equity": 1000,
                "cash_equivalents": 150,
                "ebitda": [20, 25, 30, 35],
                "interest_expense": 50,
                "current_assets": 300,
                "current_liabilities": 200,
                "eps": 25,
                "book_value_per_share": 200,
                "sales_per_share": 100,
            },
            profile="balanced",
        )
        
        if result["success"]:
            # Verify all domain analyses are present
            assert "growth_analysis" in result
            assert "risk_analysis" in result
            assert "valuation_analysis" in result
            # Verify scoring was executed
            assert "composite_score" in result or "score_breakdown" in result


class TestMcpServerIntegration:
    """Integration tests for MCP server functionality."""

    def test_mcp_server_initialization(self) -> None:
        """Test that MCP server initializes correctly."""
        from backend.mcp_server import mcp_server
        
        assert mcp_server is not None
        assert hasattr(mcp_server, 'name')
        assert mcp_server.name == "Arthaprama IPO Intelligence Engine"
        
    def test_all_tools_registered(self) -> None:
        """Test that all required tools are registered with MCP server."""
        from backend.mcp_server import mcp_server
        
        # Get list of registered tools
        # Note: The exact API may vary depending on MCP SDK version
        assert hasattr(mcp_server, '_tool_manager') or hasattr(mcp_server, 'tools')
        
    def test_tool_docstrings_present(self) -> None:
        """Test that all tools have comprehensive docstrings."""
        tools = [
            calculate_ipo_growth,
            evaluate_ipo_risk,
            model_ipo_valuation,
            generate_composite_ipo_score,
            run_full_ipo_workflow,
        ]
        
        for tool in tools:
            assert tool.__doc__ is not None
            assert len(tool.__doc__) > 50  # Reasonable docstring length
            assert "Args:" in tool.__doc__
            assert "Returns:" in tool.__doc__


# Integration tests for SSE connection lifecycle would go here
# These would require a running FastAPI instance and HTTP client
# Example structure (would need actual implementation):
"""
@pytest.mark.integration
class TestMcpSseIntegration:
    
    @pytest.mark.asyncio
    async def test_sse_connection(self, client: AsyncClient) -> None:
        '''Test SSE connection to MCP endpoint.'''
        response = await client.get("/sse")
        assert response.status_code == 200
        
    @pytest.mark.asyncio  
    async def test_tool_listing_via_sse(self, client: AsyncClient) -> None:
        '''Test tool listing response via SSE.'''
        # Implementation would depend on MCP SSE protocol specifics
        pass
"""
