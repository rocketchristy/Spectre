from pydantic import BaseModel, EmailStr, Field, field_validator
import re

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
        return v.strip()

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
        return v.strip()

class AddressRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    line1: str = Field(..., min_length=1, max_length=100)
    line2: str = Field(default="", max_length=100)  # Optional, can be empty
    city: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=50)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country_code: str = Field(..., min_length=2, max_length=3)
    phone: str = Field(..., min_length=6, max_length=20)
    
    @field_validator('country_code')
    @classmethod
    def country_code_uppercase(cls, v):
        return v.upper()  # Auto-convert to uppercase
    
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
        return v.strip()