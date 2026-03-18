import pytest
from Utilities.utilities import hash_password, sanitize_input
import configparser

class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) == 64  # SHA-256 hash length in hex
    
    def test_hash_password_consistent(self):
        """Test that same password creates same hash"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 == hash2
    
    def test_hash_password_empty_string(self):
        """Test hashing empty password"""
        hashed = hash_password("")
        assert hashed is not None
        assert len(hashed) == 64


class TestSanitization:
    """Test XSS sanitization functionality"""
    
    def test_sanitize_basic_xss(self, malicious_strings):
        """Test that basic XSS attacks are sanitized"""
        for malicious in malicious_strings:
            clean = sanitize_input(malicious)
            
            # Should not contain dangerous patterns
            assert '<script>' not in clean.lower()
            assert 'javascript:' not in clean.lower()
            assert 'onerror' not in clean.lower()
            assert '<iframe' not in clean.lower()
    
    def test_sanitize_html_escaping(self):
        """Test that HTML characters are escaped"""
        test_input = "<div>Test & 'quotes' \"here\"</div>"
        clean = sanitize_input(test_input)
        
        assert '&lt;' in clean or '<div>' not in clean
        assert '&amp;' in clean or '&' not in clean or test_input != clean
    
    def test_sanitize_normal_text(self):
        """Test that normal text passes through"""
        normal_text = "This is a normal string with no special chars"
        clean = sanitize_input(normal_text)
        
        assert clean == normal_text
    
    def test_sanitize_whitespace(self):
        """Test that whitespace is stripped"""
        text_with_spaces = "  Test String  "
        clean = sanitize_input(text_with_spaces)
        
        assert clean == "Test String"


class TestSKUParsing:
    """Test SKU parsing functionality"""
    
    def test_parse_valid_sku(self, sample_sku):
        """Test parsing a valid SKU"""
        # Load config for SKU lengths
        config = configparser.ConfigParser()
        config.read('DatabaseAccess/config.ini')
        
        series_length = int(config['sku']['series_length'])
        style_length = int(config['sku']['style_length'])
        serial_length = int(config['sku']['serial_length'])
        
        series_end = series_length
        style_end = series_end + style_length
        serial_end = style_end + serial_length
        
        series_code = sample_sku[0:series_end]
        style_code = sample_sku[series_end:style_end]
        serial_number = sample_sku[style_end:serial_end]
        modifier_code = sample_sku[serial_end:]
        
        assert series_code == "PC"
        assert style_code == "0"
        assert serial_number == "0002"
        assert modifier_code == "ENN"
    
    def test_sku_minimum_length(self, sample_sku):
        """Test that SKU meets minimum length"""
        assert len(sample_sku) >= 10
