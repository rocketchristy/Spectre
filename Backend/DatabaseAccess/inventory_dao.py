"""
================================================================================
File: inventory_dao.py
Description: Data Access Object for inventory management operations
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module provides database operations for inventory management including:
- Retrieving all available inventory
- Managing user-specific inventory
- Adding/updating/removing inventory items
- Getting detailed product SKU information
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


class InventoryDAO:
    """
    Data Access Object for Inventory table operations.
    
    Handles all database interactions related to product inventory including
    stock management, pricing, and product variant details.
    """
    
    def __init__(self, pool):
        """
        Initialize InventoryDAO with a database connection pool.
        
        Inputs:
            pool (IBMDBConnectionPool): Database connection pool instance
        
        Outputs:
            None
        """
        self.pool = pool

    def get_inventory(self):
        """
        Retrieve all available inventory items with complete product details.
        
        Inputs:
            None
        
        Outputs:
            dict: {"status": "success", "output": list of inventory items}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Returns only products that:
            - Have active inventory records (INNER JOIN on INVENTORY)
            - Are marked as active (IS_ACTIVE = 'Y')
            Includes SKU, product details, pricing, seller info, and images
            Uses multi-table JOIN for complete product information
        """
        conn = self.pool.get_connection()
        try:
            sql = """
            SELECT
                PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                PV.MODIFIER_CODE AS SKU,
                S.DESCRIPTION AS SERIES_NAME,
                ST.DESCRIPTION AS STYLE_NAME,
                PT.DESCRIPTION AS PRODUCT_NAME,
                SM.DESCRIPTION AS MODIFIER_NAME,
                PT.BASE_PRICE_CENTS,
                VI.URL,
                I.ID AS INVENTORY_ID,
                I.SELLER_ID,
                I.QUANTITY_AVAILABLE,
                I.UNIT_PRICE_CENTS,
                I.CURRENCY_CODE
            FROM USER01.PRODUCT_VARIANTS PV
            INNER JOIN USER01.PRODUCT_TYPES PT
                ON PV.SERIES_CODE = PT.SERIES_CODE
            AND PV.STYLE_CODE = PT.STYLE_CODE
            AND PV.SERIAL_NUMBER = PT.SERIAL_NUMBER
            INNER JOIN USER01.SERIES S
                ON PT.SERIES_CODE = S.CODE
            INNER JOIN USER01.STYLES ST
                ON PT.STYLE_CODE = ST.CODE
            INNER JOIN USER01.STYLE_MODIFIERS SM
                ON PV.STYLE_CODE = SM.STYLE_CODE
            AND PV.MODIFIER_CODE = SM.MODIFIER_CODE
            LEFT JOIN USER01.VARIANT_IMAGES VI
                ON PV.SERIES_CODE = VI.SERIES_CODE
            AND PV.STYLE_CODE = VI.STYLE_CODE
            AND PV.SERIAL_NUMBER = VI.SERIAL_NUMBER
            AND PV.MODIFIER_CODE = VI.MODIFIER_CODE
            INNER JOIN USER01.INVENTORY I
                ON PV.SERIES_CODE = I.SERIES_CODE
            AND PV.STYLE_CODE = I.STYLE_CODE
            AND PV.SERIAL_NUMBER = I.SERIAL_NUMBER
            AND PV.MODIFIER_CODE = I.MODIFIER_CODE
            WHERE PV.IS_ACTIVE = 'Y'
