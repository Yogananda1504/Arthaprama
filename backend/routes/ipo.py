"""
IPO Routes for Arthaprama FastAPI Backend.

This module exposes asynchronous REST endpoints mapped cleanly to process
raw IPO analytics queries with profile-aware evaluation.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from arthaprama.config import ProfileStrategy, get_profile
from arthaprama.ipo.growth import calculate_all_growth_metrics
from arthaprama.ipo.risk import calculate_all_risk_metrics
from arthaprama.ipo.scoring import generate_ipo_score
from arthaprama.ipo.valuation import calculate_all_valuation_metrics
from arthaprama.ipo.workflow import IPOWorkflowEngine
from backend.schemas import (
    ErrorResponse,
    FullIPOAnalysisRequest,
    FullIPOAnalysisResponse,
    GrowthAnalysisResponse,
    GrowthMetricsResponse,
    IPOEvaluationRequest,
    IPOEvaluationResponse,
    RiskAnalysisResponse,
    RiskMetricsResponse,
    ScoreBreakdownResponse,
    ValuationAnalysisResponse,
    ValuationMetricsResponse,
)

router = APIRouter(prefix="/api/v1/ipo", tags=["IPO Analysis"])


@router.post(
    "/evaluate",
    response_model=IPOEvaluationResponse,
    responses={
        200: {"description": "Successful IPO evaluation"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Evaluate an IPO",
    description="""
    Perform comprehensive IPO analysis using the 100-point scoring matrix.
    
    This endpoint evaluates an IPO across four pillars:
    - **Growth** (30 points): Revenue growth, profit growth, margins, ROE, ROCE
    - **Risk** (30 points): Debt ratios, liquidity, cash flow quality, promoter metrics
    - **Valuation** (30 points): P/E, P/B, EV/EBITDA, PEG, peer comparisons
    - **IPO Quality** (10 points): Dilution, promoter holding, pledge ratio
    
    The evaluation uses investor profile strategies to weight the scoring:
    - `balanced`: Equal weighting across all pillars (default)
    - `conservative`: Higher weight on risk mitigation
    - `aggressive_growth`: Higher weight on growth metrics
    - `deep_value`: Higher weight on valuation metrics
    """,
)
async def evaluate_ipo(request: IPOEvaluationRequest) -> IPOEvaluationResponse:
    """
    Evaluate an IPO using the 100-point scoring matrix.

    Args:
        request: IPO evaluation request containing all financial data.

    Returns:
        Comprehensive evaluation response with scores and metrics.

    Raises:
        HTTPException: If evaluation fails due to invalid data.
    """
    try:
        # Convert Pydantic models to dictionaries for calculation functions
        growth_data = request.growth_data.model_dump()
        risk_data = request.risk_data.model_dump()
        valuation_data = request.valuation_data.model_dump()
        ipo_data = request.ipo_data.model_dump()

        # Convert peer data if provided
        peer_data = None
        if request.peer_data:
            peer_data = request.peer_data.model_dump()

        # Generate score using the scoring engine
        score_result = generate_ipo_score(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile=request.profile,
            peer_data=peer_data,
        )

        # Calculate individual metrics for response
        growth_metrics_dict = calculate_all_growth_metrics(growth_data)
        risk_metrics_dict = calculate_all_risk_metrics(risk_data)
        valuation_metrics_dict = calculate_all_valuation_metrics(valuation_data, peer_data)

        # Build response objects
        score_breakdown = ScoreBreakdownResponse(
            growth_score=float(score_result.growth_score),
            risk_score=float(score_result.risk_score),
            valuation_score=float(score_result.valuation_score),
            ipo_quality_score=float(score_result.ipo_quality_score),
            total_score=float(score_result.total_score),
            growth_details=score_result.growth_details,
            risk_details=score_result.risk_details,
            valuation_details=score_result.valuation_details,
            ipo_quality_details=score_result.ipo_quality_details,
        )

        growth_metrics = GrowthMetricsResponse(
            revenue_growth_yoy=float(growth_metrics_dict.get("revenue_growth_yoy", 0)),
            profit_growth_yoy=float(growth_metrics_dict.get("profit_growth_yoy", 0)),
            ebitda_growth_yoy=float(growth_metrics_dict.get("ebitda_growth_yoy", 0)),
            eps_growth_yoy=float(growth_metrics_dict.get("eps_growth_yoy", 0)),
            revenue_cagr_3yr=float(growth_metrics_dict.get("revenue_cagr_3yr", 0)),
            pat_cagr_3yr=float(growth_metrics_dict.get("pat_cagr_3yr", 0)),
            ebitda_margin=float(growth_metrics_dict.get("ebitda_margin", 0)),
            pat_margin=float(growth_metrics_dict.get("pat_margin", 0)),
            roe=float(growth_metrics_dict.get("roe", 0)),
            roce=float(growth_metrics_dict.get("roce", 0)),
            cfo_growth=float(growth_metrics_dict.get("cfo_growth", 0)),
        )

        risk_metrics = RiskMetricsResponse(
            debt_to_equity=float(risk_metrics_dict.get("debt_to_equity", 0)),
            net_debt=float(risk_metrics_dict.get("net_debt", 0)),
            net_debt_to_ebitda=float(risk_metrics_dict.get("net_debt_to_ebitda", 0)),
            interest_coverage=float(risk_metrics_dict.get("interest_coverage", 0)),
            current_ratio=float(risk_metrics_dict.get("current_ratio", 0)),
            quick_ratio=float(risk_metrics_dict.get("quick_ratio", 0)),
            cfo_to_debt=float(risk_metrics_dict.get("cfo_to_debt", 0)),
            cfo_to_pat=float(risk_metrics_dict.get("cfo_to_pat", 0)),
            free_cash_flow=float(risk_metrics_dict.get("free_cash_flow", 0)),
            fcf_to_pat=float(risk_metrics_dict.get("fcf_to_pat", 0)),
            customer_concentration=float(risk_metrics_dict.get("customer_concentration", 0)),
            promoter_pledge_ratio=float(risk_metrics_dict.get("promoter_pledge_ratio", 0)),
            contingent_liabilities_to_nw=float(risk_metrics_dict.get("contingent_liabilities_to_nw", 0)),
        )

        valuation_metrics = ValuationMetricsResponse(
            pe_ratio=float(valuation_metrics_dict.get("pe_ratio", 0)),
            pb_ratio=float(valuation_metrics_dict.get("pb_ratio", 0)),
            ps_ratio=float(valuation_metrics_dict.get("ps_ratio", 0)),
            ev_to_ebitda=float(valuation_metrics_dict.get("ev_to_ebitda", 0)),
            ev_to_sales=float(valuation_metrics_dict.get("ev_to_sales", 0)),
            peg_ratio=float(valuation_metrics_dict.get("peg_ratio", 0)),
            earnings_yield=float(valuation_metrics_dict.get("earnings_yield", 0)),
            price_to_fcf=float(valuation_metrics_dict.get("price_to_fcf", 0)),
            enterprise_value=float(valuation_metrics_dict.get("enterprise_value", 0)),
            pe_premium_vs_peer=float(valuation_metrics_dict.get("pe_premium_vs_peer", 0)),
            ev_ebitda_premium_vs_peer=float(valuation_metrics_dict.get("ev_ebitda_premium_vs_peer", 0)),
            ipo_dilution=float(valuation_metrics_dict.get("ipo_dilution", 0)),
            post_ipo_eps=float(valuation_metrics_dict.get("post_ipo_eps", 0)),
        )

        return IPOEvaluationResponse(
            company_name=request.company_name,
            sector=request.sector,
            profile_used=request.profile,
            total_score=float(score_result.total_score),
            score_breakdown=score_breakdown,
            growth_metrics=growth_metrics,
            risk_metrics=risk_metrics,
            valuation_metrics=valuation_metrics,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error during evaluation: {e!s}") from e


@router.get(
    "/scores/breakdown",
    response_model=dict[str, Any],
    summary="Get scoring breakdown explanation",
    description="Returns detailed explanation of how scores are calculated across all pillars.",
)
async def get_scoring_breakdown() -> dict[str, Any]:
    """
    Get detailed explanation of the scoring methodology.

    Returns:
        Dictionary explaining scoring weights and methodology.
    """
    return {
        "growth_score": {
            "max_points": 30,
            "metrics": [
                {"name": "Revenue Growth YoY", "weight": 2},
                {"name": "Profit Growth YoY", "weight": 3},
                {"name": "EBITDA Growth YoY", "weight": 2},
                {"name": "EPS Growth YoY", "weight": 2},
                {"name": "Revenue CAGR 3-Year", "weight": 3},
                {"name": "PAT CAGR 3-Year", "weight": 3},
                {"name": "EBITDA Margin", "weight": 2},
                {"name": "PAT Margin", "weight": 2},
                {"name": "ROE", "weight": 3},
                {"name": "ROCE", "weight": 3},
                {"name": "CFO Growth", "weight": 2},
            ],
        },
        "risk_score": {
            "max_points": 30,
            "metrics": [
                {"name": "Debt-to-Equity", "weight": 4},
                {"name": "Net Debt/EBITDA", "weight": 3},
                {"name": "Interest Coverage", "weight": 4},
                {"name": "Current Ratio", "weight": 3},
                {"name": "Quick Ratio", "weight": 2},
                {"name": "CFO to Debt", "weight": 3},
                {"name": "CFO to PAT", "weight": 3},
                {"name": "FCF to PAT", "weight": 2},
                {"name": "Customer Concentration", "weight": 2},
                {"name": "Promoter Pledge Ratio", "weight": 3},
                {"name": "Contingent Liabilities/NW", "weight": 2},
            ],
        },
        "valuation_score": {
            "max_points": 30,
            "metrics": [
                {"name": "P/E Ratio", "weight": 5},
                {"name": "P/B Ratio", "weight": 3},
                {"name": "P/S Ratio", "weight": 3},
                {"name": "EV/EBITDA", "weight": 5},
                {"name": "PEG Ratio", "weight": 5},
                {"name": "Earnings Yield", "weight": 3},
                {"name": "Price to FCF", "weight": 3},
                {"name": "P/E Premium vs Peer", "weight": 3},
            ],
        },
        "ipo_quality_score": {
            "max_points": 10,
            "metrics": [
                {"name": "IPO Dilution", "weight": 3},
                {"name": "Promoter Holding Post-IPO", "weight": 4},
                {"name": "Promoter Pledge Ratio", "weight": 3},
            ],
        },
        "total": {"max_points": 100},
    }


@router.get(
    "/profiles",
    response_model=dict[str, Any],
    summary="Get available investor profiles",
    description="Returns all available investor profile strategies and their configurations.",
)
async def get_profiles() -> dict[str, Any]:
    """
    Get all available investor profile configurations.

    Returns:
        Dictionary of profile names to their weight configurations.
    """
    profiles = {}
    for strategy in ProfileStrategy:
        profile = get_profile(strategy)
        profiles[strategy.value] = {
            "strategy": strategy.value,
            "weights": {k: float(v) for k, v in profile.weights.to_dict().items()},
            "thresholds": {k: float(v) for k, v in profile.thresholds.to_dict().items()},
        }
    return profiles


@router.get(
    "/profile/{profile_name}",
    response_model=dict[str, Any],
    summary="Get specific investor profile",
    description="Returns configuration for a specific investor profile strategy.",
)
async def get_profile_detail(profile_name: str) -> dict[str, Any]:
    """
    Get detailed configuration for a specific investor profile.

    Args:
        profile_name: Name of the profile (balanced, conservative, aggressive_growth, deep_value).

    Returns:
        Profile configuration dictionary.

    Raises:
        HTTPException: If profile name is invalid.
    """
    try:
        profile = get_profile(profile_name)
        return {
            "strategy": profile.strategy.value,
            "weights": {k: float(v) for k, v in profile.weights.to_dict().items()},
            "thresholds": {k: float(v) for k, v in profile.thresholds.to_dict().items()},
            "sector_overrides": profile.sector_overrides,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =============================================================================
# FULL IPO ANALYSIS WORKFLOW ENDPOINTS
# =============================================================================


@router.post(
    "/analyze",
    response_model=FullIPOAnalysisResponse,
    responses={
        200: {"description": "Successful full IPO analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Run full IPO analysis workflow",
    description="""
    Execute a comprehensive, end-to-end IPO analysis using the unified workflow engine.
    
    This endpoint orchestrates the sequential execution of:
    1. **Growth Analysis**: Revenue, profit, EBITDA, EPS growth metrics
    2. **Risk Analysis**: Debt ratios, liquidity, cash flow quality, promoter metrics
    3. **Valuation Analysis**: P/E, P/B, EV/EBITDA, peer comparisons
    4. **Composite Scoring**: 100-point scoring across all pillars
    
    The workflow returns a unified report containing all intermediate results
    and the final composite score.
    """,
)
async def analyze_full_ipo(request: FullIPOAnalysisRequest) -> FullIPOAnalysisResponse:
    """
    Run full IPO analysis workflow.

    Args:
        request: Full IPO analysis request containing all financial data.

    Returns:
        Comprehensive analysis response with all metrics and composite score.

    Raises:
        HTTPException: If analysis fails due to invalid data.
    """
    try:
        # Convert Pydantic models to dictionaries
        growth_data = request.growth_data.model_dump()
        risk_data = request.risk_data.model_dump()
        valuation_data = request.valuation_data.model_dump()
        ipo_data = request.ipo_data.model_dump()

        # Convert peer data if provided
        peer_data = None
        if request.peer_data:
            peer_data = request.peer_data.model_dump()

        # Execute workflow engine
        workflow = IPOWorkflowEngine()
        result = workflow.execute(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile=request.profile,
            peer_data=peer_data,
        )

        # Build response
        growth_analysis = GrowthAnalysisResponse(
            metrics=result.growth_analysis.to_dict()["metrics"],
            errors=result.growth_analysis.errors,
            success=result.growth_analysis.success,
        )

        risk_analysis = RiskAnalysisResponse(
            metrics=result.risk_analysis.to_dict()["metrics"],
            errors=result.risk_analysis.errors,
            success=result.risk_analysis.success,
        )

        valuation_analysis = ValuationAnalysisResponse(
            metrics=result.valuation_analysis.to_dict()["metrics"],
            errors=result.valuation_analysis.errors,
            success=result.valuation_analysis.success,
        )

        composite_score = None
        if result.composite_score:
            composite_score = ScoreBreakdownResponse(
                growth_score=float(result.composite_score.growth_score),
                risk_score=float(result.composite_score.risk_score),
                valuation_score=float(result.composite_score.valuation_score),
                ipo_quality_score=float(result.composite_score.ipo_quality_score),
                total_score=float(result.composite_score.total_score),
                growth_details=result.composite_score.growth_details,
                risk_details=result.composite_score.risk_details,
                valuation_details=result.composite_score.valuation_details,
                ipo_quality_details=result.composite_score.ipo_quality_details,
            )

        return FullIPOAnalysisResponse(
            growth_analysis=growth_analysis,
            risk_analysis=risk_analysis,
            valuation_analysis=valuation_analysis,
            composite_score=composite_score,
            errors=result.errors,
            success=result.success,
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e!s}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error during analysis: {e!s}") from e


@router.post(
    "/analyze/upload",
    response_model=FullIPOAnalysisResponse,
    responses={
        200: {"description": "Successful full IPO analysis from uploaded file"},
        400: {"model": ErrorResponse, "description": "Invalid file format or data"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Run full IPO analysis from uploaded file",
    description="""
    Upload a JSON file containing IPO data and execute the full analysis workflow.
    
    The uploaded file should contain valid JSON matching the FullIPOAnalysisRequest schema.
    Supported file formats: .json
    
    Example file structure:
    ```json
    {
        "meta": {
            "company_name": "Example Tech Ltd",
            "sector": "Technology",
            ...
        },
        "growth_data": {...},
        "risk_data": {...},
        "valuation_data": {...},
        "ipo_data": {...}
    }
    ```
    """,
)
async def analyze_ipo_from_upload(
    file: UploadFile = File(...),
) -> FullIPOAnalysisResponse:
    """
    Run full IPO analysis from an uploaded file.

    Args:
        file: Uploaded JSON file containing IPO data.

    Returns:
        Comprehensive analysis response with all metrics and composite score.

    Raises:
        HTTPException: If file parsing or analysis fails.
    """
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not file.filename.lower().endswith(".json"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file.filename}'. Only .json files are supported.",
            )

        # Read and parse file content
        contents = await file.read()
        try:
            data = json.loads(contents.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e!s}") from e

        # Validate against schema
        try:
            request = FullIPOAnalysisRequest.model_validate(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Schema validation failed: {e!s}") from e

        # Execute workflow (reuse the analyze function logic)
        growth_data = request.growth_data.model_dump()
        risk_data = request.risk_data.model_dump()
        valuation_data = request.valuation_data.model_dump()
        ipo_data = request.ipo_data.model_dump()

        peer_data = None
        if request.peer_data:
            peer_data = request.peer_data.model_dump()

        workflow = IPOWorkflowEngine()
        result = workflow.execute(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile=request.profile,
            peer_data=peer_data,
        )

        # Build response
        growth_analysis = GrowthAnalysisResponse(
            metrics=result.growth_analysis.to_dict()["metrics"],
            errors=result.growth_analysis.errors,
            success=result.growth_analysis.success,
        )

        risk_analysis = RiskAnalysisResponse(
            metrics=result.risk_analysis.to_dict()["metrics"],
            errors=result.risk_analysis.errors,
            success=result.risk_analysis.success,
        )

        valuation_analysis = ValuationAnalysisResponse(
            metrics=result.valuation_analysis.to_dict()["metrics"],
            errors=result.valuation_analysis.errors,
            success=result.valuation_analysis.success,
        )

        composite_score = None
        if result.composite_score:
            composite_score = ScoreBreakdownResponse(
                growth_score=float(result.composite_score.growth_score),
                risk_score=float(result.composite_score.risk_score),
                valuation_score=float(result.composite_score.valuation_score),
                ipo_quality_score=float(result.composite_score.ipo_quality_score),
                total_score=float(result.composite_score.total_score),
                growth_details=result.composite_score.growth_details,
                risk_details=result.composite_score.risk_details,
                valuation_details=result.composite_score.valuation_details,
                ipo_quality_details=result.composite_score.ipo_quality_details,
            )

        return FullIPOAnalysisResponse(
            growth_analysis=growth_analysis,
            risk_analysis=risk_analysis,
            valuation_analysis=valuation_analysis,
            composite_score=composite_score,
            errors=result.errors,
            success=result.success,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error processing file: {e!s}") from e
