"""
Pydantic v2 Data Structure Validation Schemas for Arthaprama Backend.

This module defines comprehensive Pydantic v2 models for validating nested
financial data structures used in IPO analysis pipelines.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class FinancialYearData(BaseModel):
    """Schema for a single financial year's data."""

    revenue: Decimal = Field(..., description="Total revenue for the year", ge=0)
    pat: Decimal = Field(..., description="Profit After Tax", ge=0)
    ebitda: Decimal = Field(..., description="EBITDA", ge=0)
    ebit: Decimal = Field(default=Decimal("0"), description="EBIT", ge=0)
    eps: Decimal = Field(default=Decimal("0"), description="Earnings Per Share", ge=0)
    cfo: Decimal = Field(default=Decimal("0"), description="Cash Flow from Operations")
    capex: Decimal = Field(default=Decimal("0"), description="Capital Expenditure", ge=0)
    total_assets: Decimal = Field(default=Decimal("0"), description="Total Assets", ge=0)
    total_liabilities: Decimal = Field(default=Decimal("0"), description="Total Liabilities", ge=0)


class BalanceSheetData(BaseModel):
    """Schema for balance sheet data."""

    total_debt: Decimal = Field(default=Decimal("0"), description="Total Debt", ge=0)
    shareholders_equity: Decimal = Field(default=Decimal("0"), description="Shareholders Equity", ge=0)
    cash_equivalents: Decimal = Field(default=Decimal("0"), description="Cash & Cash Equivalents", ge=0)
    current_assets: Decimal = Field(default=Decimal("0"), description="Current Assets", ge=0)
    current_liabilities: Decimal = Field(default=Decimal("0"), description="Current Liabilities", ge=0)
    inventory: Decimal = Field(default=Decimal("0"), description="Inventory", ge=0)
    net_worth: Decimal = Field(default=Decimal("0"), description="Net Worth", ge=0)
    contingent_liabilities: Decimal = Field(default=Decimal("0"), description="Contingent Liabilities", ge=0)


class GrowthDataInput(BaseModel):
    """Schema for growth calculation inputs."""

    revenue_current: Decimal = Field(..., description="Current period revenue", ge=0)
    revenue_previous: Decimal = Field(..., description="Previous period revenue", ge=0)
    revenue_3yrs_ago: Decimal = Field(default=Decimal("0"), description="Revenue 3 years ago", ge=0)
    pat_current: Decimal = Field(..., description="Current period PAT", ge=0)
    pat_previous: Decimal = Field(..., description="Previous period PAT", ge=0)
    pat_3yrs_ago: Decimal = Field(default=Decimal("0"), description="PAT 3 years ago", ge=0)
    ebitda_current: Decimal = Field(..., description="Current period EBITDA", ge=0)
    ebitda_previous: Decimal = Field(..., description="Previous period EBITDA", ge=0)
    eps_current: Decimal = Field(..., description="Current period EPS", ge=0)
    eps_previous: Decimal = Field(..., description="Previous period EPS", ge=0)
    ebit: Decimal = Field(default=Decimal("0"), description="EBIT", ge=0)
    cfo_current: Decimal = Field(default=Decimal("0"), description="Current CFO")
    cfo_previous: Decimal = Field(default=Decimal("0"), description="Previous CFO")
    avg_shareholders_equity: Decimal = Field(default=Decimal("0"), description="Average Shareholders Equity", ge=0)
    capital_employed: Decimal = Field(default=Decimal("0"), description="Capital Employed", ge=0)


