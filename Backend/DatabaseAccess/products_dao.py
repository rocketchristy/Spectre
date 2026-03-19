import os
import configparser
config = configparser.ConfigParser()
config.read('DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
clidriver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")

"""
================================================================================
File: products_dao.py
Description: Product catalog and variant management operations
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module handles all product catalog database operations including retrieving
product types, styles, modifiers, and specific product variants. Works with
PRODUCT_TYPES, PRODUCT_VARIANTS, SERIES, STYLES, STYLE_MODIFIERS, and 
VARIANT_IMAGES tables in the IBM Db2 database.
================================================================================
"""

import ibm_db

class ProductsDAO:
    def __init__(self, pool):
        """
        Initialize ProductsDAO with connection pool.
        
        Inputs:
            pool (IBMDBConnectionPool): Database connection pool instance
        
        Outputs:
            None
        """
        self.pool = pool
    def get_product_types(self):
        """
        Retrieve all product types with SKU, price, and description.
        
        Inputs:
            None
        
        Outputs:
            dict: {"status": "success", "output": list of product type dictionaries}
                  Each product contains: SKU (SERIES_CODE || STYLE_CODE || SERIAL_NUMBER),
                  BASE_PRICE_CENTS, and DESCRIPTION
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            SKU is constructed by concatenating series, style, and serial number codes
            Returns all product types without filtering
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT
                            PT.SERIES_CODE || PT.STYLE_CODE || PT.SERIAL_NUMBER,
                            PT.BASE_PRICE_CENTS,
                            PT.DESCRIPTION
                        FROM USER01.PRODUCT_TYPES PT
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
    def get_modifiers(self, style_code):
        """
        Retrieve active style modifiers for a specific product style.
        
        Inputs:
            style_code (str): Product style code identifier
        
        Outputs:
            dict: {"status": "success", "output": list of modifier dictionaries}
                  Each modifier contains: MODIFIER_CODE, DESCRIPTION, PRICE_MULTIPLIER
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Only returns active modifiers (IS_ACTIVE = 'Y')
            Price multiplier is used to calculate variant-specific pricing
            Common modifiers include colorways, special editions, etc.
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT SM.MODIFIER_CODE, 
                        SM.DESCRIPTION,
                        SM.PRICE_MULTIPLIER
                        FROM USER01.STYLE_MODIFIERS AS SM
                        WHERE SM.IS_ACTIVE = 'Y'AND
                        SM.STYLE_CODE = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, style_code)
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
    def get_products(self):
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT
                            PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                            PV.MODIFIER_CODE AS SKU,
                            S.DESCRIPTION AS SERIES_NAME,
                            ST.DESCRIPTION AS STYLE_NAME,
                            PT.DESCRIPTION AS PRODUCT_NAME,
                            SM.DESCRIPTION AS MODIFIER_NAME,
                            PT.BASE_PRICE_CENTS,
                            VI.URL
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
    '''
    def get_specific_product_set(self, series_code, style_code, serial_number):
        """
        Retrieve all variants of a specific product (all color/modifier options).
        
        Inputs:
            series_code (str): Product series code (e.g., brand/collection)
            style_code (str): Product style code
            serial_number (int): Product serial number
        
        Outputs:
            dict: {"status": "success", "output": list of variant dictionaries}
                  Each variant contains: SKU, SERIES_NAME, STYLE_NAME, PRODUCT_NAME,
                  MODIFIER_NAME, BASE_PRICE_CENTS, URL (image)
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Returns all active variants (IS_ACTIVE = 'Y') for a specific base product
            SKU is constructed from series, style, serial, and modifier codes
            Includes 5-table JOIN to get complete product information
            Left joins variant images (URL may be NULL if no image exists)
            Use this to show all color/edition options for a product
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT
                            PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                            PV.MODIFIER_CODE AS SKU,
                            S.DESCRIPTION AS SERIES_NAME,
                            ST.DESCRIPTION AS STYLE_NAME,
                            PT.DESCRIPTION AS PRODUCT_NAME,
                            SM.DESCRIPTION AS MODIFIER_NAME,
                            PT.BASE_PRICE_CENTS,
                            VI.URL
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
                        WHERE PV.IS_ACTIVE = 'Y'
                        AND PV.SERIES_CODE = ?
                        AND PV.STYLE_CODE = ?
                        AND PV.SERIAL_NUMBER = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, series_code)
            ibm_db.bind_param(stmt, 2, style_code)
            ibm_db.bind_param(stmt, 3, serial_number)
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

    def get_specific_product(self, series_code, style_code, serial_number, modifier_code):
        """
        Retrieve details for a specific product variant.
        
        Inputs:
            series_code (str): Product series code
            style_code (str): Product style code
            serial_number (int): Product serial number
            modifier_code (str): Variant modifier code (colorway/edition)
        
        Outputs:
            dict: {"status": "success", "output": [variant_dictionary]}
                  Variant contains: SKU, SERIES_NAME, STYLE_NAME, PRODUCT_NAME,
                  MODIFIER_NAME, BASE_PRICE_CENTS, URL (image)
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Returns single specific variant (exact SKU match)
            Only returns active variants (IS_ACTIVE = 'Y')
            Includes 5-table JOIN to get complete product information
            Left joins variant image (URL may be NULL)
            Use this to display product detail page for a specific variant
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT
                            PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                            PV.MODIFIER_CODE AS SKU,
                            S.DESCRIPTION AS SERIES_NAME,
                            ST.DESCRIPTION AS STYLE_NAME,
                            PT.DESCRIPTION AS PRODUCT_NAME,
                            SM.DESCRIPTION AS MODIFIER_NAME,
                            PT.BASE_PRICE_CENTS,
                            VI.URL
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
                        WHERE PV.IS_ACTIVE = 'Y'
                        AND PV.SERIES_CODE = ?
                        AND PV.STYLE_CODE = ?
                        AND PV.SERIAL_NUMBER = ?
                        AND PV.MODIFIER_CODE = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, series_code)
            ibm_db.bind_param(stmt, 2, style_code)
            ibm_db.bind_param(stmt, 3, serial_number)
            ibm_db.bind_param(stmt, 4, modifier_code)
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

    def get_product_variant_ids(self, sku):
        """
        Get database IDs for a product variant by SKU.
        
        Inputs:
            sku (str): Stock Keeping Unit (complete product identifier)
        
        Outputs:
            dict: {"status": "success", "output": [{"ID": variant_id, "PRODUCT_ID": product_id}]}
                  Returns variant ID and associated product ID
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Used to resolve SKU to database primary keys
            Required for inventory operations that need numeric IDs
            Returns empty list if SKU not found
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT ID, PRODUCT_ID FROM USER01.PRODUCT_VARIANTS 
                    WHERE SKU = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, sku)
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

