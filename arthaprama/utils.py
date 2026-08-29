"""
Utility functions for Indian market formatting and number conversions.

This module provides native utilities for handling the Indian numbering system,
including conversions to Lakhs and Crores, and INR currency formatting.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def _to_decimal(value: Any) -> Decimal:
    """
    Safely convert a value to Decimal for precise arithmetic.

    Args:
        value: Any numeric value (int, float, str, Decimal).

    Returns:
        Decimal representation of the input value.
    """
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def format_inr(value: Any, precision: int = 2, include_symbol: bool = True) -> str:
    """
    Format a numeric value as Indian Rupees with proper comma placement.

    This function follows the Indian numbering system where commas are placed
    after every two digits from the right (after the first three digits).

    Args:
        value: The numeric value to format.
        precision: Number of decimal places to show (default: 2).
        include_symbol: Whether to prefix with ₹ symbol (default: True).

    Returns:
        Formatted string in Indian Rupee format.

    Example:
        >>> format_inr(1000000)
        '₹10,00,000.00'
        >>> format_inr(50000.5, precision=0)
        '₹50,000'
    """
    decimal_value = _to_decimal(value).quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)

    # Handle negative values
    is_negative = decimal_value < 0
    abs_value = abs(decimal_value)

    # Split into integer and decimal parts
    str_value = str(abs_value)
    if "." in str_value:
        int_part, dec_part = str_value.split(".")
    else:
        int_part = str_value
        dec_part = ""

    # Apply Indian comma formatting
    if len(int_part) > 3:
        # First three digits from right
        last_three = int_part[-3:]
        remaining = int_part[:-3]

        # Add commas every two digits in the remaining part
        formatted_remaining = []
        while remaining:
            formatted_remaining.append(remaining[-2:])
            remaining = remaining[:-2]

        int_part_formatted = ",".join(reversed(formatted_remaining)) + "," + last_three
    else:
        int_part_formatted = int_part

    # Build final string
    result = int_part_formatted
    if dec_part:
        result += f".{dec_part}"

    if include_symbol:
        result = "₹" + result

    if is_negative:
        result = "-" + result

    return result


def format_inr_lakh(value: Any, precision: int = 2) -> str:
    """
    Format a value in Lakhs with INR symbol.

    1 Lakh = 100,000 (10^5)

    Args:
        value: The numeric value to format.
        precision: Number of decimal places to show (default: 2).

    Returns:
        Formatted string showing value in Lakhs.

    Example:
        >>> format_inr_lakh(1000000)
        '₹10.00 Lakh'
        >>> format_inr_lakh(5000000)
        '₹50.00 Lakh'
    """
    decimal_value = _to_decimal(value)
    lakhs = decimal_value / Decimal("100000")
    formatted_lakhs = lakhs.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)

    if formatted_lakhs == 1:
        return f"₹{formatted_lakhs} Lakh"
    return f"₹{formatted_lakhs} Lakh"


def format_inr_cr(value: Any, precision: int = 2) -> str:
    """
    Format a value in Crores with INR symbol.

    1 Crore = 10,000,000 (10^7) = 100 Lakhs

    Args:
        value: The numeric value to format.
        precision: Number of decimal places to show (default: 2).

    Returns:
        Formatted string showing value in Crores.

    Example:
        >>> format_inr_cr(10000000)
        '₹1.00 Cr'
        >>> format_inr_cr(50000000)
        '₹5.00 Cr'
    """
    decimal_value = _to_decimal(value)
    crores = decimal_value / Decimal("10000000")
    formatted_crores = crores.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)
    return f"₹{formatted_crores} Cr"


def to_lakhs(value: Any, precision: int = 4) -> Decimal:
    """
    Convert a value to Lakhs (numeric).

    Args:
        value: The numeric value to convert.
        precision: Number of decimal places for the result.

    Returns:
        Value expressed in Lakhs as Decimal.

    Example:
        >>> to_lakhs(1000000)
        Decimal('10.0000')
    """
    decimal_value = _to_decimal(value)
    return (decimal_value / Decimal("100000")).quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def to_crores(value: Any, precision: int = 4) -> Decimal:
    """
    Convert a value to Crores (numeric).

    Args:
        value: The numeric value to convert.
        precision: Number of decimal places for the result.

    Returns:
        Value expressed in Crores as Decimal.

    Example:
        >>> to_crores(10000000)
        Decimal('1.0000')
    """
    decimal_value = _to_decimal(value)
    return (decimal_value / Decimal("10000000")).quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)


def format_percentage(value: Any, precision: int = 2, include_sign: bool = False) -> str:
    """
    Format a numeric value as a percentage.

    Args:
        value: The numeric value to format (already as percentage, e.g., 15.5 for 15.5%).
        precision: Number of decimal places to show (default: 2).
        include_sign: Whether to include + sign for positive values (default: False).

    Returns:
        Formatted percentage string.

    Example:
        >>> format_percentage(15.5)
        '15.50%'
        >>> format_percentage(-5.25, include_sign=True)
        '-5.25%'
        >>> format_percentage(10.0, include_sign=True)
        '+10.00%'
    """
    decimal_value = _to_decimal(value).quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)

    result = str(decimal_value)
    # Ensure precision is maintained even for whole numbers
    if "." not in result:
        result += "." + "0" * precision
    else:
        current_precision = len(result.split(".")[1])
        if current_precision < precision:
            result += "0" * (precision - current_precision)

    if include_sign and decimal_value > 0:
        result = "+" + result

    return result + "%"


def smart_format_inr(value: Any, precision: int = 2) -> str:
    """
    Intelligently format a value using the most appropriate unit.

    Automatically selects between raw INR, Lakhs, or Crores based on magnitude.

    Args:
        value: The numeric value to format.
        precision: Number of decimal places to show (default: 2).

    Returns:
        Formatted string with appropriate unit suffix.

    Example:
        >>> smart_format_inr(50000)
        '₹50,000.00'
        >>> smart_format_inr(5000000)
        '₹50.00 Lakh'
        >>> smart_format_inr(50000000)
        '₹5.00 Cr'
    """
    decimal_value = _to_decimal(value)
    abs_value = abs(decimal_value)

    if abs_value >= Decimal("10000000"):  # 1 Crore or more
        return format_inr_cr(decimal_value, precision)
    elif abs_value >= Decimal("100000"):  # 1 Lakh or more
        return format_inr_lakh(decimal_value, precision)
    else:
        return format_inr(decimal_value, precision)


def parse_indian_number(value: str) -> Decimal:
    """
    Parse an Indian-formatted number string to Decimal.

    Handles formats like "₹10,00,000", "5.5 Cr", "10 Lakh", etc.

    Args:
        value: String representation of a number.

    Returns:
        Parsed Decimal value.

    Raises:
        ValueError: If the string cannot be parsed.

    Example:
        >>> parse_indian_number("₹10,00,000")
        Decimal('1000000')
        >>> parse_indian_number("5.5 Cr")
        Decimal('55000000')
        >>> parse_indian_number("10 Lakh")
        Decimal('1000000')
    """
    # Remove common symbols and whitespace
    cleaned = value.strip().replace("₹", "").replace(",", "").strip()

    # Check for unit suffixes
    upper_cleaned = cleaned.upper()

    if "CR" in upper_cleaned or "CRORE" in upper_cleaned:
        multiplier = Decimal("10000000")
        num_str = cleaned.upper().replace("CR", "").replace("CRORE", "").strip()
    elif "LAKH" in upper_cleaned:
        multiplier = Decimal("100000")
        num_str = cleaned.upper().replace("LAKH", "").strip()
    else:
        multiplier = Decimal("1")
        num_str = cleaned

    # Remove any remaining non-numeric characters except decimal point and minus
    num_str = "".join(c for c in num_str if c.isdigit() or c in ".-")

    if not num_str or num_str == "-":
        raise ValueError(f"Cannot parse '{value}' as a number")

    return Decimal(num_str) * multiplier
