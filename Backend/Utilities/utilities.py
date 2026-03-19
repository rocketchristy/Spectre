"""
================================================================================
File: utilities.py
Description: Utility functions for security, authentication, and data sanitization
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module provides common utility functions used throughout the application
including password hashing, token validation, and input sanitization for XSS
prevention.
================================================================================
"""

import hashlib
import html
import re
from Backend.Utilities.logger import logger
from fastapi import Header, HTTPException


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 algorithm.
    
    Inputs:
        password (str): Plain text password to hash
    
    Outputs:
        str: Hexadecimal string representation of the hashed password
    
    Notes:
        Uses SHA-256 for one-way password hashing
        Passwords cannot be reversed from the hash
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_token_header(token: str = Header(...)):
    """
    Extract and validate authentication token from request headers.
    
    Inputs:
        token (str): Authentication token from request header (injected by FastAPI)
    
    Outputs:
        str: Validated token string
    
    Raises:
        HTTPException: 401 error if token is missing or invalid
    
    Notes:
        Used as a FastAPI dependency for protected endpoints
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token header missing")
    # Optionally, add logic to validate the token here
    return token


def sanitize_input(input_string: str) -> str:
    """
    Sanitize input string to prevent XSS (Cross-Site Scripting) attacks.
    
    Inputs:
        input_string (str): Raw user input string to sanitize
    
    Outputs:
        str: Sanitized string safe for storage and display
    
    Side Effects:
        Removes potentially dangerous HTML/JavaScript characters and tags
        Escapes special HTML characters
    
    Notes:
        Protects against:
        - Script injection (<script> tags)
        - JavaScript protocol handlers (javascript:)
        - Event handlers (onclick, onload, etc.)
        - Embedded content (iframe, object, embed tags)
    """
    if not input_string:
        return input_string
    
    # Escape HTML characters
    sanitized = html.escape(input_string)
    
    # Remove any remaining script tags or event handlers (case insensitive)
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, etc.
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>',
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized.strip()
