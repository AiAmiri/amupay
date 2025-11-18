"""
Shared utilities for phone number validation and formatting.
This module provides consistent phone number handling across all apps.
"""

import re
from django.core.exceptions import ValidationError


def validate_and_format_phone_number(value):
    """
    Validate and format phone number for Afghanistan and international numbers.
    
    Args:
        value (str): Phone number to validate and format
        
    Returns:
        str: Formatted phone number in E.164 format
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    if not value:
        raise ValidationError("Phone number is required")
    
    # Remove any spaces, dashes, parentheses, or other formatting
    cleaned_number = re.sub(r'[\s\-\(\)]', '', str(value).strip())
    
    # Check if it's Afghan local format (starts with 0 and 10 digits total)
    if re.match(r'^0[7][0-9]{8}$', cleaned_number):
        # Convert to E.164 format for Afghanistan (+93)
        return '+93' + cleaned_number[1:]
    
    # Check if it's already in Afghan international format
    if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
        return cleaned_number
    
    # Check if it's a valid international number (E.164 format) - but not Afghan format
    if re.match(r'^\+[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
        return cleaned_number
        
    # Check if it's a valid number without + (add +) - but not Afghan format
    if re.match(r'^[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^93[7][0-9]{8}$', cleaned_number):
        return '+' + cleaned_number
    
    raise ValidationError(
        "Phone number must be in valid format. Afghanistan: 0701234567 or +93701234567. International: +1234567890"
    )


def validate_phone_number_format(value):
    """
    Validate phone number format without formatting (for display purposes).
    
    Args:
        value (str): Phone number to validate
        
    Returns:
        str: Validated phone number (unchanged)
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    if not value:
        raise ValidationError("Phone number is required")
    
    # Remove any spaces, dashes, parentheses, or other formatting
    cleaned_number = re.sub(r'[\s\-\(\)]', '', str(value).strip())
    
    # Check if it's Afghan local format (starts with 0 and 10 digits total)
    if re.match(r'^0[7][0-9]{8}$', cleaned_number):
        return value  # Return original value for display
    
    # Check if it's already in Afghan international format
    if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
        return value
    
    # Check if it's a valid international number (E.164 format)
    if re.match(r'^\+[1-9]\d{6,14}$', cleaned_number):
        return value
        
    # Check if it's a valid number without + (add +)
    if re.match(r'^[1-9]\d{6,14}$', cleaned_number):
        return value
    
    raise ValidationError(
        "Phone number must be in valid format. Afghanistan: 0701234567 or +93701234567. International: +1234567890"
    )


def is_afghan_phone_number(value):
    """
    Check if a phone number is an Afghan number.
    
    Args:
        value (str): Phone number to check
        
    Returns:
        bool: True if Afghan number, False otherwise
    """
    if not value:
        return False
    
    cleaned_number = re.sub(r'[\s\-\(\)]', '', str(value).strip())
    
    # Check Afghan local format
    if re.match(r'^0[7][0-9]{8}$', cleaned_number):
        return True
    
    # Check Afghan international format
    if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
        return True
    
    return False


def format_phone_for_display(value):
    """
    Format phone number for display purposes.
    
    Args:
        value (str): Phone number to format
        
    Returns:
        str: Formatted phone number for display
    """
    if not value:
        return value
    
    cleaned_number = re.sub(r'[\s\-\(\)]', '', str(value).strip())
    
    # Format Afghan numbers nicely
    if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
        # Format as +93 70 123 4567
        return f"+93 {cleaned_number[3:5]} {cleaned_number[5:8]} {cleaned_number[8:]}"
    
    # Format other international numbers
    if re.match(r'^\+[1-9]\d{6,14}$', cleaned_number):
        # Basic formatting for other countries
        return cleaned_number
    
    return value
