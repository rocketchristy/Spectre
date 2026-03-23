import os
import configparser
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
clidriver_path=config['database']['clidriver_path']
os.add_dll_directory(f"{clidriver_path}/bin")
driver_path = f"{clidriver_path}/bin/amd64.VC12.CRT"
os.environ["PATH"] = driver_path + ";" + os.environ.get("PATH", "")

"""
================================================================================
File: orders_dao.py
Description: Order processing and management operations
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module handles all order-related database operations including creating
orders, adding order items, retrieving order history, updating order costs,
and managing order addresses. Works with ORDERS, ORDER_ITEMS, and 
ORDER_ADDRESSES tables in the IBM Db2 database.
================================================================================
"""

import ibm_db

class OrdersDAO:
    def __init__(self, pool):
        """
        Initialize OrdersDAO with connection pool.
        
        Inputs:
            pool (IBMDBConnectionPool): Database connection pool instance
        
        Outputs:
            None
        """
        self.pool = pool

    def get_user_orders(self, user_id):
        """
        Retrieve all orders for a user with item details.
        
        Inputs:
            user_id (int): User's unique identifier
        
        Outputs:
            dict: {"status": "success", "output": list of order dictionaries}
                  Each order contains: order details and associated order items
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Uses JOIN to combine ORDERS and ORDER_ITEMS tables
            Returns all orders for the user regardless of status
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT * FROM USER01.ORDERS
                     JOIN USER01.ORDER_ITEMS 
                     ON USER01.ORDERS.ID = USER01.ORDER_ITEMS.ORDER_ID
                     WHERE USER_ID =?
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
        """
        Create a new order for a user with address information.
        
        Inputs:
            user_id (int): User's unique identifier
            currency_code (str): ISO currency code (e.g., "USD")
            subtotal_cents (int): Order subtotal in cents
            billing_address_id (int): ID of billing address
            shipping_address_id (int): ID of shipping address
        
        Outputs:
            dict: {"status": "success"} if order created
                  {"status": "error", "reason": error_message} on failure
        
        Side Effects:
            Inserts new row into ORDERS table
            Sets TAX_CENTS, SHIPPING_CENTS, DISCOUNT_CENTS to 0
            Sets TOTAL_CENTS equal to subtotal_cents initially
            Commits transaction on success, rolls back on failure
        
        Notes:
            Tax and shipping calculations not yet implemented
            Use add_order_item() to add items to the order
            Use update_order_cost() to recalculate totals after adding items
        """
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

    def add_order_item(self, order_id, inventory_id, seller_id, 
                       sku, product_name, unit_price_cents,
                       currency_code, quantity):
        """
        Add an inventory item to an order with seller and product details.
        
        Inputs:
            order_id (int): Order's unique identifier
            inventory_id (int): Inventory item's unique identifier
            seller_id (int): Seller's user ID
            sku (str): Stock Keeping Unit (product identifier)
            product_name (str): Name of the product
            unit_price_cents (int): Price per unit in cents
            currency_code (str): ISO currency code (e.g., "USD")
            quantity (int): Number of units being ordered
        
        Outputs:
            dict: {"status": "success"} if item added to order
                  {"status": "error", "reason": error_message} on failure
        
        Side Effects:
            Inserts new row into ORDER_ITEMS table
            Calculates and stores TOTAL_CENTS (unit_price_cents * quantity)
            Commits transaction on success, rolls back on failure
        
        Notes:
            Does not validate inventory availability
            Use inventory_dao to check/update stock separately
            Total is calculated automatically from unit price and quantity
            After adding all items, call update_order_cost() to update order totals
        """

        conn = self.pool.get_connection()
        try:
            # Calculate total cents for this order item
            total_cents = unit_price_cents * quantity
            
            sql="""
                    INSERT INTO USER01.ORDER_ITEMS 
                        (ORDER_ID, INVENTORY_ID, SELLER_ID, 
                        SKU, PRODUCT_NAME, UNIT_PRICE_CENTS,
                        CURRENCY_CODE, QUANTITY, TOTAL_CENTS) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,order_id)
            ibm_db.bind_param(stmt,2,inventory_id)
            ibm_db.bind_param(stmt,3,seller_id)
            ibm_db.bind_param(stmt,4,sku)
            ibm_db.bind_param(stmt,5,product_name)
            ibm_db.bind_param(stmt,6,unit_price_cents)
            ibm_db.bind_param(stmt,7, currency_code)
            ibm_db.bind_param(stmt,8, quantity)
            ibm_db.bind_param(stmt,9, total_cents)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)

    def get_order_id(self, user_id):
        """
        Retrieve the most recent order ID for a user.
        
        Inputs:
            user_id (int): User's unique identifier
        
        Outputs:
            dict: {"status": "success", "output": [{"ID": order_id}]}
                  Returns list with single order ID dictionary
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            Returns only the most recent order (sorted by CREATED_AT DESC)
            Uses FETCH FIRST 1 ROW ONLY for DB2 compatibility
            Typically used after add_order() to get newly created order ID
        """
        conn = self.pool.get_connection()
        try:
            sql =  """
                    SELECT ID FROM USER01.ORDERS 
                    WHERE USER_ID = ?
                    ORDER BY CREATED_AT DESC
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
    
    def update_order_cost(self, cost, order_id):
        """
        Update the subtotal and total cost for an order.
        
        Inputs:
            cost (int): Total cost in cents
            order_id (int): Order's unique identifier
        
        Outputs:
            dict: {"status": "success"} if costs updated
                  {"status": "error", "reason": "Order not found"} if order_id invalid
                  {"status": "error", "reason": error_message} on other failure
        
        Side Effects:
            Updates SUBTOTAL_CENTS and TOTAL_CENTS in ORDERS table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Currently sets SUBTOTAL_CENTS and TOTAL_CENTS to same value
            Tax calculation not yet implemented
            Call after adding all order items to set final totals
        """
        conn = self.pool.get_connection()
        try:
            sql = """ UPDATE USER01.ORDERS
                    SET SUBTOTAL_CENTS = ?,
                        TOTAL_CENTS = ? 
                    WHERE ID = ?
                    """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, cost)
            ibm_db.bind_param(stmt, 2, cost)
            ibm_db.bind_param(stmt, 3, order_id)
            ibm_db.execute(stmt)
            num_rows = ibm_db.num_rows(stmt)
        
            if num_rows == 0:
                return {"status": "error", "reason": "Order not found"}
            
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)


    def check_address_in_order(self, address_id):
        """
        Check if a user address already exists in ORDER_ADDRESSES table.
        
        Inputs:
            address_id (int): Address unique identifier from ADDRESSES table
        
        Outputs:
            dict: {"status": "success", "output": [address_data]}
                  If address exists in ORDER_ADDRESSES, OA.ID will be populated
                  If address not in ORDER_ADDRESSES, OA.ID will be NULL
                  {"status": "error", "reason": error_message} on failure
        
        Notes:
            LEFT JOIN returns address data even if not in ORDER_ADDRESSES
            Matches on all address fields (name, lines, city, region, postal, country, phone)
            Used to avoid duplicate addresses in ORDER_ADDRESSES table
            If OA.ID is NULL, call add_order_address() to create copy
        """
        conn = self.pool.get_connection()
        try:
            sql =   """
            SELECT OA.ID, A.FULL_NAME,A.LINE1,A.LINE2,
            A.CITY,A.REGION,A.POSTAL_CODE,A.COUNTRY_CODE, A.PHONE
            FROM USER01.ADDRESSES AS A LEFT JOIN USER01.ORDER_ADDRESSES AS OA
            ON A.FULL_NAME = OA.FULL_NAME
            AND A.LINE1 = OA.LINE1
            AND A.LINE2 = OA.LINE2
            AND A.CITY = OA.CITY
            AND A.REGION = OA.REGION
            AND A.POSTAL_CODE = OA.POSTAL_CODE
            AND A.COUNTRY_CODE = OA.COUNTRY_CODE
            AND A.PHONE = A.PHONE
            WHERE A.ID = ?"""
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, address_id)
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

    def add_order_address(self, full_name, line1, line2,
                          city, region, postal_code, country_code,
                          phone):
        """
        Create a snapshot copy of an address in ORDER_ADDRESSES table.
        
        Inputs:
            full_name (str): Recipient's full name
            line1 (str): Address line 1 (street address)
            line2 (str): Address line 2 (apt/suite, optional)
            city (str): City name
            region (str): State/province/region
            postal_code (str): ZIP/postal code
            country_code (str): ISO country code
            phone (str): Contact phone number
        
        Outputs:
            dict: {"status": "success"} if address added
                  {"status": "error", "reason": error_message} on failure
        
        Side Effects:
            Inserts new row into ORDER_ADDRESSES table
            Commits transaction on success, rolls back on failure
        
        Notes:
            Creates immutable copy of shipping address for order record
            Preserves address even if user modifies/deletes original in ADDRESSES
            Use check_address_in_order() first to avoid duplicates
        """
        conn = self.pool.get_connection()
        try:
            sql="""
                    INSERT INTO USER01.ORDER_ADDRESSES 
                        (FULL_NAME, LINE1, LINE2,
                        CITY, REGION, POSTAL_CODE, COUNTRY_CODE,
                        PHONE) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,full_name)
            ibm_db.bind_param(stmt,2,line1)
            ibm_db.bind_param(stmt,3,line2)
            ibm_db.bind_param(stmt,4,city)
            ibm_db.bind_param(stmt,5,region)
            ibm_db.bind_param(stmt,6, postal_code)
            ibm_db.bind_param(stmt,7, country_code)
            ibm_db.bind_param(stmt,8, phone)
            ibm_db.execute(stmt)
            ibm_db.commit(conn)
            return {"status": "success"}
        except Exception as e:
            ibm_db.rollback(conn)
            return {"status": "error", "reason": str(e)}
        finally:
            self.pool.return_connection(conn)
       