import sys
import os
import configparser
from unittest.mock import MagicMock, patch, Mock

# --- Pre-import mocking for ibm_db and config.ini ---
# ibm_db requires the Db2 CLI driver which isn't available in test environments.
# Both connection_pool.py and inventory_dao.py read config.ini and import ibm_db
# at module level, so we must mock these before importing the server.
sys.modules['ibm_db'] = MagicMock()
os.add_dll_directory = MagicMock()

_original_read = configparser.ConfigParser.read
def _mock_config_read(self, filenames, encoding=None):
    if isinstance(filenames, str) and 'config.ini' in filenames:
        self.read_dict({
            'database': {
                'clidriver_path': 'C:/mock/clidriver',
                'hostname': 'localhost',
                'port': '50000',
                'database': 'testdb',
                'username': 'testuser',
                'password': 'testpass',
            },
            'sku': {
                'series_length': '2',
                'style_length': '1',
                'serial_length': '4',
                'modifier_length': '3',
            },
        })
        return [filenames]
    return _original_read(self, filenames, encoding=encoding)

configparser.ConfigParser.read = _mock_config_read

# Now safe to import the server
import pytest
from fastapi.testclient import TestClient
from Backend.RestAPI.server import app


@pytest.fixture
def client():
    """Create test client for API with mocked database connection"""
    mock_pool = MagicMock()
    app.state.db_pool = mock_pool
    return TestClient(app)


@pytest.fixture
def mock_user_dao():
    """Mock UserDAO for integration tests"""
    with patch('Backend.RestAPI.Routes.user.UserDAO') as MockDAO:
        instance = MockDAO.return_value
        yield instance


@pytest.fixture
def mock_cart_dao():
    """Mock CartDAO for integration tests"""
    with patch('Backend.RestAPI.Routes.user.CartDAO') as MockDAO:
        instance = MockDAO.return_value
        yield instance


