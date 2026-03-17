--********************************************************************
--* MEMBER  : E09RPTO3
--* PURPOSE : Generate database and table-level statistics report
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
--*   - Report queries Db2 catalog tables for schema metadata
--*   - Shows table count, column count, row count per table
--*   - Includes tablespace and index information
--*   - Row counts from RUNSTATS (may be stale if not run recently)
--*   - Limited to ECOMDB01 database tables
--********************************************************************

SELECT
    T.DBNAME                  AS DATABASE_NAME,
    T.TSNAME                  AS TABLESPACE_NAME,
    T.NAME                    AS TABLE_NAME,
    T.TYPE                    AS TABLE_TYPE,
    T.STATUS                  AS TABLE_STATUS,
    COUNT(DISTINCT C.NAME)    AS COLUMN_COUNT,
    T.CARD                    AS ESTIMATED_ROW_COUNT,
    T.NPAGES                  AS NUM_PAGES,
    T.PCTPAGES                AS PCT_PAGES_USED,
    COUNT(DISTINCT IX.NAME)   AS INDEX_COUNT,
    T.CREATEDTS               AS CREATED_TIMESTAMP,
    T.ALTEREDTS               AS ALTERED_TIMESTAMP,
    CASE T.STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'C' THEN 'CHECK PENDING'
        WHEN 'L' THEN 'LOAD IN PROGRESS'
        WHEN 'R' THEN 'RESTRICTED'
        WHEN 'T' THEN 'TABLESPACE STOPPED'
        WHEN 'U' THEN 'UTILITY IN PROGRESS'
        ELSE T.STATUS
    END                       AS STATUS_DESCRIPTION
FROM SYSIBM.SYSTABLES T
LEFT JOIN SYSIBM.SYSCOLUMNS C
    ON T.CREATOR = C.TBCREATOR
    AND T.NAME = C.TBNAME
LEFT JOIN SYSIBM.SYSINDEXES IX
    ON T.CREATOR = IX.TBCREATOR
    AND T.NAME = IX.TBNAME
WHERE T.CREATOR = '<Your HLQ>'
  AND T.DBNAME = 'ECOMDB01'
  AND T.TYPE = 'T'
GROUP BY T.DBNAME, T.TSNAME, T.NAME, T.TYPE, T.STATUS,
         T.CARD, T.NPAGES, T.PCTPAGES, T.CREATEDTS, T.ALTEREDTS
ORDER BY T.NAME ASC;

--********************************************************************
--* SUMMARY STATISTICS
--********************************************************************

SELECT
    '<Your HLQ>'                      AS SCHEMA_NAME,
    'ECOMDB01'                        AS DATABASE_NAME,
    COUNT(DISTINCT T.NAME)            AS TOTAL_TABLES,
    COUNT(DISTINCT T.TSNAME)          AS TOTAL_TABLESPACES,
    COUNT(DISTINCT C.NAME)            AS TOTAL_COLUMNS,
    COUNT(DISTINCT IX.NAME)           AS TOTAL_INDEXES,
    SUM(T.CARD)                       AS TOTAL_ESTIMATED_ROWS,
    SUM(T.NPAGES)                     AS TOTAL_PAGES_USED
FROM SYSIBM.SYSTABLES T
LEFT JOIN SYSIBM.SYSCOLUMNS C
    ON T.CREATOR = C.TBCREATOR
    AND T.NAME = C.TBNAME
LEFT JOIN SYSIBM.SYSINDEXES IX
    ON T.CREATOR = IX.TBCREATOR
    AND T.NAME = IX.TBNAME
WHERE T.CREATOR = '<Your HLQ>'
  AND T.DBNAME = 'ECOMDB01'
  AND T.TYPE = 'T';

--********************************************************************
--* END OF E09RPTO3.sql
--********************************************************************
