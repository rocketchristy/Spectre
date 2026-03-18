--********************************************************************
--* MEMBER  : E09RPTO1
--* PURPOSE : Generate order history report by day and user
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
--*   - Report groups orders by calendar day and user
--*   - Shows order count, total revenue in dollars
--*   - Sorted by date (most recent first), then by user email
--*   - Status field shows distribution of order statuses per day
--********************************************************************

SELECT
    DATE(O.CREATED_AT)        AS ORDER_DATE,
    U.EMAIL                   AS USER_EMAIL,
    U.FIRST_NAME              AS FIRST_NAME,
    U.LAST_NAME               AS LAST_NAME,
    COUNT(O.ID)               AS ORDER_COUNT,
    SUM(O.TOTAL_CENTS)/100.00 AS TOTAL_REVENUE_USD,
    SUM(CASE WHEN O.STATUS = 'pending'   THEN 1 ELSE 0 END) 
                              AS PENDING_ORDERS,
    SUM(CASE WHEN O.STATUS = 'confirmed' THEN 1 ELSE 0 END) 
                              AS CONFIRMED_ORDERS,
    SUM(CASE WHEN O.STATUS = 'fulfilled' THEN 1 ELSE 0 END) 
                              AS FULFILLED_ORDERS,
    SUM(CASE WHEN O.STATUS = 'canceled'  THEN 1 ELSE 0 END) 
                              AS CANCELED_ORDERS,
    SUM(CASE WHEN O.STATUS = 'refunded'  THEN 1 ELSE 0 END) 
                              AS REFUNDED_ORDERS
FROM <Your HLQ>.ORDERS O
LEFT JOIN <Your HLQ>.USERS U
    ON O.USER_ID = U.ID
WHERE O.CREATED_AT >= CURRENT TIMESTAMP - 90 DAYS
GROUP BY DATE(O.CREATED_AT), U.EMAIL, U.FIRST_NAME, U.LAST_NAME
ORDER BY ORDER_DATE DESC, USER_EMAIL ASC
FETCH FIRST 500 ROWS ONLY;

--********************************************************************
--* END OF E09RPTO1.sql
--********************************************************************
