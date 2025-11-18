"""
Shared utilities for OTP generation and validation.
This module provides consistent OTP handling across all apps.
"""

import secrets
import string
from django.utils import timezone
from datetime import timedelta


def generate_otp_code(length=6):
    """
    Generate a cryptographically secure OTP code.
    
    Args:
        length (int): Length of the OTP code (default: 6)
        
    Returns:
        str: Generated OTP code
    """
    if length < 4 or length > 10:
        raise ValueError("OTP length must be between 4 and 10 characters")
    
    # Generate cryptographically secure random digits
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_otp_code_4_digits():
    """
    Generate a 4-digit OTP code for WhatsApp/SMS.
    
    Returns:
        str: 4-digit OTP code
    """
    return generate_otp_code(4)


def generate_otp_code_6_digits():
    """
    Generate a 6-digit OTP code for email verification.
    
    Returns:
        str: 6-digit OTP code
    """
    return generate_otp_code(6)


def calculate_otp_expiry(minutes=10):
    """
    Calculate OTP expiry time.
    
    Args:
        minutes (int): Minutes until expiry (default: 10)
        
    Returns:
        datetime: Expiry time
    """
    return timezone.now() + timedelta(minutes=minutes)


def is_otp_expired(created_at, expiry_minutes=10):
    """
    Check if OTP is expired.
    
    Args:
        created_at (datetime): When OTP was created
        expiry_minutes (int): Expiry time in minutes (default: 10)
        
    Returns:
        bool: True if expired, False otherwise
    """
    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    return timezone.now() > expiry_time


def validate_otp_format(otp_code, expected_length=6):
    """
    Validate OTP code format.
    
    Args:
        otp_code (str): OTP code to validate
        expected_length (int): Expected length of OTP
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not otp_code:
        return False
    
    # Check if it's all digits
    if not otp_code.isdigit():
        return False
    
    # Check length
    if len(otp_code) != expected_length:
        return False
    
    return True


def format_otp_for_display(otp_code, group_size=3):
    """
    Format OTP code for display purposes.
    
    Args:
        otp_code (str): OTP code to format
        group_size (int): Group size for formatting (default: 3)
        
    Returns:
        str: Formatted OTP code (e.g., "123 456")
    """
    if not otp_code:
        return otp_code
    
    # Group digits with spaces
    formatted = ' '.join(otp_code[i:i+group_size] for i in range(0, len(otp_code), group_size))
    return formatted