class RiskDataInput(BaseModel):
    """Schema for risk calculation inputs."""

    total_debt: Decimal = Field(default=Decimal("0"), description="Total Debt", ge=0)
    shareholders_equity: Decimal = Field(default=Decimal("0"), description="Shareholders Equity", ge=0)
    cash_equivalents: Decimal = Field(default=Decimal("0"), description="Cash & Cash Equivalents", ge=0)
    ebitda: Decimal = Field(default=Decimal("0"), description="EBITDA", ge=0)
    ebit: Decimal = Field(default=Decimal("0"), description="EBIT", ge=0)
    interest_expense: Decimal = Field(default=Decimal("0"), description="Interest Expense", ge=0)
    current_assets: Decimal = Field(default=Decimal("0"), description="Current Assets", ge=0)
    current_liabilities: Decimal = Field(default=Decimal("0"), description="Current Liabilities", ge=0)
    inventory: Decimal = Field(default=Decimal("0"), description="Inventory", ge=0)
    cfo: Decimal = Field(default=Decimal("0"), description="Cash Flow from Operations")
    pat: Decimal = Field(default=Decimal("0"), description="Profit After Tax")
    capex: Decimal = Field(default=Decimal("0"), description="Capital Expenditure", ge=0)
    largest_customer_rev: Decimal = Field(default=Decimal("0"), description="Revenue from Largest Customer", ge=0)
    total_rev: Decimal = Field(default=Decimal("0"), description="Total Revenue", ge=0)
    pledged_shares: Decimal = Field(default=Decimal("0"), description="Pledged Shares", ge=0)
    total_promoter_shares: Decimal = Field(default=Decimal("0"), description="Total Promoter Shares", ge=0)
    contingent_liabilities: Decimal = Field(default=Decimal("0"), description="Contingent Liabilities", ge=0)
    net_worth: Decimal = Field(default=Decimal("0"), description="Net Worth", ge=0)


class ValuationDataInput(BaseModel):
    """Schema for valuation calculation inputs."""

    market_cap: Decimal = Field(..., description="Market Capitalization", ge=0)
    pat: Decimal = Field(default=Decimal("0"), description="Profit After Tax")
    book_value: Decimal = Field(default=Decimal("0"), description="Book Value", ge=0)
    revenue: Decimal = Field(default=Decimal("0"), description="Revenue", ge=0)
    ebitda: Decimal = Field(default=Decimal("0"), description="EBITDA", ge=0)
    eps: Decimal = Field(default=Decimal("0"), description="Earnings Per Share")
    ipo_price: Decimal = Field(default=Decimal("0"), description="IPO Price", ge=0)
    total_debt: Decimal = Field(default=Decimal("0"), description="Total Debt", ge=0)
    cash_equivalents: Decimal = Field(default=Decimal("0"), description="Cash & Cash Equivalents", ge=0)
    free_cash_flow: Decimal = Field(default=Decimal("0"), description="Free Cash Flow")
    new_shares: Decimal = Field(default=Decimal("0"), description="New Shares Issued", ge=0)
    post_ipo_shares: Decimal = Field(default=Decimal("0"), description="Post-IPO Shares", ge=0)
    post_ipo_diluted_shares: Decimal = Field(default=Decimal("0"), description="Post-IPO Diluted Shares", ge=0)
    post_ipo_pat: Decimal = Field(default=Decimal("0"), description="Post-IPO PAT")
    expected_eps_growth_pct: Decimal = Field(default=Decimal("0"), description="Expected EPS Growth %")


class PeerDataInput(BaseModel):
    """Schema for peer comparison data."""

    peer_median_pe: Decimal = Field(default=Decimal("0"), description="Peer Median P/E Ratio")
    peer_median_ev_ebitda: Decimal = Field(default=Decimal("0"), description="Peer Median EV/EBITDA")
    peer_median_pb: Decimal = Field(default=Decimal("0"), description="Peer Median P/B Ratio")
    peer_market_caps: list[Decimal] = Field(default_factory=list, description="List of Peer Market Caps")


