"""
Class for accessing database with a simple ibm_db connection pool
"""
import os
import configparser
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
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

