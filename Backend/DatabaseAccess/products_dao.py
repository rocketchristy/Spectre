import os
import configparser
config = configparser.ConfigParser()
config.read('DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
clidriver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = clidriver_path + ";" + os.environ.get("PATH", "")

import ibm_db

class ProductsDAO:
    def __init__(self, pool):
        self.pool = pool
    def get_product_types(self):
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
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT SM.MODIFIER_CODE, 
                        SM.DESCRIPTION
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

