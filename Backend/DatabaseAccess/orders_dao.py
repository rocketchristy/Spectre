import os
import configparser
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
driver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = driver_path + ";" + os.environ.get("PATH", "")

import ibm_db

class OrdersDAO:
    def __init__(self,pool):
        self.pool = pool

    def get_user_orders(self, user_id):
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT * FROM USER01.ORDERS WHERE USER_ID =?
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

    def add_order(self, user_id, currency_code, subtotal_cents, 
                billing_address_id, shipping_address_id):
        conn = self.pool.get_connection()
        try:
            sql="""
                    INSERT INTO USER01.ORDERS
                        (USER_ID, CURRENCY_CODE, SUBTOTAL_CENTS, TAX_CENTS,
                        SHIPPING_CENTS, DISCOUNT_CENTS, TOTAL_CENTS,
                        BILLING_ADDRESS_ID, SHIPPING_ADDRESS_ID)
                    VALUES (?, ?, ?, 0, 0, 0, ?, ?, ?)"""
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user_id)
            ibm_db.bind_param(stmt,2,currency_code)
            ibm_db.bind_param(stmt,3,subtotal_cents)
            ibm_db.bind_param(stmt,4,subtotal_cents)
            ibm_db.bind_param(stmt,5,billing_address_id)
            ibm_db.bind_param(stmt,6,shipping_address_id)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def add_order_item(self, order_id, variant_id, product_id,
                    seller_user_id, sku, product_name, unit_price_cents)

        conn = self.pool.get_connection()
        try:
            sql="""
                    INSERT INTO USER01.ORDER_ITEMS 
                        (ORDER_ID, VARIANT_ID, PRODUCT_ID, 
                        SELLER_USER_ID, SKU, PRODUCT_NAME,
                        UNIT_PRICE_CENTS)
                    """
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,order_id)
            ibm_db.bind_param(stmt,2,variant_id)
            ibm_db.bind_param(stmt,3,product_id)
            ibm_db.bind_param(stmt,4,seller_user_id)
            ibm_db.bind_param(stmt,5,sku)
            ibm_db.bind_param(stmt,6,product_name)
            ibm_db.bind_param(stmt,7,unit_price_cents)
            ibm_db.bind_param(stmt,8, currency_code)
            ibm_db.bind_param(stmt,9, quantity)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_order_id(self, user_id):
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT ID FROM USER01.ORDERS 
                    WHERE USER_ID = ?
                    ORDER BY PLACED_AT DESC
                    FETCH FIRST 1 ROW ONLY
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
    