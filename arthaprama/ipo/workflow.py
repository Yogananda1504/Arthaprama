"""
IPO Workflow Engine for Arthaprama.

This module implements a unified, workflow-based IPO analysis pipeline that
orchestrates existing isolated domain calculations (growth, risk, valuation, scoring)
into an atomic end-to-end execution flow.

The workflow engine accepts a consolidated IPO data structure, sequentially executes
the underlying modules, passes intermediate outputs to the scoring engine, and
returns a single unified report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from arthaprama.ipo.growth import calculate_all_growth_metrics, GrowthCalculationError
from arthaprama.ipo.risk import calculate_all_risk_metrics, RiskCalculationError
from arthaprama.ipo.valuation import (
    calculate_all_valuation_metrics,
    ValuationCalculationError,
)
from arthaprama.ipo.scoring import generate_ipo_score, ScoreBreakdown


@dataclass
class GrowthAnalysisResult:
    """Result of growth metrics calculation."""

    metrics: dict[str, Decimal] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with float values."""
        return {
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "errors": self.errors,
            "success": self.success,
        }


@dataclass
class RiskAnalysisResult:
    """Result of risk metrics calculation."""

    metrics: dict[str, Decimal] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with float values."""
        return {
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "errors": self.errors,
            "success": self.success,
        }


@dataclass
class ValuationAnalysisResult:
    """Result of valuation metrics calculation."""

    metrics: dict[str, Decimal] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with float values."""
        return {
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "errors": self.errors,
            "success": self.success,
        }


@dataclass
class FullIPOAnalysisResult:
    """Complete IPO analysis result from the workflow engine."""

    growth_analysis: GrowthAnalysisResult = field(default_factory=GrowthAnalysisResult)
    risk_analysis: RiskAnalysisResult = field(default_factory=RiskAnalysisResult)
    valuation_analysis: ValuationAnalysisResult = field(
        default_factory=ValuationAnalysisResult
    )
    composite_score: ScoreBreakdown | None = None
    errors: list[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "growth_analysis": self.growth_analysis.to_dict(),
            "risk_analysis": self.risk_analysis.to_dict(),
            "valuation_analysis": self.valuation_analysis.to_dict(),
            "composite_score": (
                self.composite_score.to_dict() if self.composite_score else None
            ),
            "errors": self.errors,
            "success": self.success,
        }


class IPOWorkflowError(Exception):
    """Exception raised when workflow execution fails."""

    pass


def run_full_ipo_analysis(
    growth_data: dict[str, Any],
    risk_data: dict[str, Any],
    valuation_data: dict[str, Any],
    ipo_data: dict[str, Any],
    profile: str | None = None,
    peer_data: dict[str, Any] | None = None,
    precision: int = 4,
) -> FullIPOAnalysisResult:
    """
    Execute a complete IPO analysis workflow.

    This function orchestrates the sequential execution of growth, risk, and
    valuation calculations, then feeds the results into the scoring engine
    to produce a comprehensive IPO evaluation.

    Args:
        growth_data: Financial data for growth calculations including:
            - revenue_current, revenue_previous, revenue_3yrs_ago
            - pat_current, pat_previous, pat_3yrs_ago
            - ebitda_current, ebitda_previous
            - eps_current, eps_previous
            - ebit, cfo_current, cfo_previous
            - avg_shareholders_equity, capital_employed
        risk_data: Financial data for risk calculations including:
            - total_debt, shareholders_equity, cash_equivalents
            - ebitda, ebit, interest_expense
            - current_assets, current_liabilities, inventory
            - cfo, pat, capex
            - largest_customer_rev, total_rev
            - pledged_shares, total_promoter_shares
            - contingent_liabilities, net_worth
        valuation_data: Financial data for valuation calculations including:
            - market_cap, pat, book_value, revenue
            - ebitda, eps, ipo_price
            - total_debt, cash_equivalents
            - free_cash_flow
            - new_shares, post_ipo_shares, post_ipo_diluted_shares, post_ipo_pat
            - expected_eps_growth_pct
        ipo_data: IPO-specific data including:
            - ipo_dilution, promoter_holding_post_ipo, promoter_pledge_ratio
        profile: Optional investor profile (balanced, conservative, aggressive_growth, deep_value).
                 Defaults to "balanced" if None.
        peer_data: Optional peer comparison data for relative valuation.
        precision: Number of decimal places for calculations (default: 4).

    Returns:
        FullIPOAnalysisResult containing all analysis results and composite score.

    Example:
        >>> result = run_full_ipo_analysis(
        ...     growth_data={
        ...         "revenue_current": 1200,
        ...         "revenue_previous": 1000,
        ...         "pat_current": 150,
        ...         "pat_previous": 100,
        ...         "ebitda_current": 200,
        ...         "ebitda_previous": 180,
        ...         "eps_current": 25,
        ...         "eps_previous": 20,
        ...     },
        ...     risk_data={
        ...         "total_debt": 200,
        ...         "shareholders_equity": 800,
        ...         "cash_equivalents": 100,
        ...     },
        ...     valuation_data={
        ...         "market_cap": 2000,
        ...         "pat": 150,
        ...         "book_value": 800,
        ...         "revenue": 1200,
        ...     },
        ...     ipo_data={"promoter_holding_post_ipo": 60},
        ...     profile="balanced"
        ... )
        >>> print(result.composite_score.total_score)
        72.5
    """
    result = FullIPOAnalysisResult()

    # Step 1: Calculate Growth Metrics
    try:
        growth_metrics = calculate_all_growth_metrics(growth_data, precision)
        result.growth_analysis = GrowthAnalysisResult(
            metrics=growth_metrics,
            errors=[],
            success=True,
        )
    except GrowthCalculationError as e:
        result.growth_analysis = GrowthAnalysisResult(
            metrics={},
            errors=[str(e)],
            success=False,
        )
        result.errors.append(f"Growth calculation error: {str(e)}")
    except Exception as e:
        result.growth_analysis = GrowthAnalysisResult(
            metrics={},
            errors=[f"Unexpected error: {str(e)}"],
            success=False,
        )
        result.errors.append(f"Growth calculation failed: {str(e)}")

    # Step 2: Calculate Risk Metrics
    try:
        risk_metrics = calculate_all_risk_metrics(risk_data, precision)
        result.risk_analysis = RiskAnalysisResult(
            metrics=risk_metrics,
            errors=[],
            success=True,
        )
    except RiskCalculationError as e:
        result.risk_analysis = RiskAnalysisResult(
            metrics={},
            errors=[str(e)],
            success=False,
        )
        result.errors.append(f"Risk calculation error: {str(e)}")
    except Exception as e:
        result.risk_analysis = RiskAnalysisResult(
            metrics={},
            errors=[f"Unexpected error: {str(e)}"],
            success=False,
        )
        result.errors.append(f"Risk calculation failed: {str(e)}")

    # Step 3: Calculate Valuation Metrics
    try:
        valuation_metrics = calculate_all_valuation_metrics(
            valuation_data, peer_data, precision
        )
        result.valuation_analysis = ValuationAnalysisResult(
            metrics=valuation_metrics,
            errors=[],
            success=True,
        )
    except ValuationCalculationError as e:
        result.valuation_analysis = ValuationAnalysisResult(
            metrics={},
            errors=[str(e)],
            success=False,
        )
        result.errors.append(f"Valuation calculation error: {str(e)}")
    except Exception as e:
        result.valuation_analysis = ValuationAnalysisResult(
            metrics={},
            errors=[f"Unexpected error: {str(e)}"],
            success=False,
        )
        result.errors.append(f"Valuation calculation failed: {str(e)}")

    # Step 4: Generate Composite Score (only if all analyses succeeded or have partial data)
    try:
        # Use the scoring engine with raw data (it will recalculate internally)
        # This ensures consistency with the existing scoring logic
        composite = generate_ipo_score(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile=profile,
            peer_data=peer_data,
        )
        result.composite_score = composite
    except Exception as e:
        result.errors.append(f"Scoring failed: {str(e)}")
        result.composite_score = None

    # Determine overall success
    result.success = (
        result.growth_analysis.success
        and result.risk_analysis.success
        and result.valuation_analysis.success
    )

    return result


