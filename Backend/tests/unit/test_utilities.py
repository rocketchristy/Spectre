import pytest
from unittest.mock import patch, MagicMock
from Backend.Utilities.utilities import hash_password, sanitize_input, get_token_header
from Backend.Utilities.validation import (
    LoginRequest, RegisterRequest, UpdateUserRequest,
    AddressRequest, InventoryItemRequest, CartItemRequest
)
from pydantic import ValidationError
from fastapi import HTTPException


@pytest.fixture
def malicious_strings():
    """Fixture providing common XSS attack strings for testing"""
    return [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror='alert(1)'>",
        "<iframe src='evil.com'></iframe>",
        "<svg onload=alert(1)>",
        "';DROP TABLE users;--"
    ]


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_hash_password_creates_hash(self):
        """Test that hash_password returns a valid SHA-256 hex string"""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) == 64  # SHA-256 hash length in hex

    def test_hash_password_consistent(self):
        """Test that same password always produces same hash"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 == hash2

    def test_hash_password_different_passwords_differ(self):
        """Test that different passwords produce different hashes"""
        hash1 = hash_password("PasswordA12345")
        hash2 = hash_password("PasswordB12345")

        assert hash1 != hash2

    def test_hash_password_empty_string(self):
        """Test hashing empty password still produces valid hash"""
        hashed = hash_password("")
        assert hashed is not None
        assert len(hashed) == 64

    def test_hash_password_special_characters(self):
        """Test hashing password with unicode and special characters"""
        hashed = hash_password("P@$$w0rd!#%^&*日本語")
        assert len(hashed) == 64

    def test_hash_password_very_long_input(self):
        """Test hashing a very long password"""
        long_password = "A" * 10000
        hashed = hash_password(long_password)
        assert len(hashed) == 64


class TestSanitization:
    """Test XSS sanitization functionality"""

    def test_sanitize_script_tags(self, malicious_strings):
        """Test that script tags and XSS vectors are neutralized"""
        for malicious in malicious_strings:
            clean = sanitize_input(malicious)

            assert '<script>' not in clean.lower()
            assert 'javascript:' not in clean.lower()
            assert 'onerror' not in clean.lower()
            assert '<iframe' not in clean.lower()

    def test_sanitize_html_angle_brackets_escaped(self):
        """Test that < and > are escaped to HTML entities"""
        clean = sanitize_input("<div>content</div>")
        assert '&lt;' in clean
        assert '&gt;' in clean
        assert '<div>' not in clean

    def test_sanitize_ampersand_escaped(self):
        """Test that & is escaped to &amp;"""
        clean = sanitize_input("Tom & Jerry")
        assert '&amp;' in clean
        assert clean == "Tom &amp; Jerry"

    def test_sanitize_quotes_escaped(self):
        """Test that quotes are escaped"""
        clean = sanitize_input('He said "hello"')
        assert '&quot;' in clean or '"' not in clean

    def test_sanitize_normal_text_unchanged(self):
        """Test that normal text passes through unmodified"""
        normal_text = "This is a normal string with no special chars"
        clean = sanitize_input(normal_text)
        assert clean == normal_text

    def test_sanitize_whitespace_stripped(self):
        """Test that leading/trailing whitespace is stripped"""
        clean = sanitize_input("  Test String  ")
        assert clean == "Test String"

    def test_sanitize_empty_string(self):
        """Test that empty string returns empty string"""
        assert sanitize_input("") == ""

    def test_sanitize_none_returns_none(self):
        """Test that None input returns None (guard clause)"""
        assert sanitize_input(None) is None

    def test_sanitize_onload_event_handler(self):
        """Test that onload event handler is removed"""
        clean = sanitize_input("<svg onload=alert(1)>")
        assert 'onload' not in clean.lower()

    def test_sanitize_object_and_embed_tags(self):
        """Test that object and embed tags are removed"""
        clean = sanitize_input("<object data='evil.swf'></object>")
        assert '<object' not in clean.lower()

        clean2 = sanitize_input("<embed src='evil.swf'>")
        assert '<embed' not in clean2.lower()


class TestGetTokenHeader:
    """Test the get_token_header FastAPI dependency"""

    def test_valid_token_returned(self):
        """Test that a valid token string is returned as-is"""
        result = get_token_header(token="abc123")
        assert result == "abc123"

    def test_empty_token_raises_401(self):
        """Test that empty token raises HTTPException 401"""
        with pytest.raises(HTTPException) as exc_info:
            get_token_header(token="")
        assert exc_info.value.status_code == 401

    def test_numeric_token_accepted(self):
        """Test that numeric token strings are accepted"""
        result = get_token_header(token="99999")
        assert result == "99999"


class TestLoginRequestValidation:
    """Test LoginRequest Pydantic model validation"""

    def test_valid_login(self):
        """Test valid login data passes validation"""
        req = LoginRequest(email="user@example.com", password="ValidPass1")
        assert req.email == "user@example.com"
        assert req.password == "ValidPass1"

    def test_invalid_email_rejected(self):
        """Test that invalid email format is rejected"""
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="ValidPass1")

    def test_short_password_rejected(self):
        """Test that password under 8 characters is rejected"""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="short")

    def test_password_too_long_rejected(self):
        """Test that password over 100 characters is rejected"""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="A" * 101)


class TestRegisterRequestValidation:
    """Test RegisterRequest Pydantic model validation"""

    def test_valid_registration(self):
        """Test valid registration data passes validation"""
        req = RegisterRequest(
            email="user@example.com",
            password="ValidPass1",
            first_name="John",
            last_name="Doe"
        )
        assert req.first_name == "John"
        assert req.last_name == "Doe"

    def test_empty_first_name_rejected(self):
        """Test that empty first_name is rejected"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="ValidPass1",
                first_name="",
                last_name="Doe"
            )

    def test_whitespace_only_name_rejected(self):
        """Test that whitespace-only name is rejected by validator"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="ValidPass1",
                first_name="   ",
                last_name="Doe"
            )

    def test_name_sanitized_on_creation(self):
        """Test that XSS in name fields is sanitized"""
        req = RegisterRequest(
            email="user@example.com",
            password="ValidPass1",
            first_name="<script>alert(1)</script>John",
            last_name="Doe"
        )
        assert '<script>' not in req.first_name
        assert 'alert' not in req.first_name.lower() or '&lt;' in req.first_name

    def test_missing_email_rejected(self):
        """Test that missing email field is rejected"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                password="ValidPass1",
                first_name="John",
                last_name="Doe"
            )


