"""
================================================================================
File: user_dao.py
Description: Data Access Object for user management and authentication operations
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module provides database operations for user accounts including:
- User registration and authentication
- Address management
- Session token management
- User profile updates
================================================================================
"""

import os
import configparser

# Load database configuration
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
clidriver_path = config['database']['clidriver_path']

# Set up IBM Db2 CLI driver paths
os.add_dll_directory(f"{clidriver_path}/bin")
clidriver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")

import ibm_db


class UserDAO:
    """
    Data Access Object for User table operations.
    
    Handles all database interactions related to user accounts, addresses,
    authentication tokens, and profile management.
    """
    
    def __init__(self, pool):
        """
        Initialize UserDAO with a database connection pool.
        
        Inputs:
            pool (IBMDBConnectionPool): Database connection pool instance
        
        Outputs:
            None
        """
        self.pool = pool

    def add_user(self, email, password, first_name, last_name):
        """
        Create a new user account in the database.
        
        Inputs:
            email (str): User's email address (must be unique)
            password (str): Hashed password
            first_name (str): User's first name
            last_name (str): User's last name
        
        Outputs:
            dict: {"status": "success"} on success
                  {"status": "error", "reason": str} on failure
        
        Notes:
            - Checks for duplicate email addresses
            - Commits transaction on success, rolls back on failure
        """
        conn = self.pool.get_connection()
        try:
            sql = """INSERT INTO USER01.USERS 
                    (EMAIL,
                    HASHED_PASSWORD,
                    FIRST_NAME,
                    LAST_NAME) 
                VALUES (?, ?, ?, ?)"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.bind_param(stmt, 3, first_name)
            ibm_db.bind_param(stmt, 4, last_name)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            error_code = ibm_db.conn_error(conn)
            error_msg = ibm_db.conn_errormsg(conn)
            if "SQLSTATE=23505" in str(e) or "SQLSTATE=23505" in error_msg:
                return {"status": "error", "reason": "Duplicate email"}
            else:
                return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_user(self, email):
        """
        Retrieve user information by email address.
        
        Inputs:
            email (str): User's email address to look up
        
        Outputs:
            dict: {"status": "success", "output": list of user records}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Output list contains dicts with keys: ID, HASHED_PASSWORD, FIRST_NAME, LAST_NAME
        """
        conn = self.pool.get_connection()
        try:
            sql = """SELECT 
                    ID,
                    HASHED_PASSWORD,
                    FIRST_NAME,
                    LAST_NAME
                 FROM USER01.USERS WHERE EMAIL = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)
    
    def get_user_addresses(self, user_id):
        """
        Retrieve all addresses associated with a user.
        
        Inputs:
            user_id (int): User's unique identifier
        
        Outputs:
            dict: {"status": "success", "output": list of address records}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Output includes user name and all address fields for each address
        """
        conn = self.pool.get_connection()
        try:
            sql = """
                SELECT 
                    USER01.USERS.FIRST_NAME,
                    USER01.USERS.LAST_NAME,
                    USER01.ADDRESSES.ID,
                    USER01.ADDRESSES.FULL_NAME,
                    USER01.ADDRESSES.LINE1,
                    USER01.ADDRESSES.LINE2,
                    USER01.ADDRESSES.CITY,
                    USER01.ADDRESSES.REGION,
                    USER01.ADDRESSES.POSTAL_CODE,
                    USER01.ADDRESSES.COUNTRY_CODE,
                    USER01.ADDRESSES.PHONE 
                 FROM USER01.USERS LEFT JOIN USER01.ADDRESSES
                 ON USER01.USERS.ID = USER01.ADDRESSES.USER_ID
                 WHERE USER01.USERS.ID = ?
                 """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, user_id)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_user_info(self, user_id):
        """
        Retrieve basic user information by user ID.
        
        Inputs:
            user_id (int): User's unique identifier
        
        Outputs:
            dict: {"status": "success", "output": list with EMAIL, FIRST_NAME, LAST_NAME}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Returns user's public information without password hash
        """
        conn = self.pool.get_connection()
        try:
            sql = """
                SELECT 
                    USER01.USERS.EMAIL,
                    USER01.USERS.FIRST_NAME,
                    USER01.USERS.LAST_NAME
                FROM USER01.USERS
                WHERE USER01.USERS.ID = ?
                 """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, user_id)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def add_token(self, user_id):
        """
        Create a new authentication token for a user session.
        
        Inputs:
            user_id (int): User's unique identifier
        
        Outputs:
            dict: {"status": "success"} on success
                  {"status": "error", "reason": str} on failure
        
        Side Effects:
            Inserts new token record in TOKENS table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Token ID is auto-generated by database
            Used for session management and authentication
        """
        conn = self.pool.get_connection()
        try:
            sql="""INSERT INTO USER01.TOKENS (USER_ID) VALUES (?)"""
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user_id)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def delete_token(self, token):
        """
        Remove an authentication token (logout user session).
        
        Inputs:
            token (str): Token ID to delete
        
        Outputs:
            dict: {"status": "success"} if token deleted
                  {"status": "error", "reason": "Token not found"} if token doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Deletes token record from TOKENS table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Used for user logout
        """
        conn = self.pool.get_connection()
        try:
            sql = """DELETE FROM USER01.TOKENS WHERE ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, token)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "Token not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_user_id(self, token):
        """
        Retrieve user ID associated with an authentication token.
        
        Inputs:
            token (str): Authentication token
        
        Outputs:
            dict: {"status": "success", "output": list with USER_ID} if token valid
                  {"status": "error", "reason": "Token not found"} if token invalid
                  {"status": "error", "reason": str} on other failure
        
        Notes:
            Used to authenticate requests by verifying token validity
            Empty result indicates expired or invalid token
        """
        conn = self.pool.get_connection()
        try:
            sql = """SELECT USER_ID
                 FROM USER01.TOKENS WHERE ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, token)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            
            if results == []:
                return {"status": "error", "reason": "Token not found"}
            
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_token(self, email):
        """
        Retrieve authentication token for a user by email address.
        
        Inputs:
            email (str): User's email address
        
        Outputs:
            dict: {"status": "success", "output": list with token ID}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Joins TOKENS and USERS tables
            Returns empty list if user has no active tokens
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT USER01.TOKENS.ID
                        FROM USER01.TOKENS
                        JOIN USER01.USERS ON USER01.TOKENS.USER_ID = USER01.USERS.ID
                        WHERE USER01.USERS.EMAIL = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def update_user_data(self, user_id, email, password, fname, lname):
        """
        Update user profile information.
        
        Inputs:
            user_id (int): User's unique identifier
            email (str): New email address
            password (str): New hashed password
            fname (str): New first name
            lname (str): New last name
        
        Outputs:
            dict: {"status": "success"} if user updated
                  {"status": "error", "reason": "User not found"} if user doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Updates user record in USERS table
            Commits transaction on success, rolls back on failure
        """
        conn = self.pool.get_connection()
        try:
            sql = """ UPDATE USER01.USERS
                    SET EMAIL = ?, 
                    HASHED_PASSWORD = ?,
                    FIRST_NAME = ?,
                    LAST_NAME = ?
                    WHERE ID = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.bind_param(stmt, 3, fname)
            ibm_db.bind_param(stmt, 4, lname)
            ibm_db.bind_param(stmt, 5, user_id)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "User not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def add_address(self, user_id, full_name, line1, line2, city, region, postal_code, country_code, phone):
        """
        Add a new address for a user.
        
        Inputs:
            user_id (int): User's unique identifier
            full_name (str): Recipient's full name
            line1 (str): Address line 1
            line2 (str): Address line 2 (optional, can be empty)
            city (str): City name
            region (str): State/province/region
            postal_code (str): Postal/ZIP code
            country_code (str): ISO country code
            phone (str): Phone number
        
        Outputs:
            dict: {"status": "success"} on success
                  {"status": "error", "reason": str} on failure
        
        Side Effects:
            Inserts new address record in ADDRESSES table
            Commits transaction on success, rolls back on failure
        """
        conn = self.pool.get_connection()
        try:
            sql="""INSERT INTO USER01.ADDRESSES 
                (USER_ID, FULL_NAME, LINE1, LINE2, CITY, REGION, POSTAL_CODE, COUNTRY_CODE, PHONE) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user_id)
            ibm_db.bind_param(stmt,2,full_name)
            ibm_db.bind_param(stmt,3,line1)
            ibm_db.bind_param(stmt,4,line2)
            ibm_db.bind_param(stmt,5,city)
            ibm_db.bind_param(stmt,6,region)
            ibm_db.bind_param(stmt,7,postal_code)
            ibm_db.bind_param(stmt,8,country_code)
            ibm_db.bind_param(stmt,9,phone)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_address(self, address_id):
        """
        Retrieve a specific address by ID.
        
        Inputs:
            address_id (int): Address unique identifier
        
        Outputs:
            dict: {"status": "success", "output": list with address details}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Returns all address fields for the specified address ID
        """
        conn = self.pool.get_connection()
        try:
            sql = """
                SELECT 
                    ID,
                    FULL_NAME,
                    LINE1,
                    LINE2,
                    CITY,
                    REGION,
                    POSTAL_CODE,
                    COUNTRY_CODE,
                    PHONE
                FROM USER01.ADDRESSES
                WHERE ID = ?
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, address_id)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def delete_address(self, user_id, index):
        """
        Delete a specific address for a user.
        
        Inputs:
            user_id (int): User's unique identifier
            index (int): Address ID to delete
        
        Outputs:
            dict: {"status": "success"} if address deleted
                  {"status": "error", "reason": "Address not found"} if address doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Deletes address record from ADDRESSES table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Verifies both user_id and address_id match for security
        """
        conn = self.pool.get_connection()
        try:
            sql = """DELETE FROM USER01.ADDRESSES WHERE USER01.ADDRESSES.USER_ID = ? AND USER01.ADDRESSES.ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, user_id)
            ibm_db.bind_param(stmt, 2, index)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "Address not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)