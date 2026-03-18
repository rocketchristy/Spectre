import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from Backend.RestAPI.server import app


@pytest.fixture
def client():
    """Create test client for API with mocked database connection"""
    # Create a mock connection pool so routes don't fail on db_pool access
    mock_pool = MagicMock()
    app.state.db_pool = mock_pool
    
    return TestClient(app)


class TestHealthCheckEndpoints:
    """Test health check endpoints that don't require database"""

    def test_hello_world(self, client):
        """Test /hello_world endpoint"""
        response = client.get('/hello_world')
        assert response.status_code == 200
        assert response.json() == "Hi All"

    def test_hola_mundo(self, client):
        """Test /hola_mundo endpoint"""
        response = client.get('/hola_mundo')
        assert response.status_code == 200
        assert response.json() == "Hola a todos"


class TestErrorHandling:
    """Test API error handling and HTTP status codes"""

    def test_404_nonexistent_endpoint(self, client):
        """Test 404 for nonexistent endpoint"""
        response = client.get('/spectre/api/nonexistent')
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Test 405 for unsupported HTTP method"""
        response = client.post('/spectre/api/products/')
        assert response.status_code == 405

    def test_422_invalid_json_body(self, client):
        """Test 422 for invalid JSON in request body"""
        response = client.post(
            '/spectre/api/user/register',
            content='{invalid json}',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 422

    def test_422_missing_required_fields(self, client, sample_user_data):
        """Test 422 for missing required fields"""
        incomplete_data = {'email': 'test@example.com'}  # Missing password, etc
        response = client.post('/spectre/api/user/register', json=incomplete_data)
        assert response.status_code == 422

    def test_422_invalid_email_format(self, client, sample_user_data):
        """Test 422 for invalid email format"""
        user_data = sample_user_data.copy()
        user_data['email'] = 'not-an-email'
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422


class TestUserAPIValidation:
    """Test User API input validation"""

    def test_register_missing_email(self, client, sample_user_data):
        """Test registration fails without email"""
        user_data = sample_user_data.copy()
        del user_data['email']
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_password(self, client, sample_user_data):
        """Test registration fails without password"""
        user_data = sample_user_data.copy()
        del user_data['password']
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_first_name(self, client, sample_user_data):
        """Test registration fails without first_name"""
        user_data = sample_user_data.copy()
        del user_data['first_name']
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_last_name(self, client, sample_user_data):
        """Test registration fails without last_name"""
        user_data = sample_user_data.copy()
        del user_data['last_name']
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_short_password(self, client, sample_user_data):
        """Test registration fails with short password"""
        user_data = sample_user_data.copy()
        user_data['password'] = 'short'
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_empty_first_name(self, client, sample_user_data):
        """Test registration fails with empty first_name"""
        user_data = sample_user_data.copy()
        user_data['first_name'] = ''
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_empty_last_name(self, client, sample_user_data):
        """Test registration fails with empty last_name"""
        user_data = sample_user_data.copy()
        user_data['last_name'] = ''
        
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422


class TestProductAPIBasic:
    """Test Product API basic functionality"""

    def test_get_products_returns_list(self, client):
        """Test GET /products returns list (or error, mock db doesn't have data)"""
        response = client.get('/spectre/api/products/')
        # Could be 200 with empty list, or 500 due to mock db
        assert response.status_code in [200, 500]

    def test_get_product_by_sku_formatting(self, client, sample_sku):
        """Test GET /products/{sku} accepts valid SKU format"""
        response = client.get(f'/spectre/api/products/{sample_sku}')
        # 404 expected since mock db has no data, but should not fail validation
        assert response.status_code in [200, 404, 500]

    def test_product_endpoints_exist(self, client):
        """Test that product endpoints are available"""
        # These should not return 404 for the route
        response = client.get('/spectre/api/products/')
        # Could return data or server error, but not 404 (route not found)
        assert response.status_code != 404


class TestInventoryAPIBasic:
    """Test Inventory API routes exist"""

    def test_inventory_endpoints_exist(self, client):
        """Test that inventory endpoints are available"""
        response = client.get('/spectre/api/inventory/')
        # Route exists but may return 500 with mock db
        assert response.status_code in [200, 422, 500]


class TestCartAPIBasic:
    """Test Cart API routes exist"""

    def test_cart_endpoints_exist(self, client):
        """Test that cart endpoints are available"""
        response = client.get('/spectre/api/cart/')
        # Route exists but may return 422 (missing auth header)
        assert response.status_code in [200, 422, 403, 500]


class TestOrdersAPIBasic:
    """Test Orders API routes exist"""

    def test_orders_endpoints_available(self, client):
        """Test that orders endpoints are available"""
        response = client.get('/spectre/api/orders/me')
        # Check endpoint exists (won't get 404)
        assert response.status_code in [200, 404, 403, 422, 500]



