"""
================================================================================
File: validation.py
Description: Pydantic models for request/response validation and data sanitization
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module defines Pydantic BaseModel classes for validating API request data.
Each model includes field validation, type checking, and XSS sanitization to
ensure data integrity and security.
================================================================================
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from Backend.Utilities.utilities import sanitize_input


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class LoginRequest(BaseModel):
    """
    Request model for user login.
    
    Attributes:
        email (EmailStr): User's email address (automatically validated)
        password (str): User's password (8-100 characters)
    """
    email: EmailStr  # Automatically validates email format
    password: str = Field(..., min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    """
    Request model for new user registration.
    
    Attributes:
        email (EmailStr): User's email address (automatically validated)
        password (str): User's password (8-100 characters)
        first_name (str): User's first name (1-50 characters)
        last_name (str): User's last name (1-50 characters)
    
    Validators:
        name_not_empty: Ensures names are not empty/whitespace and sanitizes input
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v):
        """
        Validate and sanitize name fields.
        
        Inputs:
            v (str): Name field value
        
        Outputs:
            str: Sanitized and trimmed name
        
        Raises:
            ValueError: If name is empty or only whitespace
        """
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        return sanitize_input(v.strip())


class UpdateUserRequest(BaseModel):
    """
    Request model for updating user information.
    
    Attributes:
        email (EmailStr): User's new email address
        password (str): User's new password (8-100 characters)
        fname (str): User's new first name (1-50 characters)
        lname (str): User's new last name (1-50 characters)
    
    Validators:
        name_not_empty: Ensures names are not empty/whitespace and sanitizes input
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    fname: str = Field(..., min_length=1, max_length=50)
    lname: str = Field(..., min_length=1, max_length=50)
    
    @field_validator('fname', 'lname')
    @classmethod
    def name_not_empty(cls, v):
        """
        Validate and sanitize name fields.
        
        Inputs:
            v (str): Name field value
        
        Outputs:
            str: Sanitized and trimmed name
        
        Raises:
            ValueError: If name is empty or only whitespace
        """
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        return sanitize_input(v.strip())


# ============================================================================
# ADDRESS MODEL
# ============================================================================

class AddressRequest(BaseModel):
    """
    Request model for address information (billing/shipping).
    
    Attributes:
        full_name (str): Recipient's full name (1-100 characters)
        line1 (str): Address line 1 (1-100 characters)
        line2 (str): Address line 2 (optional, max 100 characters)
        city (str): City name (1-50 characters)
        region (str): State/province/region (1-50 characters)
        postal_code (str): Postal/ZIP code (1-20 characters)
        country_code (str): ISO country code (2-3 characters)
        phone (str): Phone number (6-20 characters)
    
    Validators:
        sanitize_text_fields: Prevents XSS attacks on text fields
        country_code_uppercase: Converts country code to uppercase
        phone_format: Removes non-numeric characters from phone
        postal_code_not_empty: Validates postal code is not empty
    """
    full_name: str = Field(..., min_length=1, max_length=100)
    line1: str = Field(..., min_length=1, max_length=100)
    line2: str = Field(default="", max_length=100)  # Optional
    city: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=50)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country_code: str = Field(..., min_length=2, max_length=3)
    phone: str = Field(..., min_length=6, max_length=20)
    
    @field_validator('full_name', 'line1', 'line2', 'city', 'region')
    @classmethod
    def sanitize_text_fields(cls, v):
        """
        Sanitize text fields to prevent XSS attacks.
        
        Inputs:
            v (str): Text field value
        
        Outputs:
            str: Sanitized text or original if empty
        """
        return sanitize_input(v) if v else v
    
    @field_validator('country_code')
    @classmethod
    def country_code_uppercase(cls, v):
        """
        Convert country code to uppercase and sanitize.
        
        Inputs:
            v (str): Country code (e.g., 'us', 'ca')
        
        Outputs:
            str: Uppercase, sanitized country code (e.g., 'US', 'CA')
        """
        return sanitize_input(v.upper())
    
    @field_validator('phone')
    @classmethod
    def phone_format(cls, v):
        """
        Remove non-numeric characters from phone number.
        
        Inputs:
            v (str): Phone number with possible formatting
        
        Outputs:
            str: Digits-only phone number
        
        Raises:
            ValueError: If phone has fewer than 6 digits
        """
        digits = re.sub(r'\D', '', v)
        if len(digits) < 6:
            raise ValueError('Phone number must have at least 10 digits')
        return digits
    
    @field_validator('postal_code')
    @classmethod
    def postal_code_not_empty(cls, v):
        """
        Validate postal code is not empty and sanitize.
        
        Inputs:
            v (str): Postal code value
        
        Outputs:
            str: Sanitized and trimmed postal code
        
        Raises:
            ValueError: If postal code is empty or whitespace
        """
        if not v.strip():
            raise ValueError('Postal code cannot be empty')
        return sanitize_input(v.strip())


# ============================================================================
# INVENTORY MODEL
# ============================================================================

class InventoryItemRequest(BaseModel):
    """
    Request model for adding/updating inventory items.
    
    Attributes:
        sku (str): Product SKU (Stock Keeping Unit)
        quantity (int): Number of items in stock
        unitPriceCents (str): Price per unit in cents
        currencyCode (str): Currency code (e.g., 'USD')
    
    Validators:
        sanitize_string_fields: Prevents XSS on SKU and currency code
    """
    sku: str
    quantity: int
    unitPriceCents: str
    currencyCode: str
    
    @field_validator('sku', 'currencyCode')
    @classmethod
    def sanitize_string_fields(cls, v):
        """
        Sanitize string fields to prevent XSS attacks.
        
        Inputs:
            v (str): String field value
        
        Outputs:
            str: Sanitized string or original if empty
        """
        return sanitize_input(v) if v else v


# ============================================================================
# CART MODEL
# ============================================================================

class CartItemRequest(BaseModel):
    """
    Request model for adding items to shopping cart.
    
    Attributes:
        inventory_id (str): ID of the inventory item
        quantity (int): Quantity to add to cart
        unit_price_cents (str): Price per unit in cents
        currency_code (str): Currency code (e.g., 'USD')
    
    Validators:
        sanitize_string_fields: Prevents XSS on string fields
    """
    inventory_id: str
    quantity: int
    unit_price_cents: str
    currency_code: str
    
    @field_validator('inventory_id', 'currency_code')
    @classmethod
    def sanitize_string_fields(cls, v):
        """
        Sanitize string fields to prevent XSS attacks.
        
        Inputs:
            v (str): String field value
        
        Outputs:
            str: Sanitized string or original if empty
        """
        return sanitize_input(v) if v else v