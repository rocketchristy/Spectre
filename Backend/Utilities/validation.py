from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from Backend.Utilities.utilities import sanitize_input

#---------------------- VALIDATION FUNCTIONS -----------------------------------
def validate_email(email: str) -> bool:
    """Validate email format."""
    try:
        EmailStr.validate(email)
        return True
    except Exception:
        return False


def validate_password(password: str) -> bool:
    """Validate password requirements (8-100 characters)."""
    if not isinstance(password, str):
        return False
    return 8 <= len(password) <= 100


#---------------------- LOGIN VALDATION -----------------------------------
class LoginRequest(BaseModel):
    email: EmailStr  # Automatically validates email format
    password: str = Field(..., min_length=8, max_length=100)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    
    #@field_validator('password')
    #@classmethod
    #def password_strength(cls, v):
    #    if not re.search(r'[A-Z]', v):
    #        raise ValueError('Password must contain at least one uppercase letter')
    #    if not re.search(r'[a-z]', v):
    #        raise ValueError('Password must contain at least one lowercase letter')
    #    if not re.search(r'[0-9]', v):
    #        raise ValueError('Password must contain at least one digit')
    #    return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        # Sanitize to prevent XSS
        return sanitize_input(v.strip())

class UpdateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    fname: str = Field(..., min_length=1, max_length=50)
    lname: str = Field(..., min_length=1, max_length=50)
    
    @field_validator('fname', 'lname')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        # Sanitize to prevent XSS
        return sanitize_input(v.strip())

class AddressRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    line1: str = Field(..., min_length=1, max_length=100)
    line2: str = Field(default="", max_length=100)  # Optional, can be empty
    city: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=50)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country_code: str = Field(..., min_length=2, max_length=3)
    phone: str = Field(..., min_length=6, max_length=20)
    
    @field_validator('full_name', 'line1', 'line2', 'city', 'region')
    @classmethod
    def sanitize_text_fields(cls, v):
        # Sanitize all text fields to prevent XSS
        return sanitize_input(v) if v else v
    
    @field_validator('country_code')
    @classmethod
    def country_code_uppercase(cls, v):
        return sanitize_input(v.upper())  # Auto-convert to uppercase and sanitize
    
    @field_validator('phone')
    @classmethod
    def phone_format(cls, v):
        # Remove non-numeric characters
        digits = re.sub(r'\D', '', v)
        if len(digits) < 6:
            raise ValueError('Phone number must have at least 10 digits')
        return digits
    
    @field_validator('postal_code')
    @classmethod
    def postal_code_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Postal code cannot be empty')
        # Sanitize postal code
        return sanitize_input(v.strip())
    

#--------------- INVENTORY VALIDATION ---------------------------------------
class InventoryItemRequest(BaseModel):
    sku: str
    quantity: int
    unitPriceCents: str
    currencyCode: str
    seller: str
    
    @field_validator('sku', 'currencyCode', 'seller')
    @classmethod
    def sanitize_string_fields(cls, v):
        # Sanitize string fields to prevent XSS
        return sanitize_input(v) if v else v



# ------------------- CART VALIDATION ---------------------------------------
class CartItemRequest(BaseModel):
    inventory_id: str
    quantity: int
    unit_price_cents: str
    currency_code: str
    
    @field_validator('inventory_id', 'currency_code')
    @classmethod
    def sanitize_string_fields(cls, v):
        # Sanitize string fields to prevent XSS
        return sanitize_input(v) if v else v