class TestHealthCheckEndpoints:
    """Test health check endpoints that don't require database"""

    def test_hello_world(self, client):
        """Test /hello_world endpoint returns greeting"""
        response = client.get('/hello_world')
        assert response.status_code == 200
        assert response.json() == "Hi All"

    def test_hola_mundo(self, client):
        """Test /hola_mundo endpoint returns Spanish greeting"""
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
        """Test 405 for unsupported HTTP method on GET-only endpoint"""
        response = client.post('/spectre/api/products/')
        assert response.status_code == 405

    def test_422_invalid_json_body(self, client):
        """Test 422 for malformed JSON in request body"""
        response = client.post(
            '/spectre/api/user/register',
            content='{invalid json}',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 422

    def test_422_missing_required_fields(self, client, sample_user_data):
        """Test 422 for incomplete registration data"""
        incomplete_data = {'email': 'test@example.com'}
        response = client.post('/spectre/api/user/register', json=incomplete_data)
        assert response.status_code == 422

    def test_422_invalid_email_format(self, client, sample_user_data):
        """Test 422 for invalid email format in registration"""
        user_data = sample_user_data.copy()
        user_data['email'] = 'not-an-email'
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422


class TestUserAPIValidation:
    """Test User API input validation via FastAPI/Pydantic"""

    def test_register_missing_email(self, client, sample_user_data):
        """Test registration rejects request without email"""
        user_data = sample_user_data.copy()
        del user_data['email']
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_password(self, client, sample_user_data):
        """Test registration rejects request without password"""
        user_data = sample_user_data.copy()
        del user_data['password']
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_first_name(self, client, sample_user_data):
        """Test registration rejects request without first_name"""
        user_data = sample_user_data.copy()
        del user_data['first_name']
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_missing_last_name(self, client, sample_user_data):
        """Test registration rejects request without last_name"""
        user_data = sample_user_data.copy()
        del user_data['last_name']
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_short_password(self, client, sample_user_data):
        """Test registration rejects password shorter than 8 characters"""
        user_data = sample_user_data.copy()
        user_data['password'] = 'short'
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_empty_first_name(self, client, sample_user_data):
        """Test registration rejects empty first_name"""
        user_data = sample_user_data.copy()
        user_data['first_name'] = ''
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422

    def test_register_empty_last_name(self, client, sample_user_data):
        """Test registration rejects empty last_name"""
        user_data = sample_user_data.copy()
        user_data['last_name'] = ''
        response = client.post('/spectre/api/user/register', json=user_data)
        assert response.status_code == 422


class TestUserAPIEndpoints:
    """Test User API endpoints with mocked DAO layer"""

    def test_register_success(self, client, sample_user_data):
        """Test successful user registration returns 201"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO, \
             patch('Backend.RestAPI.Routes.user.CartDAO') as MockCartDAO:
            user_dao = MockUserDAO.return_value
            cart_dao = MockCartDAO.return_value
            user_dao.add_user.return_value = {"status": "success"}
            user_dao.get_user.return_value = {"status": "success", "output": [{"ID": 1}]}
            cart_dao.create_cart.return_value = {"status": "success"}

            response = client.post('/spectre/api/user/register', json=sample_user_data)

            assert response.status_code == 201
            assert response.json()['message'] == "User registered successfully"
            user_dao.add_user.assert_called_once()

    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email returns 400"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.add_user.return_value = {"status": "error", "reason": "Duplicate email"}

            response = client.post('/spectre/api/user/register', json=sample_user_data)

            assert response.status_code == 400

    def test_login_success(self, client):
        """Test successful login returns 200 with token"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            from Backend.Utilities.utilities import hash_password
            pwd_hash = hash_password("SecurePass123!")
            user_dao.get_user.return_value = {
                "status": "success",
                "output": [{"ID": 1, "HASHED_PASSWORD": pwd_hash, "FIRST_NAME": "John"}]
            }
            user_dao.add_token.return_value = {"status": "success"}
            user_dao.get_token.return_value = {
                "status": "success",
                "output": [{"ID": 42}]
            }

            response = client.post('/spectre/api/user/login', json={
                "email": "test@example.com",
                "password": "SecurePass123!"
            })

            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert data["token"] == 42
            assert data["first_name"] == "John"

    def test_login_invalid_email(self, client):
        """Test login with nonexistent email returns 401"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.get_user.return_value = {"status": "success", "output": []}

            response = client.post('/spectre/api/user/login', json={
                "email": "nobody@example.com",
                "password": "SecurePass123!"
            })

            assert response.status_code == 401

    def test_login_wrong_password(self, client):
        """Test login with wrong password returns 401"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.get_user.return_value = {
                "status": "success",
                "output": [{"ID": 1, "HASHED_PASSWORD": "wrong_hash", "FIRST_NAME": "John"}]
            }

            response = client.post('/spectre/api/user/login', json={
                "email": "test@example.com",
                "password": "SecurePass123!"
            })

            assert response.status_code == 401

    def test_get_user_data_requires_auth(self, client):
        """Test that GET /user/ returns 422 without token header"""
        response = client.get('/spectre/api/user/')
        assert response.status_code == 422

    def test_get_user_data_invalid_token(self, client):
        """Test that GET /user/ returns 401 with invalid token"""
        with patch('Backend.RestAPI.Routes.user.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.get_user_id.return_value = {"status": "error", "reason": "Token not found"}

            response = client.get('/spectre/api/user/', headers={"token": "invalid"})

            assert response.status_code == 401


class TestProductAPIEndpoints:
    """Test Product API endpoints with mocked DAO layer"""

    def test_get_all_products_success(self, client):
        """Test GET /products/ returns product list"""
        with patch('Backend.RestAPI.Routes.products.ProductsDAO') as MockDAO:
            dao = MockDAO.return_value
            dao.get_product_types.return_value = {
                "status": "success",
                "output": [{"COL1": "PC0001", "COL2": 2999, "COL3": "Watch"}]
            }

            response = client.get('/spectre/api/products/')

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1

    def test_get_all_products_empty(self, client):
        """Test GET /products/ returns empty list when no products"""
        with patch('Backend.RestAPI.Routes.products.ProductsDAO') as MockDAO:
            dao = MockDAO.return_value
            dao.get_product_types.return_value = {"status": "success", "output": []}

            response = client.get('/spectre/api/products/')

            assert response.status_code == 200
            assert response.json() == []

    def test_get_all_products_db_error(self, client):
        """Test GET /products/ returns 500 on database error"""
        with patch('Backend.RestAPI.Routes.products.ProductsDAO') as MockDAO:
            dao = MockDAO.return_value
            dao.get_product_types.return_value = {"status": "error", "reason": "DB down"}

            response = client.get('/spectre/api/products/')

            assert response.status_code == 500

    def test_get_product_invalid_sku_length(self, client):
        """Test GET /products/{sku} returns 404 for invalid SKU length"""
        response = client.get('/spectre/api/products/ABC')
        assert response.status_code == 404


class TestInventoryAPIEndpoints:
    """Test Inventory API endpoints with mocked DAO layer"""

    def test_get_all_inventory_success(self, client):
        """Test GET /inventory/ returns inventory list"""
        with patch('Backend.RestAPI.Routes.inventory.InventoryDAO') as MockDAO:
            dao = MockDAO.return_value
            dao.get_inventory.return_value = {
                "status": "success",
                "output": [{"SKU": "PC0001ENN", "QUANTITY_AVAILABLE": 50}]
            }

            response = client.get('/spectre/api/inventory/')

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1

    def test_get_all_inventory_db_error(self, client):
        """Test GET /inventory/ returns 500 on database error"""
        with patch('Backend.RestAPI.Routes.inventory.InventoryDAO') as MockDAO:
            dao = MockDAO.return_value
            dao.get_inventory.return_value = {"status": "error", "reason": "DB down"}

            response = client.get('/spectre/api/inventory/')

            assert response.status_code == 500

    def test_get_user_inventory_requires_auth(self, client):
        """Test GET /inventory/me returns 422 without token header"""
        response = client.get('/spectre/api/inventory/me')
        assert response.status_code == 422


class TestCartAPIEndpoints:
    """Test Cart API endpoints with mocked DAO layer"""

    def test_get_cart_requires_auth(self, client):
        """Test GET /cart/ returns 422 without token header"""
        response = client.get('/spectre/api/cart/')
        assert response.status_code == 422

    def test_get_cart_invalid_token(self, client):
        """Test GET /cart/ returns 401 with invalid token"""
        with patch('Backend.RestAPI.Routes.cart.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.get_user_id.return_value = {"status": "error", "reason": "Token not found"}

            response = client.get('/spectre/api/cart/', headers={"token": "invalid"})

            assert response.status_code == 401

    def test_get_cart_success(self, client):
        """Test GET /cart/ returns cart items with valid token"""
        with patch('Backend.RestAPI.Routes.cart.UserDAO') as MockUserDAO, \
             patch('Backend.RestAPI.Routes.cart.CartDAO') as MockCartDAO:
            user_dao = MockUserDAO.return_value
            cart_dao = MockCartDAO.return_value
            user_dao.get_user_id.return_value = {"status": "success", "output": [{"USER_ID": 1}]}
            cart_dao.get_cart.return_value = {"status": "success", "output": []}

            response = client.get('/spectre/api/cart/', headers={"token": "valid"})

            assert response.status_code == 200
            assert response.json() == []


class TestOrdersAPIEndpoints:
    """Test Orders API endpoints with mocked DAO layer"""

    def test_get_orders_requires_auth(self, client):
        """Test GET /orders/me returns 422 without token header"""
        response = client.get('/spectre/api/orders/me')
        assert response.status_code == 422

    def test_get_orders_invalid_token(self, client):
        """Test GET /orders/me returns 404 with invalid token"""
        with patch('Backend.RestAPI.Routes.orders.UserDAO') as MockUserDAO:
            user_dao = MockUserDAO.return_value
            user_dao.get_user_id.return_value = {"status": "error", "reason": "Token not found"}

            response = client.get('/spectre/api/orders/me', headers={"token": "invalid"})

            assert response.status_code == 404

    def test_get_orders_success(self, client):
        """Test GET /orders/me returns order history with valid token"""
        with patch('Backend.RestAPI.Routes.orders.UserDAO') as MockUserDAO, \
             patch('Backend.RestAPI.Routes.orders.OrdersDAO') as MockOrdersDAO:
            user_dao = MockUserDAO.return_value
            orders_dao = MockOrdersDAO.return_value
            user_dao.get_user_id.return_value = {"status": "success", "output": [{"USER_ID": 1}]}
            orders_dao.get_user_orders.return_value = {
                "status": "success",
                "output": [{"ID": 101, "TOTAL_CENTS": 9999}]
            }

            response = client.get('/spectre/api/orders/me', headers={"token": "valid"})

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["ID"] == 101



