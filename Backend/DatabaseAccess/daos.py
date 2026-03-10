"""
Class for accessing database with a simple ibm_db connection pool
"""
import os
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
clidriver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")

import ibm_db
from queue import Queue

class IBMDBConnectionPool:
    def __init__(self, conn_str, pool_size=5):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = ibm_db.connect(conn_str, "", "")
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            ibm_db.close(conn)

class LoginDAO:
    def __init__(self, pool):
        self.pool = pool

    def get_user(self, username):
        conn = self.pool.get_connection()
        try:
            sql = "SELECT password FROM Q.Staff"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)
            results = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_assoc(stmt)
            return results
        finally:
            self.pool.return_connection(conn)

    def get_user_data(self, username):
        conn = self.pool.get_connection()
        try:
            sql = "SELECT * FROM Q.Staff WHERE ID = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, staff_id)
            ibm_db.execute(stmt)
            return ibm_db.fetch_assoc(stmt)
        finally:
            self.pool.return_connection(conn)
    
    def add_user(self, info):
    def update_user_info(self, username, info):

class InventoryDAO:
    def __init__(self, pool):
        self.pool = pool

    def retrieve_all_items(self, parameters):

    def retrieve_item(self, parameters):

    def add_item(self, parameters):

    def remove_item(self):

    
class CartDAO:
    def __init__(self, pool):
        self.pool = pool
    
    def add_item(self):
    
    def remove_item(self):

    def retrieve_cart(self):

    def remove_cart(self):


    
# Usage:
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
username=config['database']['username']
password = config['database']['password']

conn_str = (
    "DATABASE=HL02HL2D;"
    "HOSTNAME=192.168.54.250;"
    "PORT=3600;"
    "PROTOCOL=TCPIP;"
    f"UID={username};"
    f"PWD={password};"
)

pool = IBMDBConnectionPool(conn_str, pool_size=5)
staff_dao = InventoryDAO(pool)
all_staff = staff_dao.get_all_staff()
print(all_staff)
staff = staff_dao.get_staff_by_id(123)
pool.close_all()