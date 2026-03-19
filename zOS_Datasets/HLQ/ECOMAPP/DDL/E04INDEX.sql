--********************************************************************
--* MEMBER  : E04INDEX
--* PURPOSE : Create non-unique performance indexes for ECOMDB01 database
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-11
--*------------------------------------------------------------------
--* INSTRUCTIONS:
--*   Replace <Your HLQ> with your High Level Qualifier throughout
--*   this script before running.
--*------------------------------------------------------------------
--* NOTES:
--*   - Primary key and unique indexes already created in E03TABLE
--*   - Only additional access-path indexes listed here for
--*     performance optimization on SKU-based schema
--********************************************************************

-- ==============================================================
-- TOKENS: Look up tokens by user
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_TOKENS_USERID
    ON <Your HLQ>.TOKENS (USER_ID ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- STYLE_MODIFIERS: Find valid modifiers for a style
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_STYLMOD_STYLE
    ON <Your HLQ>.STYLE_MODIFIERS (STYLE_CODE ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- PRODUCT_TYPES: Find types by series or style
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_PRDTYP_SERIES
    ON <Your HLQ>.PRODUCT_TYPES (SERIES_CODE ASC)
    BUFFERPOOL BP0
    CLOSE NO;

CREATE INDEX <Your HLQ>.IX_PRDTYP_STYLE
    ON <Your HLQ>.PRODUCT_TYPES (STYLE_CODE ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- PRODUCT_VARIANTS: Find variants by type
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_PRDVAR_TYPE
    ON <Your HLQ>.PRODUCT_VARIANTS 
    (SERIES_CODE ASC, STYLE_CODE ASC, SERIAL_NUMBER ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- VARIANT_IMAGES: All images for a variant
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_VARIMG_VARIANT
    ON <Your HLQ>.VARIANT_IMAGES 
    (SERIES_CODE ASC, STYLE_CODE ASC, SERIAL_NUMBER ASC, 
     MODIFIER_CODE ASC, SORT_ORDER ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- INVENTORY: Find inventory by seller
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_INVTRY_SELLER
    ON <Your HLQ>.INVENTORY (SELLER_ID ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- INVENTORY: Find inventory by variant
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_INVTRY_VARIANT
    ON <Your HLQ>.INVENTORY 
    (SERIES_CODE ASC, STYLE_CODE ASC, SERIAL_NUMBER ASC, 
     MODIFIER_CODE ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- CARTS: Active/abandoned carts for a user
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_CARTS_USER_STATUS
    ON <Your HLQ>.CARTS (USER_ID ASC, STATUS ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- CART_ITEMS: All items in a cart
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_CRTITM_CART
    ON <Your HLQ>.CART_ITEMS (CART_ID ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- ADDRESSES: All addresses for a user
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_ADDR_USERID
    ON <Your HLQ>.ADDRESSES (USER_ID ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- ORDERS: Order history by user and date
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_ORDERS_USER_CREAT
    ON <Your HLQ>.ORDERS (USER_ID ASC, CREATED_AT DESC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- ORDER_ITEMS: All items for an order
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_ORDITM_ORDERID
    ON <Your HLQ>.ORDER_ITEMS (ORDER_ID ASC)
    BUFFERPOOL BP0
    CLOSE NO;

-- ==============================================================
-- ORDER_ITEMS: All items sold by a seller
-- ==============================================================
CREATE INDEX <Your HLQ>.IX_ORDITM_SELLERID
    ON <Your HLQ>.ORDER_ITEMS (SELLER_ID ASC, CREATED_AT DESC)
    BUFFERPOOL BP0
    CLOSE NO;