class IPOSpecificDataInput(BaseModel):
    """Schema for IPO-specific data inputs."""

    ipo_dilution: Decimal = Field(default=Decimal("0"), description="IPO Dilution %", ge=0, le=100)
    promoter_holding_pre_ipo: Decimal = Field(default=Decimal("0"), description="Promoter Holding Pre-IPO %", ge=0, le=100)
    promoter_holding_post_ipo: Decimal = Field(default=Decimal("0"), description="Promoter Holding Post-IPO %", ge=0, le=100)
    promoter_pledge_ratio: Decimal = Field(default=Decimal("0"), description="Promoter Pledge Ratio %", ge=0, le=100)
    issue_size: Decimal = Field(default=Decimal("0"), description="Issue Size", ge=0)
    fresh_issue: Decimal = Field(default=Decimal("0"), description="Fresh Issue Amount", ge=0)
    offer_for_sale: Decimal = Field(default=Decimal("0"), description="Offer for Sale Amount", ge=0)
    lot_size: Decimal = Field(default=Decimal("0"), description="Lot Size", ge=0)
    price_band_lower: Decimal = Field(default=Decimal("0"), description="Price Band Lower Limit", ge=0)
    price_band_upper: Decimal = Field(default=Decimal("0"), description="Price Band Upper Limit", ge=0)


class IPOEvaluationRequest(BaseModel):
    """
    Main request schema for IPO evaluation endpoint.

    This schema aggregates all required input data for comprehensive
    IPO analysis including growth, risk, valuation, and IPO-specific factors.
    """

    company_name: str = Field(..., description="Name of the company going public")
    sector: str = Field(..., description="Industry sector of the company")
    growth_data: GrowthDataInput = Field(..., description="Growth metrics data")
    risk_data: RiskDataInput = Field(..., description="Risk assessment data")
    valuation_data: ValuationDataInput = Field(..., description="Valuation data")
    ipo_data: IPOSpecificDataInput = Field(..., description="IPO-specific data")
    peer_data: PeerDataInput | None = Field(default=None, description="Peer comparison data")
    profile: str = Field(
        default="balanced",
        description="Investor profile strategy (balanced, conservative, aggressive_growth, deep_value)",
    )

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v: str) -> str:
        """Validate that profile is one of the allowed strategies."""
        valid_profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]
        if v.lower() not in valid_profiles:
            raise ValueError(f"Invalid profile '{v}'. Must be one of: {valid_profiles}")
        return v.lower()


class MetricDetail(BaseModel):
    """Schema for individual metric details in response."""

    value: float = Field(..., description="Calculated metric value")
    threshold: float | None = Field(default=None, description="Threshold/benchmark value")


class ScoreBreakdownResponse(BaseModel):
    """Schema for score breakdown response."""

    growth_score: float = Field(..., description="Growth pillar score", ge=0, le=30)
    risk_score: float = Field(..., description="Risk pillar score", ge=0, le=30)
    valuation_score: float = Field(..., description="Valuation pillar score", ge=0, le=30)
    ipo_quality_score: float = Field(..., description="IPO quality pillar score", ge=0, le=10)
    total_score: float = Field(..., description="Total composite score", ge=0, le=100)
    growth_details: dict[str, Any] = Field(default_factory=dict, description="Detailed growth scoring breakdown")
    risk_details: dict[str, Any] = Field(default_factory=dict, description="Detailed risk scoring breakdown")
    valuation_details: dict[str, Any] = Field(default_factory=dict, description="Detailed valuation scoring breakdown")
    ipo_quality_details: dict[str, Any] = Field(default_factory=dict, description="Detailed IPO quality scoring breakdown")


class GrowthMetricsResponse(BaseModel):
    """Schema for growth metrics calculation response."""

    revenue_growth_yoy: float = Field(..., description="Revenue Growth YoY %")
    profit_growth_yoy: float = Field(..., description="PAT Growth YoY %")
    ebitda_growth_yoy: float = Field(..., description="EBITDA Growth YoY %")
    eps_growth_yoy: float = Field(..., description="EPS Growth YoY %")
    revenue_cagr_3yr: float = Field(..., description="Revenue CAGR 3-Year")
    pat_cagr_3yr: float = Field(..., description="PAT CAGR 3-Year")
    ebitda_margin: float = Field(..., description="EBITDA Margin %")
    pat_margin: float = Field(..., description="PAT Margin %")
    roe: float = Field(..., description="Return on Equity %")
    roce: float = Field(..., description="Return on Capital Employed %")
    cfo_growth: float = Field(..., description="CFO Growth YoY %")