"""
            stmt = ibm_db.prepare(conn, sql)
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

    def get_user_inventory(self, user_id):
        """
        Retrieve all inventory items for a specific seller.
        
        Inputs:
            user_id (int): Seller's user ID
        
        Outputs:
            dict: {"status": "success", "output": list of seller's inventory}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Similar to get_inventory but filtered by seller ID
            Used for seller's inventory management page
        """
        conn = self.pool.get_connection()
        try:
            sql = """SELECT
                PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                PV.MODIFIER_CODE AS SKU,
                S.DESCRIPTION AS SERIES_NAME,
                ST.DESCRIPTION AS STYLE_NAME,
                PT.DESCRIPTION AS PRODUCT_NAME,
                SM.DESCRIPTION AS MODIFIER_NAME,
                PT.BASE_PRICE_CENTS,
                VI.URL,
                I.ID AS INVENTORY_ID,
                I.SELLER_ID,
                I.QUANTITY_AVAILABLE,
                I.UNIT_PRICE_CENTS,
                I.CURRENCY_CODE
            FROM USER01.PRODUCT_VARIANTS PV
            INNER JOIN USER01.PRODUCT_TYPES PT
                ON PV.SERIES_CODE = PT.SERIES_CODE
            AND PV.STYLE_CODE = PT.STYLE_CODE
            AND PV.SERIAL_NUMBER = PT.SERIAL_NUMBER
            INNER JOIN USER01.SERIES S
                ON PT.SERIES_CODE = S.CODE
            INNER JOIN USER01.STYLES ST
                ON PT.STYLE_CODE = ST.CODE
            INNER JOIN USER01.STYLE_MODIFIERS SM
                ON PV.STYLE_CODE = SM.STYLE_CODE
            AND PV.MODIFIER_CODE = SM.MODIFIER_CODE
            LEFT JOIN USER01.VARIANT_IMAGES VI
                ON PV.SERIES_CODE = VI.SERIES_CODE
            AND PV.STYLE_CODE = VI.STYLE_CODE
            AND PV.SERIAL_NUMBER = VI.SERIAL_NUMBER
            AND PV.MODIFIER_CODE = VI.MODIFIER_CODE
            LEFT JOIN USER01.INVENTORY I
                ON PV.SERIES_CODE = I.SERIES_CODE
            AND PV.STYLE_CODE = I.STYLE_CODE
            AND PV.SERIAL_NUMBER = I.SERIAL_NUMBER
            AND PV.MODIFIER_CODE = I.MODIFIER_CODE
            WHERE PV.IS_ACTIVE = 'Y'
            AND I.SELLER_ID = ?
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

    def get_sku_details(self, seller_id, series_code, style_code, serial_number, modifier_code):
        """
        Retrieve detailed information for a specific SKU from a specific seller.
        
        Inputs:
            seller_id (int): Seller's user ID
            series_code (str): Product series code (e.g., 'PC')
            style_code (str): Product style code (e.g., 'E001')
            serial_number (int): Product serial number
            modifier_code (str): Style modifier code (e.g., 'EHM')
        
        Outputs:
            dict: {"status": "success", "output": list with SKU details}
                  {"status": "error", "reason": str} on failure
        
        Notes:
            Returns complete product information including:
            - SKU, names, descriptions
            - Pricing (base and unit)
            - Inventory availability
            - Product images
            Used for checking if seller has specific product in stock
        """
        conn = self.pool.get_connection()
        try:
            sql = """ 
                    SELECT
                        PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                        PV.MODIFIER_CODE AS SKU,
                        S.DESCRIPTION AS SERIES_NAME,
                        ST.DESCRIPTION AS STYLE_NAME,
                        PT.DESCRIPTION AS PRODUCT_NAME,
                        SM.DESCRIPTION AS MODIFIER_NAME,
                        PT.BASE_PRICE_CENTS,
                        VI.URL,
                        I.ID AS INVENTORY_ID,
                        I.SELLER_ID,
                        I.QUANTITY_AVAILABLE,
                        I.UNIT_PRICE_CENTS,
                        I.CURRENCY_CODE
                    FROM USER01.PRODUCT_VARIANTS PV
                    INNER JOIN USER01.PRODUCT_TYPES PT
                        ON PV.SERIES_CODE = PT.SERIES_CODE
                    AND PV.STYLE_CODE = PT.STYLE_CODE
                    AND PV.SERIAL_NUMBER = PT.SERIAL_NUMBER
                    INNER JOIN USER01.SERIES S
                        ON PT.SERIES_CODE = S.CODE
                    INNER JOIN USER01.STYLES ST
                        ON PT.STYLE_CODE = ST.CODE
                    INNER JOIN USER01.STYLE_MODIFIERS SM
                        ON PV.STYLE_CODE = SM.STYLE_CODE
                    AND PV.MODIFIER_CODE = SM.MODIFIER_CODE
                    LEFT JOIN USER01.VARIANT_IMAGES VI
                        ON PV.SERIES_CODE = VI.SERIES_CODE
                    AND PV.STYLE_CODE = VI.STYLE_CODE
                    AND PV.SERIAL_NUMBER = VI.SERIAL_NUMBER
                    AND PV.MODIFIER_CODE = VI.MODIFIER_CODE
                    LEFT JOIN USER01.INVENTORY I
                        ON PV.SERIES_CODE = I.SERIES_CODE
                    AND PV.STYLE_CODE = I.STYLE_CODE
                    AND PV.SERIAL_NUMBER = I.SERIAL_NUMBER
                    AND PV.MODIFIER_CODE = I.MODIFIER_CODE
                    WHERE PV.IS_ACTIVE = 'Y'
                    AND PV.SERIES_CODE = ?
                    AND PV.STYLE_CODE = ?
                    AND PV.SERIAL_NUMBER = ?
                    AND PV.MODIFIER_CODE = ?
                    AND I.SELLER_ID = ?
 """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, series_code)
            ibm_db.bind_param(stmt, 2, style_code)
            ibm_db.bind_param(stmt, 3, serial_number)
            ibm_db.bind_param(stmt, 4, modifier_code)
            ibm_db.bind_param(stmt, 5, seller_id)
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

    def update_quantity(self, quantity, seller_id, series_code, style_code, serial_number, modifier_code):
        """
        Update the available quantity for a specific inventory item.
        
        Inputs:
            quantity (int): New quantity available
            seller_id (int): Seller's user ID
            series_code (str): Product series code
            style_code (str): Product style code
            serial_number (int): Product serial number
            modifier_code (str): Style modifier code
        
        Outputs:
            dict: {"status": "success"} if quantity updated
                  {"status": "error", "reason": "Inventory item not found"} if item doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Updates QUANTITY_AVAILABLE in INVENTORY table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Used for inventory adjustments and stock updates after sales
        """
        conn = self.pool.get_connection()
        try:
            sql = """ 
                    UPDATE USER01.INVENTORY
                    SET QUANTITY_AVAILABLE = ?
                    WHERE SELLER_ID = ?
                    AND SERIES_CODE = ?
                    AND STYLE_CODE = ?
                    AND SERIAL_NUMBER = ?
                    AND MODIFIER_CODE = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, quantity)
            ibm_db.bind_param(stmt, 2, seller_id)
            ibm_db.bind_param(stmt, 3, series_code)
            ibm_db.bind_param(stmt, 4, style_code)
            ibm_db.bind_param(stmt, 5, serial_number)
            ibm_db.bind_param(stmt, 6, modifier_code)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "Inventory item not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def add_inventory(self, seller_id, series_code, style_code, 
                      serial_number, modifier_code, quantity_available, 
                      unit_price_cents, currency_code):
        """
        Add a new inventory item for a seller.
        
        Inputs:
            seller_id (int): Seller's user ID
            series_code (str): Product series code
            style_code (str): Product style code
            serial_number (int): Product serial number
            modifier_code (str): Style modifier code
            quantity_available (int): Initial quantity in stock
            unit_price_cents (int): Price per unit in cents
            currency_code (str): Currency code (e.g., 'USD')
        
        Outputs:
            dict: {"status": "success"} on success
                  {"status": "error", "reason": str} on failure
        
        Side Effects:
            Inserts new inventory record in INVENTORY table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Product variant must already exist in PRODUCT_VARIANTS table
            Serial number should be integer (not string with leading zeros)
        """
        conn = self.pool.get_connection()
        try:
            sql="""
                    INSERT INTO USER01.INVENTORY
                        (SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER,
                        MODIFIER_CODE, QUANTITY_AVAILABLE, UNIT_PRICE_CENTS,
                        CURRENCY_CODE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,seller_id)
            ibm_db.bind_param(stmt,2,series_code)
            ibm_db.bind_param(stmt,3,style_code)
            ibm_db.bind_param(stmt,4,serial_number)
            ibm_db.bind_param(stmt,5,modifier_code)
            ibm_db.bind_param(stmt,6,quantity_available)
            ibm_db.bind_param(stmt,7,unit_price_cents)
            ibm_db.bind_param(stmt,8,currency_code)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def remove_inventory(self, seller_id, series_code, style_code, serial_number, modifier_code):
        """
        Delete an inventory item by SKU components.
        
        Inputs:
            seller_id (int): Seller's user ID
            series_code (str): Product series code
            style_code (str): Product style code
            serial_number (int): Product serial number
            modifier_code (str): Style modifier code
        
        Outputs:
            dict: {"status": "success"} if item deleted
                  {"status": "error", "reason": "Inventory item not found"} if item doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Deletes inventory record from INVENTORY table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Permanently removes inventory item
            Verifies seller_id for security
        """
        conn = self.pool.get_connection()
        try:
            sql = """
                DELETE FROM USER01.INVENTORY
                WHERE SELLER_ID = ?
                AND SERIES_CODE = ?
                AND STYLE_CODE = ?
                AND SERIAL_NUMBER = ?
                AND MODIFIER_CODE = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, seller_id)
            ibm_db.bind_param(stmt, 2, series_code)
            ibm_db.bind_param(stmt, 3, style_code)
            ibm_db.bind_param(stmt, 4, serial_number)
            ibm_db.bind_param(stmt, 5, modifier_code)
            ibm_db.execute(stmt)
            
            num_rows = ibm_db.num_rows(stmt)
            if num_rows == 0:
                return {"status": "error", "reason": "Inventory item not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)
    
    def remove_user_inventory(self, seller_id, inventory_id):
        """
        Mark an inventory item as out of stock (set quantity to 0).
        
        Inputs:
            seller_id (int): Seller's user ID
            inventory_id (int): Inventory item's unique identifier
        
        Outputs:
            dict: {"status": "success"} if quantity set to 0
                  {"status": "error", "reason": "Inventory item not found"} if item doesn't exist
                  {"status": "error", "reason": str} on other failure
        
        Side Effects:
            Sets QUANTITY_AVAILABLE to 0 in INVENTORY table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Soft delete - keeps record but marks as unavailable
            Verifies seller_id for security
            Item remains in database for historical records
        """
        conn = self.pool.get_connection()
        try:
            sql = """ 
                    UPDATE USER01.INVENTORY
                    SET QUANTITY_AVAILABLE = 0
                    WHERE ID = ?
                    AND SELLER_ID = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, inventory_id)
            ibm_db.bind_param(stmt, 2, seller_id)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "Inventory item not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)
    
