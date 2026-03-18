import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path


class TestProductsDAO:
    """Unit tests for ProductsDAO class"""

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock database connection pool"""
        pool = Mock()
        mock_conn = MagicMock()
        pool.get_connection = Mock(return_value=mock_conn)
        pool.return_connection = Mock()
        return pool

    @pytest.fixture
    def products_dao(self, mock_connection_pool):
        """Initialize ProductsDAO with mock connection pool"""
        from Backend.DatabaseAccess.products_dao import ProductsDAO
        return ProductsDAO(mock_connection_pool)

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

    def test_get_product_types_error(self, products_dao, mock_connection_pool):
        """Test error handling in get_product_types"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.products_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = products_dao.get_product_types()
            
            assert result['status'] == 'error'
            assert 'reason' in result

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


class TestInventoryDAO:
    """Unit tests for InventoryDAO class"""

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock database connection pool"""
        pool = Mock()
        mock_conn = MagicMock()
        pool.get_connection = Mock(return_value=mock_conn)
        pool.return_connection = Mock()
        return pool

    @pytest.fixture
    def inventory_dao(self, mock_connection_pool):
        """Initialize InventoryDAO with mock connection pool"""
        from Backend.DatabaseAccess.inventory_dao import InventoryDAO
        return InventoryDAO(mock_connection_pool)

    def test_get_inventory(self, inventory_dao, mock_connection_pool):
        """Test retrieving all inventory"""
        expected_inventory = [
            {
                'SKU': '001ST001SN001A',
                'QUANTITY_AVAILABLE': 50,
                'UNIT_PRICE_CENTS': 9999,
                'SELLER_ID': 1
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

    def test_update_quantity(self, inventory_dao, mock_connection_pool):
        """Test updating inventory quantity"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = inventory_dao.update_quantity(75, 1, '001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'success'

    def test_update_quantity_not_found(self, inventory_dao, mock_connection_pool):
        """Test updating quantity when item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = inventory_dao.update_quantity(75, 1, '001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'error'

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

    def test_add_inventory_error(self, inventory_dao, mock_connection_pool):
        """Test error handling when adding inventory"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = inventory_dao.add_inventory(
                1, '001', 'ST001', 'SN001', 'A', 50, 9999, 'USD'
            )
            
            assert result['status'] == 'error'

    def test_remove_inventory(self, inventory_dao, mock_connection_pool):
        """Test removing inventory item"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = inventory_dao.remove_inventory(1, '001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'success'

    def test_remove_inventory_not_found(self, inventory_dao, mock_connection_pool):
        """Test removing inventory when item not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.inventory_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = inventory_dao.remove_inventory(1, '001', 'ST001', 'SN001', 'A')
            
            assert result['status'] == 'error'

