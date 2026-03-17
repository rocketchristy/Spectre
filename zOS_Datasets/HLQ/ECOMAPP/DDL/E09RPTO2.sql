--********************************************************************
--* MEMBER  : E09RPTO2
--* PURPOSE : Generate per-item order summary report
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-17
--*------------------------------------------------------------------
--* INSTRUCTIONS:
--*   Replace <Your HLQ> with your High Level Qualifier throughout
--*   this script before running.
--*------------------------------------------------------------------
--* NOTES:
--*   - Report aggregates order items by product (SKU)
--*   - Shows total quantity sold and total revenue
--*   - Includes seller information for marketplace tracking
--*   - Sorted by total revenue (highest first)
--*   - Limited to last 90 days of order data
--********************************************************************

SELECT
    OI.SKU                     AS SKU,
    OI.PRODUCT_NAME            AS PRODUCT_NAME,
    U.EMAIL                    AS SELLER_EMAIL,
    U.FIRST_NAME               AS SELLER_FIRST_NAME,
    U.LAST_NAME                AS SELLER_LAST_NAME,
    COUNT(DISTINCT OI.ORDER_ID) AS ORDER_COUNT,
    SUM(OI.QUANTITY)           AS TOTAL_QUANTITY_SOLD,
    SUM(OI.TOTAL_CENTS)/100.00 AS TOTAL_REVENUE_USD,
    AVG(OI.UNIT_PRICE_CENTS)/100.00 AS AVG_UNIT_PRICE_USD,
    MIN(OI.UNIT_PRICE_CENTS)/100.00 AS MIN_UNIT_PRICE_USD,
    MAX(OI.UNIT_PRICE_CENTS)/100.00 AS MAX_UNIT_PRICE_USD
FROM <Your HLQ>.ORDER_ITEMS OI
JOIN <Your HLQ>.ORDERS O
    ON OI.ORDER_ID = O.ID
LEFT JOIN <Your HLQ>.USERS U
    ON OI.SELLER_ID = U.ID
WHERE O.CREATED_AT >= CURRENT TIMESTAMP - 90 DAYS
  AND O.STATUS NOT IN ('canceled', 'refunded')
GROUP BY OI.SKU, OI.PRODUCT_NAME, U.EMAIL, 
         U.FIRST_NAME, U.LAST_NAME
HAVING SUM(OI.QUANTITY) > 0
ORDER BY TOTAL_REVENUE_USD DESC, TOTAL_QUANTITY_SOLD DESC
FETCH FIRST 500 ROWS ONLY;

--********************************************************************
--* END OF E09RPTO2.sql
--********************************************************************
