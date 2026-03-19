import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path


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
def products_dao(mock_connection_pool):
    """Initialize ProductsDAO with mock connection pool"""
    from Backend.DatabaseAccess.products_dao import ProductsDAO
    return ProductsDAO(mock_connection_pool)


@pytest.fixture
def inventory_dao(mock_connection_pool):
    """Initialize InventoryDAO with mock connection pool"""
    from Backend.DatabaseAccess.inventory_dao import InventoryDAO
    return InventoryDAO(mock_connection_pool)


# Test constants
VALID_SELLER_ID = 1
VALID_INVENTORY_ID = 5
STANDARD_QUANTITY = 50
STANDARD_PRICE_CENTS = 9999
SAMPLE_SKU = '001ST001SN001A'
SAMPLE_SERIES = '001'
SAMPLE_STYLE = 'ST001'
SAMPLE_SERIAL = 'SN001'
SAMPLE_MODIFIER = 'A'
DEFAULT_CURRENCY = 'USD'


class TestProductsDAO:
    """Unit tests for ProductsDAO class"""

    def test_get_product_types(self, products_dao, mock_connection_pool):
        """Test retrieving all product types"""
        expected_types = [
            {'COL1': '123', 'COL2': 2999, 'COL3': 'Premium Watch'},
            {'COL1': '124', 'COL2': 4999, 'COL3': 'Designer Watch'}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_types + [None]
            
            result = products_dao.get_product_types()
            
            assert result['status'] == 'success'
            assert len(result['output']) == 2
            assert result['output'][0]['COL1'] == '123'
            assert result['output'][1]['COL2'] == 4999
            mock_db.prepare.assert_called_once()
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_product_types_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_product_types"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = products_dao.get_product_types()
            
            assert result['status'] == 'error'
            assert 'reason' in result
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_product_types_empty(self, products_dao, mock_connection_pool):
        """Test retrieving product types when catalog is empty"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = products_dao.get_product_types()
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)
            assert len(result['output']) == 0

    def test_get_modifiers(self, products_dao, mock_connection_pool):
        """Test retrieving modifiers for a style"""
        expected_modifiers = [
            {'MODIFIER_CODE': 'A', 'DESCRIPTION': 'Active'},
            {'MODIFIER_CODE': 'B', 'DESCRIPTION': 'Bronze'}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_modifiers + [None]
            
            result = products_dao.get_modifiers('ST001')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 2

    def test_get_modifiers_empty(self, products_dao, mock_connection_pool):
        """Test retrieving modifiers when none exist for style"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = products_dao.get_modifiers('ST999')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0

    def test_get_modifiers_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_modifiers"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = products_dao.get_modifiers('ST001')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_specific_product_set(self, products_dao, mock_connection_pool):
        """Test retrieving a specific product set"""
        expected_products = [
            {
                'SKU': '001ST001SN001A',
                'SERIES_NAME': 'Classic',
                'STYLE_NAME': 'Standard',
                'PRODUCT_NAME': 'Watch',
                'MODIFIER_NAME': 'Gold',
                'BASE_PRICE_CENTS': 9999,
                'URL': 'http://example.com/image.jpg'
            }
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_products + [None]
            
            result = products_dao.get_specific_product_set('001', 'ST001', 'SN001')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['SKU'] == '001ST001SN001A'

    def test_get_specific_product_set_empty(self, products_dao, mock_connection_pool):
        """Test retrieving product set when no variants exist"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = products_dao.get_specific_product_set('999', 'ST999', 'SN999')

            assert result['status'] == 'success'
            assert result['output'] == []

    def test_get_specific_product_set_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_specific_product_set"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = products_dao.get_specific_product_set('001', 'ST001', 'SN001')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_specific_product(self, products_dao, mock_connection_pool):
        """Test retrieving a specific product variant"""
        expected_product = {
            'SKU': '001ST001SN001A',
            'SERIES_NAME': 'Classic',
            'PRODUCT_NAME': 'Watch',
            'BASE_PRICE_CENTS': 9999
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_product, None]
            
            result = products_dao.get_specific_product('001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'success'
            assert result['output'][0]['SKU'] == '001ST001SN001A'

    def test_get_specific_product_not_found(self, products_dao, mock_connection_pool):
        """Test retrieving specific product when it doesn't exist"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = products_dao.get_specific_product('999', 'ST999', 'SN999', 'X')

            assert result['status'] == 'success'
            assert result['output'] == []

    def test_get_specific_product_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_specific_product"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = products_dao.get_specific_product('001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_product_variant_ids(self, products_dao, mock_connection_pool):
        """Test retrieving product variant IDs by SKU"""
        expected_variants = [
            {'ID': 1, 'PRODUCT_ID': 100},
            {'ID': 2, 'PRODUCT_ID': 100}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_variants + [None]
            
            result = products_dao.get_product_variant_ids('001ST001SN001A')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 2

    def test_get_product_variant_ids_empty(self, products_dao, mock_connection_pool):
        """Test retrieving variant IDs when none exist"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = products_dao.get_product_variant_ids('NONEXISTENT')

            assert result['status'] == 'success'
            assert result['output'] == []

    def test_get_product_variant_ids_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_product_variant_ids"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = products_dao.get_product_variant_ids('001ST001SN001A')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)


class TestInventoryDAO:
    """Unit tests for InventoryDAO class"""

    def test_get_inventory(self, inventory_dao, mock_connection_pool):
        """Test retrieving all inventory"""
        expected_inventory = [
            {
                'SKU': SAMPLE_SKU,
                'QUANTITY_AVAILABLE': STANDARD_QUANTITY,
                'UNIT_PRICE_CENTS': STANDARD_PRICE_CENTS,
                'SELLER_ID': VALID_SELLER_ID
            }
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_inventory + [None]
            
            result = inventory_dao.get_inventory()
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            # Verify inventory data
            inv = result['output'][0]
            assert inv['SKU'] == SAMPLE_SKU
            assert inv['QUANTITY_AVAILABLE'] == STANDARD_QUANTITY
            assert inv['SELLER_ID'] == VALID_SELLER_ID
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_inventory_empty(self, inventory_dao, mock_connection_pool):
        """Test retrieving inventory when empty"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = inventory_dao.get_inventory()
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling in get_inventory"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = inventory_dao.get_inventory()
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_inventory(self, inventory_dao, mock_connection_pool):
        """Test retrieving inventory for a specific seller"""
        expected_inventory = [
            {'SKU': '001ST001SN001A', 'QUANTITY_AVAILABLE': 25, 'SELLER_ID': 1}
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_inventory + [None]
            
            result = inventory_dao.get_user_inventory(1)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1

    def test_get_user_inventory_empty(self, inventory_dao, mock_connection_pool):
        """Test retrieving inventory when seller has none"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = inventory_dao.get_user_inventory(9999)

            assert result['status'] == 'success'
            assert result['output'] == []

    def test_get_user_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling in get_user_inventory"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.get_user_inventory(1)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_sku_details(self, inventory_dao, mock_connection_pool):
        """Test retrieving details for a specific SKU from a seller"""
        expected_sku = {
            'SKU': '001ST001SN001A',
            'QUANTITY_AVAILABLE': 100,
            'UNIT_PRICE_CENTS': 9999
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_sku, None]
            
            result = inventory_dao.get_sku_details(1, '001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['SKU'] == '001ST001SN001A'

    def test_get_sku_details_not_found(self, inventory_dao, mock_connection_pool):
        """Test retrieving SKU details when not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = inventory_dao.get_sku_details(1, '999', 'ST999', 'SN999', 'X')

            assert result['status'] == 'success'
            assert result['output'] == []

    def test_get_sku_details_error(self, inventory_dao, mock_connection_pool):
        """Test error handling in get_sku_details"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.get_sku_details(1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_quantity(self, inventory_dao, mock_connection_pool):
        """Test updating inventory quantity"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = inventory_dao.update_quantity(75, VALID_SELLER_ID, SAMPLE_SERIES, SAMPLE_STYLE, SAMPLE_SERIAL, SAMPLE_MODIFIER)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.num_rows.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_quantity_not_found(self, inventory_dao, mock_connection_pool):
        """Test updating quantity when item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = inventory_dao.update_quantity(75, 1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()

    def test_update_quantity_error(self, inventory_dao, mock_connection_pool):
        """Test error handling with rollback when update_quantity fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.update_quantity(75, 1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_inventory(self, inventory_dao, mock_connection_pool):
        """Test adding new inventory item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt

            result = inventory_dao.add_inventory(
                1, '001', 'ST001', 'SN001', 'A', 50, 9999, 'USD'
            )

            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling when adding inventory"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.add_inventory(
                1, '001', 'ST001', 'SN001', 'A', 50, 9999, 'USD'
            )

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_inventory(self, inventory_dao, mock_connection_pool):
        """Test removing inventory item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1

            result = inventory_dao.remove_inventory(1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'success'
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_inventory_not_found(self, inventory_dao, mock_connection_pool):
        """Test removing inventory when item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = inventory_dao.remove_inventory(1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()

    def test_remove_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling with rollback when remove_inventory fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.remove_inventory(1, '001', 'ST001', 'SN001', 'A')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_remove_user_inventory(self, inventory_dao, mock_connection_pool):
        """Test soft delete of inventory item (set quantity to 0)"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = inventory_dao.remove_user_inventory(seller_id=1, inventory_id=5)
            
            assert result['status'] == 'success'

    def test_remove_user_inventory_not_found(self, inventory_dao, mock_connection_pool):
        """Test soft delete when inventory item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = inventory_dao.remove_user_inventory(seller_id=1, inventory_id=9999)
            
            assert result['status'] == 'error'
            assert 'not found' in result['reason']

    def test_remove_user_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling in remove_user_inventory"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = inventory_dao.remove_user_inventory(seller_id=1, inventory_id=5)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