'''
    def add_inventory(self, seller_id, series_code, style_code,
                    serial_number, modifier_code,
                    quantity_available,unit_price_cents, 
                     currency_code ):
        conn = self.pool.get_connection()
        try:
            #search for the card see if it matches person and then add
            # 
            sql = """INSERT INTO USER01.INVENTORY 
                    (SELLER_ID,SERIES_CODE,STYLE_CODE,SERIAL_NUMBER
                    MODIFIER_CODE,QUANTITY_AVAILABLE,
                    UNIT_PRICE_CENTS) 
                VALUES (?, ?, ?, ?)"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, seller_id)
            ibm_db.bind_param(stmt, 2, series_code)
            ibm_db.bind_param(stmt, 3, style_code)
            ibm_db.bind_param(stmt, 4, serial_number)
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

    def test(self):
        conn = self.pool.get_connection()
        try:
            sql = """SELECT I.SERIES_CODE || I.STYLE_CODE || I.SERIAL_NUMBER ||
                        I.MODIFIER_CODE AS FULL_SKU,
                        S.DESCRIPTION AS SERIES_NAME,
                        ST.DESCRIPTION AS STYLE_NAME,
                        PT.DESCRIPTION AS PRODUCT_NAME,
                        SM.DESCRIPTION AS CONDITION,
                        U.FIRST_NAME || ' ' || U.LAST_NAME AS SELLER_NAME,
                        I.QUANTITY_AVAILABLE AS QTY,
                        I.UNIT_PRICE_CENTS / 100.00 AS PRICE_USD,
                        (PT.BASE_PRICE_CENTS + PM.PRICE_DELTA_CENTS) / 100.00
                            AS MSRP_USD
                    FROM USER01.INVENTORY I
                    INNER JOIN USER01.USERS U ON I.SELLER_ID = U.ID
                    INNER JOIN USER01.SERIES S ON I.SERIES_CODE = S.CODE
                    INNER JOIN USER01.STYLES ST ON I.STYLE_CODE = ST.CODE
                    INNER JOIN USER01.PRODUCT_TYPES PT
                        ON I.SERIES_CODE = PT.SERIES_CODE
                    AND I.STYLE_CODE = PT.STYLE_CODE
                    AND I.SERIAL_NUMBER = PT.SERIAL_NUMBER
                    INNER JOIN USER01.PRODUCT_TYPE_MODIFIERS PM
                        ON I.SERIES_CODE = PM.SERIES_CODE
                    AND I.STYLE_CODE = PM.STYLE_CODE
                    AND I.SERIAL_NUMBER = PM.SERIAL_NUMBER
                    AND I.MODIFIER_CODE = PM.MODIFIER_CODE
                    JOIN USER01.STYLE_MODIFIERS SM
                        ON PM.STYLE_CODE = SM.STYLE_CODE
                        AND PM.MODIFIER_CODE = SM.MODIFIER_CODE
                    WHERE I.QUANTITY_AVAILABLE > 0
                    ORDER BY S.DESCRIPTION, ST.DESCRIPTION, PT.SERIAL_NUMBER,
                            PM.MODIFIER_CODE, I.UNIT_PRICE_CENTS;"""
            stmt = ibm_db.prepare(conn, sql)
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
'''
'''
class InventoryDAO:
    def __init__(self, pool):
        self.pool = pool

    def retrieve_all_items(self, parameters):

    def retrieve_item(self, parameters):

    def add_item(self, parameters):

    def remove_item(self):

    def update_item(self):
    '''