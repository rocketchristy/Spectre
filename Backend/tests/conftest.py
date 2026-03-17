import pytest
import sys
import os
from pathlib import Path

# Add Backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Also ensure we're in the Backend directory for config.ini access
os.chdir(backend_dir)

# Shared fixtures for all tests
@pytest.fixture
def sample_sku():
    """Sample SKU for testing"""
    return "PC0002ENN"

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    }

@pytest.fixture
def sample_address():
    """Sample address for testing"""
    return {
        "full_name": "John Doe",
        "line1": "123 Main St",
        "line2": "Apt 4B",
        "city": "New York",
        "region": "NY",
        "postal_code": "10001",
        "country_code": "US",
        "phone": "1234567890"
    }

@pytest.fixture
def malicious_strings():
    """Sample XSS attack strings for testing sanitization"""
    return [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src='malicious.com'></iframe>",
        "onclick='alert(1)'",
    ]
