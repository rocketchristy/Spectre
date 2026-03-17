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
    
    def create_cart(self, user_id):
        conn = self.pool.get_connection()
        try:
            sql = """
                    INSERT INTO USER01.CARTS (USER_ID)
                    VALUES ?
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, user_id)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            error_code = ibm_db.conn_error(conn)
            error_msg = ibm_db.conn_errormsg(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)


    def get_cart_id(self, user_id):
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT ID FROM USER01.CARTS WHERE USER_ID =?
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
   

    def get_cart(self, user_id):
        conn = self.pool.get_connection()
        try:
            sql =  """
                        SELECT
                            CI.ID AS CART_ITEM_ID,
                            CI.CART_ID,
                            CI.INVENTORY_ID,
                            CI.QUANTITY,
                            CI.UNIT_PRICE_CENTS,
                            CI.CURRENCY_CODE,
                            I.SERIES_CODE,
                            I.STYLE_CODE,
                            I.SERIAL_NUMBER,
                            I.MODIFIER_CODE,
                            I.SELLER_ID,
                            PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER ||
                            PV.MODIFIER_CODE AS SKU,
                            S.DESCRIPTION AS SERIES_NAME,
                            ST.DESCRIPTION AS STYLE_NAME,
                            PT.DESCRIPTION AS PRODUCT_NAME,
                            SM.DESCRIPTION AS MODIFIER_NAME,
                            VI.URL
                        FROM USER01.CARTS C
                        INNER JOIN USER01.CART_ITEMS CI
                            ON C.ID = CI.CART_ID
                        INNER JOIN USER01.INVENTORY I
                            ON CI.INVENTORY_ID = I.ID
                        INNER JOIN USER01.PRODUCT_VARIANTS PV
                            ON I.SERIES_CODE = PV.SERIES_CODE
                        AND I.STYLE_CODE = PV.STYLE_CODE
                        AND I.SERIAL_NUMBER = PV.SERIAL_NUMBER
                        AND I.MODIFIER_CODE = PV.MODIFIER_CODE
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
                        WHERE C.USER_ID = ?
                        AND C.STATUS = 'active';
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

    def add_item(self, cart_id, inventory_id, quantity, unit_price_cents, currency_code):
        conn = self.pool.get_connection()
        try:
            sql="""
                    INSERT INTO USER01.CART_ITEMS
                        (CART_ID, INVENTORY_ID, QUANTITY, UNIT_PRICE_CENTS,
                        CURRENCY_CODE)
                    VALUES (?, ?, ?, ?, ?)
                    """
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,cart_id )
            ibm_db.bind_param(stmt,2,inventory_id) 
            ibm_db.bind_param(stmt,3,quantity)
            ibm_db.bind_param(stmt,4,unit_price_cents)
            ibm_db.bind_param(stmt,5,currency_code)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def remove_item(self, cart_id, cart_item_id):
        conn = self.pool.get_connection()
        try:
            sql = """
                    DELETE FROM USER01.CART_ITEMS
                    WHERE CART_ID = ?
                    AND ID = ?
                 """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, cart_id)
            ibm_db.bind_param(stmt, 2, cart_item_id)
            ibm_db.execute(stmt)
            
            num_rows = ibm_db.num_rows(stmt)
            if num_rows == 0:
                return {"status": "error", "reason": "Cart item not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def remove_entire_cart(self, cart_id):
        conn = self.pool.get_connection()
        try:
            sql = """
                DELETE FROM USER01.CART_ITEMS
                WHERE CART_ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, cart_id)
            ibm_db.execute(stmt)
            
            num_rows = ibm_db.num_rows(stmt)
            if num_rows == 0:
                return {"status": "error", "reason": "Cart is already empty or doesn't exist"}
            
            ibm_db.commit(conn)
            return {"status": "success", "rows_deleted": num_rows}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