class IPOWorkflowEngine:
    """
    IPO Workflow Engine class for orchestrating complete IPO analysis.

    This class provides a stateful interface for executing IPO analysis workflows,
    allowing for configuration, validation, and execution control.

    Attributes:
        precision: Number of decimal places for calculations.
        strict_mode: If True, raises exceptions on errors; if False, returns partial results.
    """

    def __init__(
        self, precision: int = 4, strict_mode: bool = False
    ) -> None:
        """
        Initialize the IPO Workflow Engine.

        Args:
            precision: Number of decimal places for calculations (default: 4).
            strict_mode: If True, raises IPOWorkflowError on failures (default: False).
        """
        self.precision = precision
        self.strict_mode = strict_mode

    def execute(
        self,
        growth_data: dict[str, Any],
        risk_data: dict[str, Any],
        valuation_data: dict[str, Any],
        ipo_data: dict[str, Any],
        profile: str | None = None,
        peer_data: dict[str, Any] | None = None,
    ) -> FullIPOAnalysisResult:
        """
        Execute the full IPO analysis workflow.

        Args:
            growth_data: Financial data for growth calculations.
            risk_data: Financial data for risk calculations.
            valuation_data: Financial data for valuation calculations.
            ipo_data: IPO-specific data.
            profile: Optional investor profile strategy.
            peer_data: Optional peer comparison data.

        Returns:
            FullIPOAnalysisResult containing all analysis results.

        Raises:
            IPOWorkflowError: If strict_mode is True and any step fails.
        """
        result = run_full_ipo_analysis(
            growth_data=growth_data,
            risk_data=risk_data,
            valuation_data=valuation_data,
            ipo_data=ipo_data,
            profile=profile,
            peer_data=peer_data,
            precision=self.precision,
        )

        if self.strict_mode and not result.success:
            raise IPOWorkflowError(
                f"Workflow execution failed with errors: {', '.join(result.errors)}"
            )

        return result

    def validate_inputs(
        self,
        growth_data: dict[str, Any],
        risk_data: dict[str, Any],
        valuation_data: dict[str, Any],
        ipo_data: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """
        Validate input data before execution.

        Args:
            growth_data: Growth calculation inputs.
            risk_data: Risk calculation inputs.
            valuation_data: Valuation calculation inputs.
            ipo_data: IPO-specific inputs.

        Returns:
            Tuple of (is_valid, list_of_error_messages).
        """
        errors: list[str] = []

        # Validate required growth fields
        required_growth = ["revenue_current", "revenue_previous", "pat_current", "pat_previous"]
        for field_name in required_growth:
            if field_name not in growth_data:
                errors.append(f"Missing required growth field: {field_name}")

        # Validate required risk fields
        required_risk = ["total_debt", "shareholders_equity"]
        for field_name in required_risk:
            if field_name not in risk_data:
                errors.append(f"Missing required risk field: {field_name}")

        # Validate required valuation fields
        required_valuation = ["market_cap"]
        for field_name in required_valuation:
            if field_name not in valuation_data:
                errors.append(f"Missing required valuation field: {field_name}")

        return len(errors) == 0, errors
