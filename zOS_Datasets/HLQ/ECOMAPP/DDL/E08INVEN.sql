--********************************************************************
--* MEMBER  : E08INVEN
--* PURPOSE : Initialize INVENTORY table with mystery product stock
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-16
--*------------------------------------------------------------------
--* NOTES:
--*   Replace <Your HLQ> with your High Level Qualifier throughout
--*   1. Adds inventory for all 24 mystery products only
--*   2. Seller: Christy D (resolved via subquery on email)
--*   3. Mystery Singles: 30-60 units each @ base price $3.00
--*   4. Mystery Midis: 20-40 units each @ base price $5.00
--*   5. Mystery Packs: 10-25 units each @ base price $10.00
--*   6. All products use 'NIB' modifier (New In Box)
--*------------------------------------------------------------------
--* CRITICAL PREREQUISITES:
--*   1. E07INIT1 MUST have completed successfully (creates users)
--*   2. User 'christy@nxtcg.com' must exist in USERS table
--*   3. Product variants must exist (E07INIT2-5 completed)
--*
--* TROUBLESHOOTING:
--*   If you get SQLCODE -407 (NULL value error):
--*   - Run the validation query below to check if user exists
--*   - Ensure ECOMINIT job completed with RC=0
--*   - Verify: SELECT * FROM <Your HLQ>.USERS 
--*            WHERE EMAIL = 'christy@nxtcg.com';
--*
--* NEXT STEP    : None (optional data load)
--********************************************************************

-- ====================================================================
-- VALIDATION: Check if Christy D exists
-- This query will return 1 row if the user exists, 0 if not
-- If it returns 0, you must run ECOMINIT first!
-- ====================================================================

SELECT 
    COUNT(*) AS USER_EXISTS,
    'User christy@nxtcg.com found - OK to proceed' AS STATUS
FROM <Your HLQ>.USERS
WHERE EMAIL = 'christy@nxtcg.com'
HAVING COUNT(*) > 0
UNION ALL
SELECT 
    COUNT(*) AS USER_EXISTS,
    'ERROR: User not found - run ECOMINIT first!' AS STATUS
FROM <Your HLQ>.USERS
WHERE EMAIL = 'christy@nxtcg.com'
HAVING COUNT(*) = 0;

-- ====================================================================
-- SHADOW MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XS01', 'NIB', 45, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XS02', 'NIB', 35, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XS03', 'NIB', 18, 1000);

-- ====================================================================
-- WATER MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XW01', 'NIB', 52, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XW02', 'NIB', 28, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XW03', 'NIB', 22, 1000);

-- ====================================================================
-- FIRE MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XF01', 'NIB', 38, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XF02', 'NIB', 40, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XF03', 'NIB', 15, 1000);

-- ====================================================================
-- EARTH MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XE01', 'NIB', 60, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XE02', 'NIB', 22, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XE03', 'NIB', 25, 1000);

-- ====================================================================
-- GRASS MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XG01', 'NIB', 33, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XG02', 'NIB', 31, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XG03', 'NIB', 12, 1000);

-- ====================================================================
-- ICE MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XI01', 'NIB', 47, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XI02', 'NIB', 26, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XI03', 'NIB', 20, 1000);

-- ====================================================================
-- NEUTRAL MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XN01', 'NIB', 55, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XN02', 'NIB', 38, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XN03', 'NIB', 17, 1000);

-- ====================================================================
-- RAINBOW MYSTERY PRODUCTS
-- ====================================================================

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'S', 'XR01', 'NIB', 41, 300);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'M', 'XR02', 'NIB', 24, 500);

INSERT INTO <Your HLQ>.INVENTORY
(SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
 QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES ((SELECT ID FROM <Your HLQ>.USERS
         WHERE EMAIL = 'christy@nxtcg.com'),
        'NA', 'P', 'XR03', 'NIB', 23, 1000);

-- ====================================================================
-- END OF INVENTORY INITIALIZATION
-- Total: 24 inventory items added for Christy D (USER_ID=3)
-- Singles: 371 units total | Midis: 244 units total
-- Packs: 152 units total | Grand Total: 767 units
-- ====================================================================
