import pytest
from unittest.mock import Mock, patch, MagicMock


class TestUserDAO:
    """Unit tests for UserDAO class"""

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock database connection pool"""
        pool = Mock()
        mock_conn = MagicMock()
        pool.get_connection = Mock(return_value=mock_conn)
        pool.return_connection = Mock()
        return pool

    @pytest.fixture
    def user_dao(self, mock_connection_pool):
        """Initialize UserDAO with mock connection pool"""
        from Backend.DatabaseAccess.user_dao import UserDAO
        return UserDAO(mock_connection_pool)

    def test_add_user(self, user_dao, mock_connection_pool):
        """Test creating a new user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_user('test@example.com', 'hashed_pwd', 'John', 'Doe')
            
            assert result['status'] == 'success'

    def test_add_user_duplicate_email(self, user_dao, mock_connection_pool):
        """Test handling duplicate email error"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("SQLSTATE=23505")
            
            result = user_dao.add_user('test@example.com', 'hashed_pwd', 'John', 'Doe')
            
            assert result['status'] == 'error'
            assert 'Duplicate email' in result['reason']

    def test_add_user_error(self, user_dao, mock_connection_pool):
        """Test error handling when adding user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_user('test@example.com', 'hashed_pwd', 'John', 'Doe')
            
            assert result['status'] == 'error'

    def test_get_user(self, user_dao, mock_connection_pool):
        """Test retrieving user by email"""
        expected_user = {
            'ID': 1,
            'HASHED_PASSWORD': 'hashed_pwd',
            'FIRST_NAME': 'John',
            'LAST_NAME': 'Doe'
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_user, None]
            
            result = user_dao.get_user('test@example.com')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            assert result['output'][0]['ID'] == 1

    def test_get_user_not_found(self, user_dao, mock_connection_pool):
        """Test getting user when not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = user_dao.get_user('notfound@example.com')
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0

    def test_get_user_addresses(self, user_dao, mock_connection_pool):
        """Test retrieving user addresses"""
        expected_addresses = [
            {
                'FIRST_NAME': 'John',
                'LAST_NAME': 'Doe',
                'ID': 1,
                'FULL_NAME': 'John Doe',
                'LINE1': '123 Main St',
                'CITY': 'Springfield',
                'POSTAL_CODE': '12345',
                'COUNTRY_CODE': 'US'
            }
        ]
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = expected_addresses + [None]
            
            result = user_dao.get_user_addresses(1)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1

    def test_get_user_info(self, user_dao, mock_connection_pool):
        """Test retrieving user basic info"""
        expected_info = {
            'EMAIL': 'test@example.com',
            'FIRST_NAME': 'John',
            'LAST_NAME': 'Doe'
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_info, None]
            
            result = user_dao.get_user_info(1)
            
            assert result['status'] == 'success'
            assert result['output'][0]['EMAIL'] == 'test@example.com'

    def test_add_token(self, user_dao, mock_connection_pool):
        """Test creating authentication token for user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_token(1)
            
            assert result['status'] == 'success'

    def test_add_token_error(self, user_dao, mock_connection_pool):
        """Test error when adding token"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_token(1)
            
            assert result['status'] == 'error'

    def test_delete_token(self, user_dao, mock_connection_pool):
        """Test deleting authentication token"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = user_dao.delete_token(1)
            
            assert result['status'] == 'success'

    def test_delete_token_not_found(self, user_dao, mock_connection_pool):
        """Test deleting token when not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = user_dao.delete_token(9999)
            
            assert result['status'] == 'error'

    def test_get_user_id(self, user_dao, mock_connection_pool):
        """Test retrieving user ID from token"""
        expected_result = {'USER_ID': 1}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_result, None]
            
            result = user_dao.get_user_id(1)
            
            assert result['status'] == 'success'
            assert result['output'][0]['USER_ID'] == 1

    def test_get_user_id_invalid_token(self, user_dao, mock_connection_pool):
        """Test error when token not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = user_dao.get_user_id(9999)
            
            assert result['status'] == 'error'
            assert 'Token not found' in result['reason']

    def test_get_token(self, user_dao, mock_connection_pool):
        """Test retrieving token by email"""
        expected_token = {'ID': 1}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_token, None]
            
            result = user_dao.get_token('test@example.com')
            
            assert result['status'] == 'success'

    def test_update_user_data(self, user_dao, mock_connection_pool):
        """Test updating user profile information"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = user_dao.update_user_data(1, 'new@example.com', 'hashed_pwd', 'Jane', 'Smith')
            
            assert result['status'] == 'success'

    def test_update_user_data_not_found(self, user_dao, mock_connection_pool):
        """Test error when user not found for update"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = user_dao.update_user_data(9999, 'new@example.com', 'hashed_pwd', 'Jane', 'Smith')
            
            assert result['status'] == 'error'

    def test_add_address(self, user_dao, mock_connection_pool):
        """Test adding address to user account"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_address(1, 'John Doe', '123 Main St', 'Apt 4', 'Springfield', 'IL', '12345', 'US', '555-1234')
            
            assert result['status'] == 'success'

    def test_add_address_error(self, user_dao, mock_connection_pool):
        """Test error when adding address"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_address(1, 'John Doe', '123 Main St', 'Apt 4', 'Springfield', 'IL', '12345', 'US', '555-1234')
            
            assert result['status'] == 'error'

    def test_delete_address(self, user_dao, mock_connection_pool):
        """Test deleting address from user account"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = user_dao.delete_address(1, 1)
            
            assert result['status'] == 'success'

    def test_delete_address_not_found(self, user_dao, mock_connection_pool):
        """Test error when address not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = user_dao.delete_address(1, 9999)
            
            assert result['status'] == 'error'