class TestUpdateUserRequestValidation:
    """Test UpdateUserRequest Pydantic model validation"""

    def test_valid_update(self):
        """Test valid update data passes validation"""
        req = UpdateUserRequest(
            email="new@example.com",
            password="NewPass123",
            fname="Jane",
            lname="Smith"
        )
        assert req.fname == "Jane"
        assert req.lname == "Smith"

    def test_empty_fname_rejected(self):
        """Test that empty fname is rejected"""
        with pytest.raises(ValidationError):
            UpdateUserRequest(
                email="new@example.com",
                password="NewPass123",
                fname="",
                lname="Smith"
            )

    def test_whitespace_lname_rejected(self):
        """Test that whitespace-only lname is rejected"""
        with pytest.raises(ValidationError):
            UpdateUserRequest(
                email="new@example.com",
                password="NewPass123",
                fname="Jane",
                lname="   "
            )


class TestAddressRequestValidation:
    """Test AddressRequest Pydantic model validation"""

    def test_valid_address(self):
        """Test valid address data passes validation"""
        req = AddressRequest(
            full_name="John Doe",
            line1="123 Main St",
            line2="Apt 4B",
            city="New York",
            region="NY",
            postal_code="10001",
            country_code="US",
            phone="1234567890"
        )
        assert req.full_name == "John Doe"
        assert req.country_code == "US"

    def test_country_code_uppercased(self):
        """Test that country code is converted to uppercase"""
        req = AddressRequest(
            full_name="John Doe",
            line1="123 Main St",
            city="New York",
            region="NY",
            postal_code="10001",
            country_code="us",
            phone="1234567890"
        )
        assert req.country_code == "US"

    def test_phone_digits_only(self):
        """Test that phone number formatting is stripped to digits"""
        req = AddressRequest(
            full_name="John Doe",
            line1="123 Main St",
            city="New York",
            region="NY",
            postal_code="10001",
            country_code="US",
            phone="(123) 456-7890"
        )
        assert req.phone == "1234567890"

    def test_phone_too_short_rejected(self):
        """Test that phone with fewer than 6 digits is rejected"""
        with pytest.raises(ValidationError):
            AddressRequest(
                full_name="John Doe",
                line1="123 Main St",
                city="New York",
                region="NY",
                postal_code="10001",
                country_code="US",
                phone="123"
            )

    def test_empty_postal_code_rejected(self):
        """Test that empty postal code is rejected"""
        with pytest.raises(ValidationError):
            AddressRequest(
                full_name="John Doe",
                line1="123 Main St",
                city="New York",
                region="NY",
                postal_code="   ",
                country_code="US",
                phone="1234567890"
            )

    def test_missing_required_field_rejected(self):
        """Test that missing required field is rejected"""
        with pytest.raises(ValidationError):
            AddressRequest(
                full_name="John Doe",
                # line1 is missing
                city="New York",
                region="NY",
                postal_code="10001",
                country_code="US",
                phone="1234567890"
            )

    def test_line2_optional(self):
        """Test that line2 is optional and defaults to empty string"""
        req = AddressRequest(
            full_name="John Doe",
            line1="123 Main St",
            city="New York",
            region="NY",
            postal_code="10001",
            country_code="US",
            phone="1234567890"
        )
        assert req.line2 == ""

    def test_xss_in_address_fields_sanitized(self):
        """Test that XSS in text fields is sanitized"""
        req = AddressRequest(
            full_name="<script>alert(1)</script>",
            line1="123 Main St",
            city="New York",
            region="NY",
            postal_code="10001",
            country_code="US",
            phone="1234567890"
        )
        assert '<script>' not in req.full_name


