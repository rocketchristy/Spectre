import os
import configparser
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
clidriver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")

import ibm_db

class UserDAO:
    def __init__(self, pool):
        self.pool = pool

    def add_user(self, email, password, first_name, last_name):
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
            return {"status": "success"}
        except Exception as e:
            error_code = ibm_db.conn_error(conn)
            error_msg = ibm_db.conn_errormsg(conn)
            if "SQLSTATE=23505" in str(e) or "SQLSTATE=23505" in error_msg:
                return {"status": "error", "reason": "Duplicate email"}
            else:
                return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_user(self, email):
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
        conn = self.pool.get_connection()
        try:
            sql = """
                SELECT 
<<<<<<< HEAD
=======
                    USER01.USERS.FIRST_NAME,
                    USER01.USERS.LAST_NAME,
>>>>>>> 2e30084cb21959f6159dc777f2ea6cfb16a0d124
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
        conn = self.pool.get_connection()
        try:
            sql="""INSERT INTO USER01.TOKENS (USER_ID) VALUES (?)"""
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user_id)
            ibm_db.execute(stmt)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def delete_token(self, token):
        conn = self.pool.get_connection()
        try:
            sql = """DELETE FROM USER01.TOKENS WHERE ID = (?)"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, token)
            ibm_db.execute(stmt)
<<<<<<< HEAD
            num_rows=ibm_db.num_rows(stmt)
            if num_rows == 0:
                return {"status": "error", "reason": "No token not found"}
            ibm_db.commit(conn)
=======
>>>>>>> 2e30084cb21959f6159dc777f2ea6cfb16a0d124
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_user_id(self, token):
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
            return {"status": "success", "output": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_token(self, email):
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
        conn = self.pool.get_connection()
        try:
            sql = """ UPDATE USER01.USERS
                    SET EMAIL = ?, 
                    HASHED_PASSWORD = ?,
                    FIRST_NAME = ?,
                    LAST_NAME = ?, 
                    WHERE ID = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.bind_param(stmt, 3, fname)
            ibm_db.bind_param(stmt, 4, lname)
            ibm_db.bind_param(stmt, 5, user_id)
            ibm_db.execute(stmt)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def add_address(self, user_id, full_name, line1, line2, city, region, postal_code, country_code, phone ):
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
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def delete_address(self, user_id, index):
        conn = self.pool.get_connection()
        try:
            sql = """DELETE FROM USER01.ADDRESSES WHERE USER01.ADDRESSES.USER_ID = ? AND USER01.ADDRESSES.ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, user_id)
            ibm_db.bind_param(stmt, 2, index)
            ibm_db.execute(stmt)
<<<<<<< HEAD
            num_rows=ibm_db.num_rows(stmt)
            if num_rows == 0:
                return {"status": "error", "reason": "No address not found"}
            ibm_db.commit(conn)
=======
>>>>>>> 2e30084cb21959f6159dc777f2ea6cfb16a0d124
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)