import hashlib
import html
import re
from Backend.Utilities.logger import logger
from fastapi import Header, HTTPException

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_token_header(token: str = Header(...)):
    if not token:
        raise HTTPException(status_code=401, detail="Token header missing")
    # Optionally, add logic to validate the token here
    return token

def sanitize_input(input_string: str) -> str:
    """
    Sanitize input string to prevent XSS attacks.
    Removes potentially dangerous HTML/JavaScript characters and tags.
    
    Args:
        input_string: The string to sanitize
        
    Returns:
        Sanitized string safe for storage and display
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
