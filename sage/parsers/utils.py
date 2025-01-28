import re
from loguru import logger

class RegexError(Exception):
    """Custom exception for indicating a regex match failure."""
    pass

def transform_amount(raw_amount: str) -> str:
    """Transform the raw amount into a standardized format"""
    # Remove the comma
    raw_amount = re.sub(",", "", raw_amount)
    # Check for decimals
    if regex_search(r"(.\d{2})", raw_amount):
        transformed_amount = raw_amount
    else:
        transformed_amount = raw_amount + ".00"
    return transformed_amount

def regex_search(pattern: str, raw_text: str) -> str:
    """Helper function to perform regex searches with consistent flags"""
    transformed_text = raw_text.replace("\r", "").replace("\n", " ")
    match = re.search(pattern, transformed_text, flags=re.DOTALL | re.MULTILINE)
    if match:
        if match.group(1):
            return match.group(1)
        else:
            return match.group()
    return None 