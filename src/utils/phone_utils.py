"""
Phone number utility functions.
Provides functions for handling and normalizing phone numbers.
"""

def normalize_phone_number(mobile: str) -> str:
    """
    Normalizes a phone number into a standard format.
    
    Args:
        mobile (str): The raw phone number input
        
    Returns:
        str: Standardized phone number in +91-XXXXXXXXXX format or empty string if invalid
    """
    # Normalize phone number: remove non-digit characters
    normalized_digits = ''.join(filter(str.isdigit, mobile))
    
    # Handle Indian phone number formats
    if len(normalized_digits) == 10:
        return f"+91-{normalized_digits}"
    elif len(normalized_digits) == 12 and normalized_digits.startswith("91"):
        return f"+91-{normalized_digits[2:]}"
    
    # Invalid format
    return "" 