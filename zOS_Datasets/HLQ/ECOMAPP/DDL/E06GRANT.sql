--********************************************************************
--* MEMBER  : E06GRANT
--* PURPOSE : Grant schema privileges for ECOMDB01 database
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-11
--*------------------------------------------------------------------
--* INSTRUCTIONS:
--*   1. Replace <Your HLQ> with your High Level Qualifier
--*   2. Replace <Your USERGRP> with the user ID or group that will
--*      access the application tables (may differ from HLQ)
--*------------------------------------------------------------------
--* NOTES:
--*   - <Your HLQ> owns all objects (schema = <Your HLQ>)
--*   - Grants schema management privileges to owner
--*   - Grants DML privileges (SELECT, INSERT, UPDATE, DELETE) to
--*     <Your USERGRP> for application runtime access
--********************************************************************

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.TOTAL_CENTS
    IS 'UNIT_PRICE_CENTS * QUANTITY. Stored for reporting.';


-- ====================================================================
-- SCHEMA OWNER GRANTS
-- ====================================================================
-- Grant schema management privileges to the owner for DDL operations
-- ====================================================================

GRANT CREATEIN, ALTERIN, DROPIN
    ON SCHEMA <Your HLQ>
    TO <Your HLQ>;

-- ====================================================================
-- APPLICATION USER GRANTS
-- ====================================================================
-- Grant DML privileges to application user/group for runtime access
-- Replace <Your USERGRP> with your application user ID or group
-- ====================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.USERS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.TOKENS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.SERIES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.STYLES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.STYLE_MODIFIERS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.PRODUCT_TYPES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.PRODUCT_TYPE_MODIFIERS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.PRODUCT_VARIANTS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.VARIANT_IMAGES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.INVENTORY TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.CARTS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.CART_ITEMS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.ADDRESSES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.ORDERS TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.ORDER_ADDRESSES TO <Your USERGRP>;
GRANT SELECT, INSERT, UPDATE, DELETE ON <Your HLQ>.ORDER_ITEMS TO <Your USERGRP>;

-- ====================================================================
-- END OF E06GRANT
-- ====================================================================

