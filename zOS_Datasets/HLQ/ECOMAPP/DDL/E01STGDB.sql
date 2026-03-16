--********************************************************************
--* MEMBER  : E01STGDB
--* PURPOSE : Create ECOMDB01 database
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-11
--*------------------------------------------------------------------
--* INSTRUCTIONS:
--*   No changes needed. This script does not reference <Your HLQ>.
--*------------------------------------------------------------------
--* NOTES:
--*   - Creates the ECOMDB01 database using system default storage
--*   - BUFFERPOOL BP0 = default 4K pool for all tablespaces
--*   - CCSID UNICODE: all objects inherit Unicode encoding
--********************************************************************

CREATE DATABASE ECOMDB01
    BUFFERPOOL BP0
    INDEXBP    BP0
    CCSID      UNICODE;
