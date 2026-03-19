import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


# Mock ibm_db module before any DAO imports
sys.modules['ibm_db'] = MagicMock()


# Mock the config loading BEFORE importing DAO modules
@pytest.fixture(scope="module", autouse=True)
def mock_config_for_all_tests():
    """Mock configuration loading to prevent import-time failures"""
    mock_config = MagicMock()
    mock_config.__getitem__.return_value = {
        'clidriver_path': 'C:/mock/path',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb',
        'hostname': 'localhost',
        'port': '50000'
    }
    
    with patch('configparser.ConfigParser') as mock_parser:
        mock_parser_instance = MagicMock()
        mock_parser_instance.__getitem__ = mock_config.__getitem__
        mock_parser.return_value = mock_parser_instance
        
        with patch('os.add_dll_directory'):
            yield


@pytest.fixture
def mock_connection_pool():
    """Mock database connection pool - shared fixture"""
    pool = Mock()
    mock_conn = MagicMock()
    pool.get_connection = Mock(return_value=mock_conn)
    pool.return_connection = Mock()
    return pool


@pytest.fixture
def cart_dao(mock_connection_pool):
    """Initialize CartDAO with mock connection pool"""
    from Backend.DatabaseAccess.cart_dao import CartDAO
    return CartDAO(mock_connection_pool)


@pytest.fixture
def orders_dao(mock_connection_pool):
    """Initialize OrdersDAO with mock connection pool"""
    from Backend.DatabaseAccess.orders_dao import OrdersDAO
    return OrdersDAO(mock_connection_pool)


# Test constants
VALID_USER_ID = 123
VALID_CART_ID = 1
VALID_CART_ITEM_ID = 5
VALID_INVENTORY_ID = 5
VALID_ORDER_ID = 101
VALID_ADDRESS_ID = 1
STANDARD_PRICE_CENTS = 9999
STANDARD_QUANTITY = 2
DEFAULT_CURRENCY = 'USD'
SAMPLE_SKU = '001ST001SN001A'
SAMPLE_PRODUCT_NAME = 'Watch'