class TestInventoryItemRequestValidation:
    """Test InventoryItemRequest Pydantic model validation"""

    def test_valid_inventory_item(self):
        """Test valid inventory item data passes validation"""
        req = InventoryItemRequest(
            sku="PC0001ENN",
            quantity=50,
            unitPriceCents="9999",
            currencyCode="USD"
        )
        assert req.sku == "PC0001ENN"
        assert req.quantity == 50

    def test_xss_in_sku_sanitized(self):
        """Test that XSS in SKU field is sanitized"""
        req = InventoryItemRequest(
            sku="<script>alert(1)</script>",
            quantity=1,
            unitPriceCents="100",
            currencyCode="USD"
        )
        assert '<script>' not in req.sku


class TestCartItemRequestValidation:
    """Test CartItemRequest Pydantic model validation"""

    def test_valid_cart_item(self):
        """Test valid cart item data passes validation"""
        req = CartItemRequest(
            inventory_id="5",
            quantity=2,
            unit_price_cents="9999",
            currency_code="USD"
        )
        assert req.inventory_id == "5"
        assert req.quantity == 2

    def test_xss_in_inventory_id_sanitized(self):
        """Test that XSS in inventory_id is sanitized"""
        req = CartItemRequest(
            inventory_id="<script>alert(1)</script>",
            quantity=1,
            unit_price_cents="100",
            currency_code="USD"
        )
        assert '<script>' not in req.inventory_id
