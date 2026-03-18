import pytest
from unittest.mock import Mock, patch, MagicMock


class TestCartDAO:
    """Unit tests for CartDAO class"""

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock database connection pool"""
        pool = Mock()
        mock_conn = MagicMock()
        pool.get_connection = Mock(return_value=mock_conn)
        pool.return_connection = Mock()
        return pool

    @pytest.fixture
    def cart_dao(self, mock_connection_pool):
        """Initialize CartDAO with mock connection pool"""
        from Backend.DatabaseAccess.cart_dao import CartDAO
        return CartDAO(mock_connection_pool)

    def test_create_cart(self, cart_dao, mock_connection_pool):
        """Test creating a new cart for user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = cart_dao.create_cart(user_id=123)
            
            assert result['status'] == 'success'

    def test_create_cart_error(self, cart_dao, mock_connection_pool):
        """Test error handling when creating cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.create_cart(user_id=123)
            
            assert result['status'] == 'error'

    def test_get_cart_id(self, cart_dao, mock_connection_pool):
        """Test retrieving cart ID for user"""
        expected_cart = {'ID': 1}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_cart, None]
            
            result = cart_dao.get_cart_id(123)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1

    def test_get_cart(self, cart_dao, mock_connection_pool):
        """Test retrieving full cart with items"""
        expected_items = [
            {
                'CART_ITEM_ID': 1,
                'SKU': '001ST001SN001A',
                'PRODUCT_NAME': 'Watch',
                'QUANTITY': 2,
                'UNIT_PRICE_CENTS': 9999
            }
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_items + [None]
            
            result = cart_dao.get_cart(123)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1

    def test_add_item(self, cart_dao, mock_connection_pool):
        """Test adding item to cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = cart_dao.add_item(1, 5, 2, 9999, 'USD')
            
            assert result['status'] == 'success'

    def test_add_item_error(self, cart_dao, mock_connection_pool):
        """Test error handling when adding item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = cart_dao.add_item(1, 5, 2, 9999, 'USD')
            
            assert result['status'] == 'error'

    def test_remove_item(self, cart_dao, mock_connection_pool):
        """Test removing item from cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = cart_dao.remove_item(1, 5)
            
            assert result['status'] == 'success'

    def test_remove_item_not_found(self, cart_dao, mock_connection_pool):
        """Test removing item when it doesn't exist"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = cart_dao.remove_item(1, 5)
            
            assert result['status'] == 'error'

    def test_remove_entire_cart(self, cart_dao, mock_connection_pool):
        """Test clearing all items from cart"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 3
            
            result = cart_dao.remove_entire_cart(1)
            
            assert result['status'] == 'success'
            assert result['rows_deleted'] == 3

    def test_remove_entire_cart_empty(self, cart_dao, mock_connection_pool):
        """Test error when cart is already empty"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.cart_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = cart_dao.remove_entire_cart(1)
            
            assert result['status'] == 'error'


class TestOrdersDAO:
    """Unit tests for OrdersDAO class"""

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock database connection pool"""
        pool = Mock()
        mock_conn = MagicMock()
        pool.get_connection = Mock(return_value=mock_conn)
        pool.return_connection = Mock()
        return pool

    @pytest.fixture
    def orders_dao(self, mock_connection_pool):
        """Initialize OrdersDAO with mock connection pool"""
        from Backend.DatabaseAccess.orders_dao import OrdersDAO
        return OrdersDAO(mock_connection_pool)

    def test_get_user_orders(self, orders_dao, mock_connection_pool):
        """Test retrieving all orders for a user"""
        user_orders = [
            {'ID': 101, 'TOTAL_CENTS': 15997, 'USER_ID': 123},
            {'ID': 102, 'TOTAL_CENTS': 29999, 'USER_ID': 123}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = user_orders + [None]
            
            result = orders_dao.get_user_orders(user_id=123)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 2

    def test_get_user_orders_error(self, orders_dao, mock_connection_pool):
        """Test error handling when retrieving orders"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.get_user_orders(user_id=123)
            
            assert result['status'] == 'error'

    def test_add_order(self, orders_dao, mock_connection_pool):
        """Test creating new order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = orders_dao.add_order(123, 'USD', 15997, 1, 2)
            
            assert result['status'] == 'success'

    def test_add_order_error(self, orders_dao, mock_connection_pool):
        """Test error handling when creating order"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = orders_dao.add_order(123, 'USD', 15997, 1, 2)
            
            assert result['status'] == 'error'

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

    def test_update_order_cost(self, orders_dao, mock_connection_pool):
        """Test updating order cost"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = orders_dao.update_order_cost(19997, 101)
            
            assert result['status'] == 'success'

    def test_update_order_cost_not_found(self, orders_dao, mock_connection_pool):
        """Test error when order not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.orders_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = orders_dao.update_order_cost(19997, 9999)
            
            assert result['status'] == 'error'

