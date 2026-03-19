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
def user_dao(mock_connection_pool):
    """Initialize UserDAO with mock connection pool"""
    from Backend.DatabaseAccess.user_dao import UserDAO
    return UserDAO(mock_connection_pool)


# Test constants
VALID_USER_ID = 1
VALID_TOKEN_ID = 1
VALID_ADDRESS_ID = 1
TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'hashed_pwd'
TEST_FIRST_NAME = 'John'
TEST_LAST_NAME = 'Doe'
TEST_FULL_NAME = 'John Doe'
TEST_ADDRESS_LINE1 = '123 Main St'
TEST_CITY = 'Springfield'
TEST_POSTAL_CODE = '12345'
TEST_COUNTRY = 'US'


class TestUserDAO:
    """Unit tests for UserDAO class"""

    def test_add_user(self, user_dao, mock_connection_pool):
        """Test creating a new user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_user(TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_user_duplicate_email(self, user_dao, mock_connection_pool):
        """Test handling duplicate email error"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("SQLSTATE=23505")
            
            result = user_dao.add_user(TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME)
            
            assert result['status'] == 'error'
            assert 'Duplicate email' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_user_error(self, user_dao, mock_connection_pool):
        """Test error handling when adding user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_user(TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user(self, user_dao, mock_connection_pool):
        """Test retrieving user by email"""
        expected_user = {
            'ID': VALID_USER_ID,
            'HASHED_PASSWORD': TEST_PASSWORD,
            'FIRST_NAME': TEST_FIRST_NAME,
            'LAST_NAME': TEST_LAST_NAME
        }
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_user, None]
            
            result = user_dao.get_user(TEST_EMAIL)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 1
            # Verify user data
            user = result['output'][0]
            assert user['ID'] == VALID_USER_ID
            assert user['HASHED_PASSWORD'] == TEST_PASSWORD
            assert user['FIRST_NAME'] == TEST_FIRST_NAME
            assert user['LAST_NAME'] == TEST_LAST_NAME
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_error(self, user_dao, mock_connection_pool):
        """Test error handling when get_user fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Connection timeout")

            result = user_dao.get_user(TEST_EMAIL)

            assert result['status'] == 'error'
            assert 'Connection timeout' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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

    def test_get_user_addresses_multiple(self, user_dao, mock_connection_pool):
        """Test retrieving multiple addresses for user"""
        expected_addresses = [
            {
                'ID': 1,
                'FULL_NAME': 'John Doe',
                'LINE1': '123 Main St',
                'CITY': 'Springfield',
                'POSTAL_CODE': '12345',
                'COUNTRY_CODE': 'US'
            },
            {
                'ID': 2,
                'FULL_NAME': 'John Doe',
                'LINE1': '456 Oak Ave',
                'CITY': 'Portland',
                'POSTAL_CODE': '97201',
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
            assert len(result['output']) == 2

    def test_get_user_addresses_none(self, user_dao, mock_connection_pool):
        """Test retrieving addresses when user has none"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = user_dao.get_user_addresses(1)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0

    def test_get_user_addresses_error(self, user_dao, mock_connection_pool):
        """Test error handling in get_user_addresses"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.get_user_addresses(1)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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
            assert result['output'][0]['FIRST_NAME'] == 'John'
            assert result['output'][0]['LAST_NAME'] == 'Doe'

    def test_get_user_info_not_found(self, user_dao, mock_connection_pool):
        """Test retrieving info for nonexistent user returns empty"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = user_dao.get_user_info(9999)

            assert result['status'] == 'success'
            assert len(result['output']) == 0
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_info_error(self, user_dao, mock_connection_pool):
        """Test error handling in get_user_info"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.get_user_info(VALID_USER_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_token(self, user_dao, mock_connection_pool):
        """Test creating authentication token for user"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_token(VALID_USER_ID)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_token_error(self, user_dao, mock_connection_pool):
        """Test error when adding token"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_token(VALID_USER_ID)
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_delete_token(self, user_dao, mock_connection_pool):
        """Test deleting authentication token"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1
            
            result = user_dao.delete_token(VALID_TOKEN_ID)
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.num_rows.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_delete_token_not_found(self, user_dao, mock_connection_pool):
        """Test deleting token when not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0
            
            result = user_dao.delete_token(9999)
            
            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_id(self, user_dao, mock_connection_pool):
        """Test retrieving user ID from token"""
        expected_result = {'USER_ID': VALID_USER_ID}
        
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_result, None]
            
            result = user_dao.get_user_id(VALID_TOKEN_ID)
            
            assert result['status'] == 'success'
            assert result['output'][0]['USER_ID'] == VALID_USER_ID
            assert len(result['output']) == 1
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_delete_token_error(self, user_dao, mock_connection_pool):
        """Test error handling when delete_token encounters database failure"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.delete_token(VALID_TOKEN_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_user_id_error(self, user_dao, mock_connection_pool):
        """Test error handling when get_user_id encounters database failure"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.get_user_id(VALID_TOKEN_ID)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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
            assert len(result['output']) == 1
            assert result['output'][0]['ID'] == 1
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_token_no_tokens(self, user_dao, mock_connection_pool):
        """Test retrieving token when user has no active tokens"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None

            result = user_dao.get_token('notoken@example.com')

            assert result['status'] == 'success'
            assert result['output'] == []
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_token_error(self, user_dao, mock_connection_pool):
        """Test error handling in get_token"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.get_token(TEST_EMAIL)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_user_data(self, user_dao, mock_connection_pool):
        """Test updating user profile information"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 1

            result = user_dao.update_user_data(1, 'new@example.com', 'hashed_pwd', 'Jane', 'Smith')

            assert result['status'] == 'success'
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_update_user_data_not_found(self, user_dao, mock_connection_pool):
        """Test error when user not found for update"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.num_rows.return_value = 0

            result = user_dao.update_user_data(9999, 'new@example.com', 'hashed_pwd', 'Jane', 'Smith')

            assert result['status'] == 'error'
            assert 'not found' in result['reason'].lower()

    def test_update_user_data_error(self, user_dao, mock_connection_pool):
        """Test error handling with rollback when update_user_data fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.update_user_data(1, 'new@example.com', 'hashed_pwd', 'Jane', 'Smith')

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_address(self, user_dao, mock_connection_pool):
        """Test adding address to user account"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            
            result = user_dao.add_address(
                VALID_USER_ID, TEST_FULL_NAME, TEST_ADDRESS_LINE1, 'Apt 4', 
                TEST_CITY, 'IL', TEST_POSTAL_CODE, TEST_COUNTRY, '555-1234'
            )
            
            assert result['status'] == 'success'
            mock_db.prepare.assert_called_once()
            mock_db.execute.assert_called_once_with(mock_stmt)
            mock_db.commit.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_add_address_error(self, user_dao, mock_connection_pool):
        """Test error when adding address"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")
            
            result = user_dao.add_address(
                VALID_USER_ID, TEST_FULL_NAME, TEST_ADDRESS_LINE1, 'Apt 4', 
                TEST_CITY, 'IL', TEST_POSTAL_CODE, TEST_COUNTRY, '555-1234'
            )
            
            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

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
            assert 'not found' in result['reason'].lower()

    def test_delete_address_error(self, user_dao, mock_connection_pool):
        """Test error handling with rollback when delete_address fails"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.delete_address(1, 1)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_db.rollback.assert_called_once_with(mock_conn)
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

    def test_get_address(self, user_dao, mock_connection_pool):
        """Test retrieving a specific address by ID"""
        expected_address = {
            'ID': 1,
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
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.side_effect = [expected_address, None]
            
            result = user_dao.get_address(1)
            
            assert result['status'] == 'success'
            assert result['output'][0]['ID'] == 1
            assert result['output'][0]['FULL_NAME'] == 'John Doe'

    def test_get_address_not_found(self, user_dao, mock_connection_pool):
        """Test getting address when not found"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_stmt = Mock()
            mock_db.prepare.return_value = mock_stmt
            mock_db.fetch_assoc.return_value = None
            
            result = user_dao.get_address(9999)
            
            assert result['status'] == 'success'
            assert len(result['output']) == 0

    def test_get_address_error(self, user_dao, mock_connection_pool):
        """Test error handling in get_address"""
        mock_conn = mock_connection_pool.get_connection.return_value
        with patch('Backend.DatabaseAccess.user_dao.ibm_db') as mock_db:
            mock_db.prepare.side_effect = Exception("Database error")

            result = user_dao.get_address(1)

            assert result['status'] == 'error'
            assert 'Database error' in result['reason']
            mock_connection_pool.return_connection.assert_called_once_with(mock_conn)

