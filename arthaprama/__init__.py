"""
Arthaprama - A production-ready technical analytical engine for Indian IPOs.

This library provides mathematical calculations for Growth, Risk, Valuation,
and composite scores specifically designed for Initial Public Offerings (IPOs)
in the Indian market.

Philosophical Root: "Prama" means accurate, valid, and foundational knowledge.
"""

__version__ = "0.1.0"
__author__ = "Arthaprama Contributors"

from arthaprama.config import InvestorProfile, ProfileStrategy, get_profile
from arthaprama.ipo import growth, risk, scoring, valuation
from arthaprama.utils import format_inr, format_inr_cr, format_inr_lakh

__all__ = [
    # Config
    "InvestorProfile",
    "ProfileStrategy",
    # Utils
    "format_inr",
    "format_inr_cr",
    "format_inr_lakh",
    "get_profile",
    # IPO Modules
    "growth",
    "risk",
    "scoring",
    "valuation",
]
