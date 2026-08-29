"""
Global Configuration & User Preferences Engine for Arthaprama.

This module implements extensible preference scaling logic and asset weights
for different investor strategies. It follows the open-closed design pattern
to allow smooth insertion of future asset types (stocks, mutual funds, etc.)
without modifying core infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any


class ProfileStrategy(Enum):
    """
    Enumeration of supported investor profile strategies.

    Attributes:
        BALANCED: Default strategy with equal weight distribution.
        CONSERVATIVE: Safety-first approach with higher risk aversion.
        AGGRESSIVE_GROWTH: High risk/high reward orientation.
        DEEP_VALUE: Bargain hunting with focus on undervalued assets.
    """

    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    AGGRESSIVE_GROWTH = "aggressive_growth"
    DEEP_VALUE = "deep_value"


@dataclass
class WeightConfig:
    """
    Configuration class for holding weight allocations across scoring pillars.

    Attributes:
        growth: Weight allocated to growth metrics (out of 30).
        risk: Weight allocated to risk metrics (out of 30).
        valuation: Weight allocated to valuation metrics (out of 30).
        ipo_quality: Weight allocated to IPO/management quality (out of 10).
    """

    growth: Decimal = Decimal(30)
    risk: Decimal = Decimal(30)
    valuation: Decimal = Decimal(30)
    ipo_quality: Decimal = Decimal(10)

    def __post_init__(self) -> None:
        """Validate that weights sum to 100."""
        total = self.growth + self.risk + self.valuation + self.ipo_quality
        if total != Decimal(100):
            raise ValueError(
                f"Weights must sum to 100, got {total}. "
                f"Growth={self.growth}, Risk={self.risk}, "
                f"Valuation={self.valuation}, IPO Quality={self.ipo_quality}"
            )

    def to_dict(self) -> dict[str, Decimal]:
        """Convert weights to dictionary format."""
        return {
            "growth": self.growth,
            "risk": self.risk,
            "valuation": self.valuation,
            "ipo_quality": self.ipo_quality,
        }


@dataclass
class ThresholdConfig:
    """
    Configuration class for threshold limits used in scoring calculations.

    Attributes:
        max_debt_to_equity: Maximum acceptable debt-to-equity ratio.
        min_interest_coverage: Minimum acceptable interest coverage ratio.
        min_current_ratio: Minimum acceptable current ratio.
        min_roe: Minimum acceptable Return on Equity percentage.
        min_roce: Minimum acceptable Return on Capital Employed percentage.
        max_pe_ratio: Maximum acceptable P/E ratio for valuation.
        max_peg_ratio: Maximum acceptable PEG ratio.
        min_ebitda_margin: Minimum acceptable EBITDA margin percentage.
        min_pat_margin: Minimum acceptable PAT margin percentage.
        max_customer_concentration: Maximum revenue from single customer (%).
        max_promoter_pledge: Maximum promoter pledge ratio (%).
    """

    max_debt_to_equity: Decimal = Decimal("2.0")
    min_interest_coverage: Decimal = Decimal("2.0")
    min_current_ratio: Decimal = Decimal("1.5")
    min_roe: Decimal = Decimal(15)
    min_roce: Decimal = Decimal(15)
    max_pe_ratio: Decimal = Decimal(40)
    max_peg_ratio: Decimal = Decimal("2.0")
    min_ebitda_margin: Decimal = Decimal(10)
    min_pat_margin: Decimal = Decimal(5)
    max_customer_concentration: Decimal = Decimal(50)
    max_promoter_pledge: Decimal = Decimal(20)

    def to_dict(self) -> dict[str, Decimal]:
        """Convert thresholds to dictionary format."""
        return {
            "max_debt_to_equity": self.max_debt_to_equity,
            "min_interest_coverage": self.min_interest_coverage,
            "min_current_ratio": self.min_current_ratio,
            "min_roe": self.min_roe,
            "min_roce": self.min_roce,
            "max_pe_ratio": self.max_pe_ratio,
            "max_peg_ratio": self.max_peg_ratio,
            "min_ebitda_margin": self.min_ebitda_margin,
            "min_pat_margin": self.min_pat_margin,
            "max_customer_concentration": self.max_customer_concentration,
            "max_promoter_pledge": self.max_promoter_pledge,
        }


@dataclass
class InvestorProfile:
    """
    Unified investor profile configuration combining weights and thresholds.

    This class serves as the primary configuration object passed to scoring
    engines. It supports dynamic customization per user request via backend
    payloads while maintaining sensible defaults for each strategy type.

    Attributes:
        strategy: The investor strategy enum value.
        weights: WeightConfig instance defining pillar allocations.
        thresholds: ThresholdConfig instance defining evaluation boundaries.
        sector_overrides: Optional dictionary for sector-specific baseline overrides.
    """

    strategy: ProfileStrategy = ProfileStrategy.BALANCED
    weights: WeightConfig = field(default_factory=WeightConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    sector_overrides: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_balanced(cls) -> InvestorProfile:
        """Create a balanced investor profile with default weights."""
        return cls(
            strategy=ProfileStrategy.BALANCED,
            weights=WeightConfig(
                growth=Decimal(30),
                risk=Decimal(30),
                valuation=Decimal(30),
                ipo_quality=Decimal(10),
            ),
            thresholds=ThresholdConfig(),
        )

    @classmethod
    def create_conservative(cls) -> InvestorProfile:
        """
        Create a conservative investor profile prioritizing safety.

        Conservative profiles emphasize risk mitigation over growth potential.
        """
        return cls(
            strategy=ProfileStrategy.CONSERVATIVE,
            weights=WeightConfig(
                growth=Decimal(20),
                risk=Decimal(40),
                valuation=Decimal(30),
                ipo_quality=Decimal(10),
            ),
            thresholds=ThresholdConfig(
                max_debt_to_equity=Decimal("1.0"),
                min_interest_coverage=Decimal("3.0"),
                min_current_ratio=Decimal("2.0"),
                min_roe=Decimal(12),
                min_roce=Decimal(12),
                max_pe_ratio=Decimal(25),
                max_peg_ratio=Decimal("1.5"),
                min_ebitda_margin=Decimal(15),
                min_pat_margin=Decimal(8),
                max_customer_concentration=Decimal(30),
                max_promoter_pledge=Decimal(10),
            ),
        )

    @classmethod
    def create_aggressive_growth(cls) -> InvestorProfile:
        """
        Create an aggressive growth investor profile.

        Aggressive growth profiles prioritize revenue and profit expansion
        over risk considerations and valuation comfort.
        """
        return cls(
            strategy=ProfileStrategy.AGGRESSIVE_GROWTH,
            weights=WeightConfig(
                growth=Decimal(40),
                risk=Decimal(20),
                valuation=Decimal(30),
                ipo_quality=Decimal(10),
            ),
            thresholds=ThresholdConfig(
                max_debt_to_equity=Decimal("3.0"),
                min_interest_coverage=Decimal("1.5"),
                min_current_ratio=Decimal("1.0"),
                min_roe=Decimal(20),
                min_roce=Decimal(20),
                max_pe_ratio=Decimal(60),
                max_peg_ratio=Decimal("3.0"),
                min_ebitda_margin=Decimal(8),
                min_pat_margin=Decimal(3),
                max_customer_concentration=Decimal(60),
                max_promoter_pledge=Decimal(30),
            ),
        )

    @classmethod
    def create_deep_value(cls) -> InvestorProfile:
        """
        Create a deep value investor profile for bargain hunters.

        Deep value profiles focus heavily on valuation metrics, seeking
        undervalued opportunities even at the cost of lower growth.
        """
        return cls(
            strategy=ProfileStrategy.DEEP_VALUE,
            weights=WeightConfig(
                growth=Decimal(20),
                risk=Decimal(25),
                valuation=Decimal(45),
                ipo_quality=Decimal(10),
            ),
            thresholds=ThresholdConfig(
                max_debt_to_equity=Decimal("1.5"),
                min_interest_coverage=Decimal("2.5"),
                min_current_ratio=Decimal("1.5"),
                min_roe=Decimal(15),
                min_roce=Decimal(15),
                max_pe_ratio=Decimal(20),
                max_peg_ratio=Decimal("1.0"),
                min_ebitda_margin=Decimal(12),
                min_pat_margin=Decimal(8),
                max_customer_concentration=Decimal(40),
                max_promoter_pledge=Decimal(15),
            ),
        )

    def get_weights_for_asset(self, asset_type: str = "ipo") -> dict[str, Decimal]:
        """
        Get weight configuration for a specific asset type.

        This method enables the open-closed design pattern by allowing
        future asset types (stock, mutual_fund, derivative) to be added
        without modifying core infrastructure.

        Args:
            asset_type: The type of asset ("ipo" currently supported).

        Returns:
            Dictionary mapping pillar names to their weight values.
        """
        # Currently only IPO weights are supported, but architecture allows
        # seamless extension to other asset types in the future
        if asset_type == "ipo":
            return self.weights.to_dict()
        # Future extension point for other asset types
        # elif asset_type == "stock":
        #     return self._get_stock_weights()
        # elif asset_type == "mutual_fund":
        #     return self._get_mutual_fund_weights()
        return self.weights.to_dict()

    def get_thresholds_for_asset(self, asset_type: str = "ipo") -> dict[str, Decimal]:
        """
        Get threshold configuration for a specific asset type.

        Args:
            asset_type: The type of asset ("ipo" currently supported).

        Returns:
            Dictionary mapping threshold names to their values.
        """
        if asset_type == "ipo":
            base_thresholds = self.thresholds.to_dict()
            # Apply sector overrides if present
            if asset_type in self.sector_overrides:
                base_thresholds.update(self.sector_overrides[asset_type])
            return base_thresholds
        return self.thresholds.to_dict()

    def to_dict(self) -> dict[str, Any]:
        """Convert entire profile to dictionary format."""
        return {
            "strategy": self.strategy.value,
            "weights": self.weights.to_dict(),
            "thresholds": self.thresholds.to_dict(),
            "sector_overrides": self.sector_overrides,
        }


# Pre-configured profile instances for quick access
_PROFILES: dict[ProfileStrategy, InvestorProfile] = {
    ProfileStrategy.BALANCED: InvestorProfile.create_balanced(),
    ProfileStrategy.CONSERVATIVE: InvestorProfile.create_conservative(),
    ProfileStrategy.AGGRESSIVE_GROWTH: InvestorProfile.create_aggressive_growth(),
    ProfileStrategy.DEEP_VALUE: InvestorProfile.create_deep_value(),
}


def get_profile(strategy: str | ProfileStrategy = "balanced") -> InvestorProfile:
    """
    Retrieve a pre-configured investor profile by strategy name or enum.

    This function provides quick access to standard profile configurations
    while allowing users to customize thresholds and weights as needed.

    Args:
        strategy: Either a string name ("balanced", "conservative", etc.)
                  or a ProfileStrategy enum value.

    Returns:
        A copy of the pre-configured InvestorProfile instance.

    Raises:
        ValueError: If an unknown strategy is provided.

    Example:
        >>> profile = get_profile("conservative")
        >>> print(profile.weights.growth)
        Decimal('20')
    """
    if isinstance(strategy, str):
        try:
            strategy_enum = ProfileStrategy(strategy.lower())
        except ValueError as e:
            valid_strategies = [s.value for s in ProfileStrategy]
            raise ValueError(f"Unknown strategy '{strategy}'. Valid options: {valid_strategies}") from e
    else:
        strategy_enum = strategy

    return _PROFILES.get(strategy_enum, InvestorProfile.create_balanced())


def create_custom_profile(
    strategy: ProfileStrategy = ProfileStrategy.BALANCED,
    weights: dict[str, Decimal] | None = None,
    thresholds: dict[str, Decimal] | None = None,
    sector_overrides: dict[str, Any] | None = None,
) -> InvestorProfile:
    """
    Create a fully customized investor profile.

    This factory function allows complete control over all profile parameters
    for advanced users requiring non-standard configurations.

    Args:
        strategy: Base strategy enum to inherit defaults from.
        weights: Optional dictionary overriding default weights.
        thresholds: Optional dictionary overriding default thresholds.
        sector_overrides: Optional sector-specific baseline overrides.

    Returns:
        A new InvestorProfile instance with custom settings.

    Example:
        >>> profile = create_custom_profile(
        ...     strategy=ProfileStrategy.BALANCED,
        ...     weights={"growth": Decimal("35"), "risk": Decimal("25"},
        ...              "valuation": Decimal("30"), "ipo_quality": Decimal("10")},
        ...     thresholds={"max_pe_ratio": Decimal("30")}
        ... )
    """
    # Start with base profile
    base_profile = get_profile(strategy)

    # Override weights if provided
    if weights:
        weight_config = WeightConfig(
            growth=weights.get("growth", base_profile.weights.growth),
            risk=weights.get("risk", base_profile.weights.risk),
            valuation=weights.get("valuation", base_profile.weights.valuation),
            ipo_quality=weights.get("ipo_quality", base_profile.weights.ipo_quality),
        )
    else:
        weight_config = base_profile.weights

    # Override thresholds if provided
    if thresholds:
        threshold_config = ThresholdConfig(
            max_debt_to_equity=thresholds.get("max_debt_to_equity", base_profile.thresholds.max_debt_to_equity),
            min_interest_coverage=thresholds.get("min_interest_coverage", base_profile.thresholds.min_interest_coverage),
            min_current_ratio=thresholds.get("min_current_ratio", base_profile.thresholds.min_current_ratio),
            min_roe=thresholds.get("min_roe", base_profile.thresholds.min_roe),
            min_roce=thresholds.get("min_roce", base_profile.thresholds.min_roce),
            max_pe_ratio=thresholds.get("max_pe_ratio", base_profile.thresholds.max_pe_ratio),
            max_peg_ratio=thresholds.get("max_peg_ratio", base_profile.thresholds.max_peg_ratio),
            min_ebitda_margin=thresholds.get("min_ebitda_margin", base_profile.thresholds.min_ebitda_margin),
            min_pat_margin=thresholds.get("min_pat_margin", base_profile.thresholds.min_pat_margin),
            max_customer_concentration=thresholds.get(
                "max_customer_concentration",
                base_profile.thresholds.max_customer_concentration,
            ),
            max_promoter_pledge=thresholds.get("max_promoter_pledge", base_profile.thresholds.max_promoter_pledge),
        )
    else:
        threshold_config = base_profile.thresholds

    return InvestorProfile(
        strategy=strategy,
        weights=weight_config,
        thresholds=threshold_config,
        sector_overrides=sector_overrides or {},
    )
