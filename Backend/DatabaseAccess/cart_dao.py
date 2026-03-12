import os
import configparser
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
driver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = driver_path + ";" + os.environ.get("PATH", "")

import ibm_db

class CartDAO:
    def __init__(self, pool):
        self.pool = pool
    
    
'''
class CartDAO:
    def __init__(self, pool):
        self.pool = pool
    
    def add_item(self):
    
    def remove_item(self):

    def retrieve_cart(self):

    def remove_entire_cart(self):
        '''