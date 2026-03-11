import hashlib
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