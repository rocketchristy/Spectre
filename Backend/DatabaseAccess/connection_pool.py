"""
================================================================================
File: connection_pool.py
Description: IBM Db2 connection pool manager for efficient database connections
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module provides a connection pooling mechanism for IBM Db2 database 
connections using the ibm_db driver. It maintains a pool of reusable connections
to improve performance and resource management.
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
from queue import Queue


class IBMDBConnectionPool:
    """
    Connection pool manager for IBM Db2 database connections.
    
    This class manages a pool of database connections using a Queue to handle
    connection requests efficiently and prevent connection exhaustion.
    """
    
    def __init__(self, conn_str, pool_size=5):
        """
        Initialize the connection pool with a specified number of connections.
        
        Inputs:
            conn_str (str): IBM Db2 connection string containing database credentials
            pool_size (int): Number of connections to maintain in the pool (default: 5)
        
        Outputs:
            None
        
        Side Effects:
            Creates pool_size number of active database connections
        """
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = ibm_db.connect(conn_str, "", "")
            self.pool.put(conn)

    def get_connection(self):
        """
        Retrieve a connection from the pool.
        
        Inputs:
            None
        
        Outputs:
            conn: IBM Db2 connection object from the pool
        
        Notes:
            Blocks if no connections are available until one is returned
        """
        return self.pool.get()

    def return_connection(self, conn):
        """
        Return a connection back to the pool for reuse.
        
        Inputs:
            conn: IBM Db2 connection object to return to the pool
        
        Outputs:
            None
        
        Side Effects:
            Connection becomes available for other operations
        """
        self.pool.put(conn)

    def close_all(self):
        """
        Close all connections in the pool and clean up resources.
        
        Inputs:
            None
        
        Outputs:
            None
        
        Side Effects:
            All connections in the pool are closed
            Pool becomes empty and unusable
        """
        while not self.pool.empty():
            conn = self.pool.get()
            ibm_db.close(conn)