class RiskMetricsResponse(BaseModel):
    """Schema for risk metrics calculation response."""

    debt_to_equity: float = Field(..., description="Debt-to-Equity Ratio")
    net_debt: float = Field(..., description="Net Debt")
    net_debt_to_ebitda: float = Field(..., description="Net Debt/EBITDA")
    interest_coverage: float = Field(..., description="Interest Coverage Ratio")
    current_ratio: float = Field(..., description="Current Ratio")
    quick_ratio: float = Field(..., description="Quick Ratio")
    cfo_to_debt: float = Field(..., description="CFO to Debt Ratio")
    cfo_to_pat: float = Field(..., description="CFO to PAT Ratio")
    free_cash_flow: float = Field(..., description="Free Cash Flow")
    fcf_to_pat: float = Field(..., description="FCF to PAT Ratio")
    customer_concentration: float = Field(..., description="Customer Concentration %")
    promoter_pledge_ratio: float = Field(..., description="Promoter Pledge Ratio %")
    contingent_liabilities_to_nw: float = Field(..., description="Contingent Liabilities to Net Worth %")


class ValuationMetricsResponse(BaseModel):
    """Schema for valuation metrics calculation response."""

    pe_ratio: float = Field(..., description="Price-to-Earnings Ratio")
    pb_ratio: float = Field(..., description="Price-to-Book Ratio")
    ps_ratio: float = Field(..., description="Price-to-Sales Ratio")
    ev_to_ebitda: float = Field(..., description="EV/EBITDA")
    ev_to_sales: float = Field(..., description="EV/Sales")
    peg_ratio: float = Field(..., description="PEG Ratio")
    earnings_yield: float = Field(..., description="Earnings Yield %")
    price_to_fcf: float = Field(..., description="Price to Free Cash Flow")
    enterprise_value: float = Field(..., description="Enterprise Value")
    pe_premium_vs_peer: float = Field(..., description="P/E Premium vs Peer %")
    ev_ebitda_premium_vs_peer: float = Field(..., description="EV/EBITDA Premium vs Peer %")
    ipo_dilution: float = Field(..., description="IPO Dilution %")
    post_ipo_eps: float = Field(..., description="Post-IPO EPS")


class IPOEvaluationResponse(BaseModel):
    """Main response schema for IPO evaluation endpoint."""

    company_name: str = Field(..., description="Company name")
    sector: str = Field(..., description="Industry sector")
    profile_used: str = Field(..., description="Investor profile strategy used")
    total_score: float = Field(..., description="Total composite score out of 100")
    score_breakdown: ScoreBreakdownResponse = Field(..., description="Detailed score breakdown by pillar")
    growth_metrics: GrowthMetricsResponse | None = Field(default=None, description="Calculated growth metrics")
    risk_metrics: RiskMetricsResponse | None = Field(default=None, description="Calculated risk metrics")
    valuation_metrics: ValuationMetricsResponse | None = Field(default=None, description="Calculated valuation metrics")

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "Example Tech Ltd",
                "sector": "Technology",
                "profile_used": "balanced",
                "total_score": 72.5,
            }
        }
    }


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Any = Field(default=None, description="Additional error details")


# =============================================================================
# FULL IPO ANALYSIS WORKFLOW SCHEMAS
# =============================================================================


class IPOPOMetadata(BaseModel):
    """Schema for basic IPO metadata."""

    company_name: str = Field(..., description="Name of the company going public")
    sector: str = Field(..., description="Industry sector of the company")
    price_band_lower: Decimal = Field(default=Decimal("0"), description="Price Band Lower Limit", ge=0)
    price_band_upper: Decimal = Field(default=Decimal("0"), description="Price Band Upper Limit", ge=0)
    issue_size: Decimal = Field(default=Decimal("0"), description="Issue Size", ge=0)
    fresh_issue: Decimal = Field(default=Decimal("0"), description="Fresh Issue Amount", ge=0)
    offer_for_sale: Decimal = Field(default=Decimal("0"), description="Offer for Sale Amount", ge=0)