class TestCartDAO:
    """Unit tests for CartDAO class"""

    def test_create_cart(self, cart_dao, mock_connection_pool):
        """Test creating a new cart for user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = cart_dao.create_cart(user_id=VALID_USER_ID)
            
            assert result['status'] == 'success'
            # Verify database operations were called
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            # Verify connection returned to pool
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_create_cart_error(self, cart_dao, mock_connection_pool):
        """Test error handling when creating cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.create_cart(user_id=VALID_USER_ID)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            # Verify rollback was called on error
            mock_db.rollback.assert_called_once_with(mock_conn)
            # Verify connection still returned to pool
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart_id(self, cart_dao, mock_connection_pool):
        """Test retrieving cart ID for user"""
        expected_cart = {'ID': VALID_CART_ID}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_cart, None]
            
            result = cart_dao.get_cart_id(VALID_USER_ID)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['ID'] == VALID_CART_ID
            # Verify SQL execution
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart_id_not_found(self, cart_dao, mock_connection_pool):
        """Test retrieving cart ID when user has no cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = cart_dao.get_cart_id(9999)

            assert result['status'] == 'success'
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart_id_error(self, cart_dao, mock_connection_pool):
        """Test error handling in get_cart_id"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = cart_dao.get_cart_id(VALID_USER_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart(self, cart_dao, mock_connection_pool):
        """Test retrieving full cart with items"""
        expected_items = [
            {
                'CART_ITEM_ID': VALID_CART_ITEM_ID,
                'SKU': SAMPLE_SKU,
                'PRODUCT_NAME': SAMPLE_PRODUCT_NAME,
                'QUANTITY': STANDARD_QUANTITY,
                'UNIT_PRICE_CENTS': STANDARD_PRICE_CENTS
            }
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_items + [None]
            
            result = cart_dao.get_cart(VALID_USER_ID)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            # Verify actual cart item data
            cart_item = result['output'][0]
            assert cart_item['CART_ITEM_ID'] == VALID_CART_ITEM_ID
            assert cart_item['SKU'] == SAMPLE_SKU
            assert cart_item['PRODUCT_NAME'] == SAMPLE_PRODUCT_NAME
            assert cart_item['QUANTITY'] == STANDARD_QUANTITY
            assert cart_item['UNIT_PRICE_CENTS'] == STANDARD_PRICE_CENTS
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart_empty(self, cart_dao, mock_connection_pool):
        """Test retrieving empty cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = cart_dao.get_cart(VALID_USER_ID)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_cart_error(self, cart_dao, mock_connection_pool):
        """Test error handling in get_cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.get_cart(VALID_USER_ID)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            assert 'reason' in result
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_item(self, cart_dao, mock_connection_pool):
        """Test adding item to cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = cart_dao.add_item(VALID_CART_ID, VALID_INVENTORY_ID, STANDARD_QUANTITY, STANDARD_PRICE_CENTS, DEFAULT_CURRENCY)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_item_error(self, cart_dao, mock_connection_pool):
        """Test error handling when adding item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.add_item(VALID_CART_ID, VALID_INVENTORY_ID, STANDARD_QUANTITY, STANDARD_PRICE_CENTS, DEFAULT_CURRENCY)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_item(self, cart_dao, mock_connection_pool):
        """Test removing item from cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = cart_dao.remove_item(VALID_CART_ID, VALID_CART_ITEM_ID)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.num_rows.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_item_not_found(self, cart_dao, mock_connection_pool):
        """Test removing item when it doesn't exist"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = cart_dao.remove_item(VALID_CART_ID, VALID_CART_ITEM_ID)

            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_item_error(self, cart_dao, mock_connection_pool):
        """Test error handling with rollback when remove_item fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = cart_dao.remove_item(VALID_CART_ID, VALID_CART_ITEM_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_entire_cart(self, cart_dao, mock_connection_pool):
        """Test clearing all items from cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 3
            
            result = cart_dao.remove_entire_cart(VALID_USER_ID)
            
            assert result['status'] == 'success'
            assert result['rows_deleted'] == 3
            assert 'rows_deleted' in result
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_entire_cart_empty(self, cart_dao, mock_connection_pool):
        """Test error when cart is already empty"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = cart_dao.remove_entire_cart(1)

            assert result['status'] == 'error'

    def test_remove_entire_cart_error(self, cart_dao, mock_connection_pool):
        """Test error handling with rollback when remove_entire_cart fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = cart_dao.remove_entire_cart(VALID_USER_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_check_existing_cart_item_found(self, cart_dao, mock_connection_pool):
        """Test checking for existing item in cart - item found"""
        expected_item = {'ID': 5, 'QUANTITY': 2}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_item, None]
            
            result = cart_dao.check_existing_cart_item(cart_id=1, inventory_id=10)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['ID'] == 5
            assert result['output'][0]['QUANTITY'] == 2

    def test_check_existing_cart_item_not_found(self, cart_dao, mock_connection_pool):
        """Test checking for existing item in cart - item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = cart_dao.check_existing_cart_item(cart_id=1, inventory_id=999)
            
            assert result['status'] == 'success'
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_check_existing_cart_item_error(self, cart_dao, mock_connection_pool):
        """Test error handling when checking existing cart item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.check_existing_cart_item(VALID_CART_ID, VALID_INVENTORY_ID)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_cart_item_quantity_success(self, cart_dao, mock_connection_pool):
        """Test updating quantity of existing cart item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = cart_dao.update_quantity(cart_items_id=5, quantity=3)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_cart_item_quantity_not_found(self, cart_dao, mock_connection_pool):
        """Test error when cart item not found for update"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = cart_dao.update_quantity(cart_items_id=999, quantity=5)
            
            assert result['status'] == 'error'
            assert 'Cart item not found' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_cart_item_quantity_error(self, cart_dao, mock_connection_pool):
        """Test error handling when updating quantity"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.update_quantity(VALID_CART_ITEM_ID, 5)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)


class TestOrdersDAO:
    """Unit tests for OrdersDAO class"""

    def test_get_user_orders(self, orders_dao, mock_connection_pool):
        """Test retrieving all orders for a user"""
        user_orders = [
            {'ID': VALID_ORDER_ID, 'TOTAL_CENTS': 15997, 'USER_ID': VALID_USER_ID},
            {'ID': VALID_ORDER_ID + 1, 'TOTAL_CENTS': 29999, 'USER_ID': VALID_USER_ID}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = user_orders + [None]
            
            result = orders_dao.get_user_orders(user_id=VALID_USER_ID)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 2
            # Verify order data
            assert result['output'][0]['ID'] == VALID_ORDER_ID
            assert result['output'][0]['TOTAL_CENTS'] == 15997
            assert result['output'][1]['ID'] == VALID_ORDER_ID + 1
            mock_db.prepare.assert_called_once()
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_orders_empty(self, orders_dao, mock_connection_pool):
        """Test retrieving orders for user with no order history"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = orders_dao.get_user_orders(user_id=999)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_orders_error(self, orders_dao, mock_connection_pool):
        """Test error handling when retrieving orders"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.get_user_orders(user_id=VALID_USER_ID)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order(self, orders_dao, mock_connection_pool):
        """Test creating new order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = orders_dao.add_order(VALID_USER_ID, DEFAULT_CURRENCY, 15997, VALID_ADDRESS_ID, VALID_ADDRESS_ID + 1)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order_error(self, orders_dao, mock_connection_pool):
        """Test error handling when creating order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.add_order(VALID_USER_ID, DEFAULT_CURRENCY, 15997, VALID_ADDRESS_ID, VALID_ADDRESS_ID + 1)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order_item(self, orders_dao, mock_connection_pool):
        """Test adding item to order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt

            result = orders_dao.add_order_item(
                101, 5, 1, '001ST001SN001A', 'Watch', 9999, 'USD', 2
            )

            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order_item_calculates_total(self, orders_dao, mock_connection_pool):
        """Test that add_order_item correctly calculates total_cents = unit_price * quantity"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt

            orders_dao.add_order_item(
                101, 5, 1, 'SKU123', 'Watch', 5000, 'USD', 3
            )

            # Verify the 9th bind_param is total_cents = 5000 * 3 = 15000
            calls = mock_db.bind_param.call_args_list
            assert calls[8][0][2] == 15000  # param 9 = total_cents

    def test_add_order_item_error(self, orders_dao, mock_connection_pool):
        """Test error handling when adding order item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.add_order_item(
                101, 5, 1, '001ST001SN001A', 'Watch', 9999, 'USD', 2
            )
            
            assert result['status'] == 'error'

    def test_get_order_id(self, orders_dao, mock_connection_pool):
        """Test retrieving most recent order ID for user"""
        expected_order = {'ID': 102}

        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_order, None]

            result = orders_dao.get_order_id(123)

            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['ID'] == 102
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_order_id_no_orders(self, orders_dao, mock_connection_pool):
        """Test retrieving order ID when user has no orders"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = orders_dao.get_order_id(999)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0

    def test_get_order_id_error(self, orders_dao, mock_connection_pool):
        """Test error handling in get_order_id"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.get_order_id(123)
            
            assert result['status'] == 'error'

    def test_update_order_cost(self, orders_dao, mock_connection_pool):
        """Test updating order cost"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1

            result = orders_dao.update_order_cost(19997, 101)

            assert result['status'] == 'success'
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_order_cost_not_found(self, orders_dao, mock_connection_pool):
        """Test error when order not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = orders_dao.update_order_cost(19997, 9999)

            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()

    def test_update_order_cost_error(self, orders_dao, mock_connection_pool):
        """Test error handling with rollback when update_order_cost fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = orders_dao.update_order_cost(19997, 101)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_check_address_in_order_exists(self, orders_dao, mock_connection_pool):
        """Test checking if address exists in ORDER_ADDRESSES"""
        expected_address = {
            'ID': 5,
            'FULL_NAME': 'John Doe',
            'LINE1': '123 Main St',
            'LINE2': 'Apt 4',
            'CITY': 'Springfield',
            'REGION': 'IL',
            'POSTAL_CODE': '12345',
            'COUNTRY_CODE': 'US',
            'PHONE': '555-1234'
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_address, None]
            
            result = orders_dao.check_address_in_order(1)
            
            assert result['status'] == 'success'
            assert result['output'][0]['ID'] == 5

    def test_check_address_in_order_not_exists(self, orders_dao, mock_connection_pool):
        """Test checking address that doesn't exist in ORDER_ADDRESSES"""
        expected_address = {
            'ID': None,  # NULL when not in ORDER_ADDRESSES
            'FULL_NAME': 'Jane Smith',
            'LINE1': '456 Oak Ave',
            'LINE2': '',
            'CITY': 'Portland',
            'REGION': 'OR',
            'POSTAL_CODE': '97201',
            'COUNTRY_CODE': 'US',
            'PHONE': '555-5678'
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_address, None]
            
            result = orders_dao.check_address_in_order(2)
            
            assert result['status'] == 'success'
            assert result['output'][0]['ID'] is None

    def test_check_address_in_order_error(self, orders_dao, mock_connection_pool):
        """Test error handling in check_address_in_order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = orders_dao.check_address_in_order(1)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order_address(self, orders_dao, mock_connection_pool):
        """Test creating address snapshot in ORDER_ADDRESSES"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt

            result = orders_dao.add_order_address(
                'John Doe', '123 Main St', 'Apt 4', 
                'Springfield', 'IL', '12345', 'US', '555-1234'
            )

            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_order_address_error(self, orders_dao, mock_connection_pool):
        """Test error handling when adding order address"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = orders_dao.add_order_address(
                'John Doe', '123 Main St', 'Apt 4', 
                'Springfield', 'IL', '12345', 'US', '555-1234'
            )

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