class FullIPOAnalysisRequest(BaseModel):
    """
    Request schema for full IPO analysis workflow endpoint.

    This schema aggregates all required input data for comprehensive
    IPO analysis through the unified workflow engine.
    """

    meta: IPOPOMetadata = Field(..., description="Basic IPO metadata")
    growth_data: GrowthDataInput = Field(..., description="Growth metrics data")
    risk_data: RiskDataInput = Field(..., description="Risk assessment data")
    valuation_data: ValuationDataInput = Field(..., description="Valuation data")
    ipo_data: IPOSpecificDataInput = Field(..., description="IPO-specific data")
    peer_data: PeerDataInput | None = Field(default=None, description="Peer comparison data")
    profile: str = Field(
        default="balanced",
        description="Investor profile strategy (balanced, conservative, aggressive_growth, deep_value)",
    )

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v: str) -> str:
        """Validate that profile is one of the allowed strategies."""
        valid_profiles = ["balanced", "conservative", "aggressive_growth", "deep_value"]
        if v.lower() not in valid_profiles:
            raise ValueError(f"Invalid profile '{v}'. Must be one of: {valid_profiles}")
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class GrowthAnalysisResponse(BaseModel):
    """Schema for growth analysis result."""

    metrics: dict[str, float] = Field(default_factory=dict, description="Calculated growth metrics")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    success: bool = Field(default=True, description="Whether calculation succeeded")


class RiskAnalysisResponse(BaseModel):
    """Schema for risk analysis result."""

    metrics: dict[str, float] = Field(default_factory=dict, description="Calculated risk metrics")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    success: bool = Field(default=True, description="Whether calculation succeeded")


class ValuationAnalysisResponse(BaseModel):
    """Schema for valuation analysis result."""

    metrics: dict[str, float] = Field(default_factory=dict, description="Calculated valuation metrics")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    success: bool = Field(default=True, description="Whether calculation succeeded")


class FullIPOAnalysisResponse(BaseModel):
    """
    Response schema for full IPO analysis workflow endpoint.

    Contains structured output with nested objects for growth_analysis,
    risk_analysis, valuation_analysis, and composite_score.
    """

    growth_analysis: GrowthAnalysisResponse = Field(..., description="Growth metrics analysis results")
    risk_analysis: RiskAnalysisResponse = Field(..., description="Risk metrics analysis results")
    valuation_analysis: ValuationAnalysisResponse = Field(..., description="Valuation metrics analysis results")
    composite_score: ScoreBreakdownResponse | None = Field(default=None, description="Composite IPO score breakdown")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered during analysis")
    success: bool = Field(default=True, description="Whether full analysis succeeded")

    model_config = {
        "json_schema_extra": {
            "example": {
                "growth_analysis": {
                    "metrics": {
                        "revenue_growth_yoy": 20.0,
                        "profit_growth_yoy": 50.0,
                        "ebitda_margin": 16.67,
                        "roe": 18.75,
                    },
                    "errors": [],
                    "success": True,
                },
                "risk_analysis": {
                    "metrics": {
                        "debt_to_equity": 0.25,
                        "interest_coverage": 9.0,
                        "current_ratio": 2.0,
                    },
                    "errors": [],
                    "success": True,
                },
                "valuation_analysis": {
                    "metrics": {
                        "pe_ratio": 13.33,
                        "pb_ratio": 2.5,
                        "ev_to_ebitda": 10.0,
                    },
                    "errors": [],
                    "success": True,
                },
                "composite_score": {
                    "growth_score": 22.5,
                    "risk_score": 25.0,
                    "valuation_score": 20.0,
                    "ipo_quality_score": 8.0,
                    "total_score": 75.5,
                    "growth_details": {},
                    "risk_details": {},
                    "valuation_details": {},
                    "ipo_quality_details": {},
                },
                "errors": [],
                "success": True,
            }
        }
    }
