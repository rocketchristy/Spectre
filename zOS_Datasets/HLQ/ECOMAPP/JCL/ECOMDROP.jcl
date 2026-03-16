//ECOMDROP JOB (ACCT-INFO),'ECOMAPP DROP',CLASS=A,MSGCLASS=7,
//             NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMDROP
//* PURPOSE : Drop all ECOMDB01 objects in reverse dependency order
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-11
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your HLQ> in SET AUTHID and DROP statements
//*   2. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   3. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*
//*   *** WARNING *** DESTRUCTIVE AND IRREVERSIBLE
//*   Run only in non-production unless authorized by DBA with
//*   confirmed backup/archive of all data.
//*------------------------------------------------------------------
//* NOTES:
//*   - Drops objects in safe order (children before parents)
//*   - Ensure no active connections to ECOMDB01 before running
//*------------------------------------------------------------------
//* PREREQS : No active connections to ECOMDB01
//* NEXT JOB: ECOMALOC + ECOMDDL to rebuild
//* ================================================================
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
// SET SSID=<Your SSID>
// SET DB2LOAD=<Your DB2HLQ>.SDSNLOAD
// SET AUTHID=<Your HLQ>
//*
//DROPIT   EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  *
  -- ============================================================
  -- STEP 1: Drop child/junction tables first (FK dependents)
  -- ============================================================
  DROP TABLE <Your HLQ>.ORDER_ITEMS;
  DROP TABLE <Your HLQ>.ORDER_ADDRESSES;
  DROP TABLE <Your HLQ>.ORDERS;
  DROP TABLE <Your HLQ>.CART_ITEMS;
  DROP TABLE <Your HLQ>.CARTS;
  DROP TABLE <Your HLQ>.INVENTORY;
  DROP TABLE <Your HLQ>.VARIANT_IMAGES;
  DROP TABLE <Your HLQ>.PRODUCT_VARIANTS;
  DROP TABLE <Your HLQ>.PRODUCT_TYPE_MODIFIERS;
  DROP TABLE <Your HLQ>.PRODUCT_TYPES;
  DROP TABLE <Your HLQ>.STYLE_MODIFIERS;
  DROP TABLE <Your HLQ>.STYLES;
  DROP TABLE <Your HLQ>.SERIES;

  -- ============================================================
  -- STEP 2: Drop remaining base tables
  -- ============================================================
  DROP TABLE <Your HLQ>.TOKENS;
  DROP TABLE <Your HLQ>.ADDRESSES;
  DROP TABLE <Your HLQ>.USERS;

  -- ============================================================
  -- STEP 3: Drop tablespaces (must be empty)
  -- ============================================================
  DROP TABLESPACE ECOMDB01.TSORDITM;
  DROP TABLESPACE ECOMDB01.TSORDADR;
  DROP TABLESPACE ECOMDB01.TSORDERS;
  DROP TABLESPACE ECOMDB01.TSADDR01;
  DROP TABLESPACE ECOMDB01.TSCRTITM;
  DROP TABLESPACE ECOMDB01.TSCARTS1;
  DROP TABLESPACE ECOMDB01.TSINVTRY;
  DROP TABLESPACE ECOMDB01.TSVARIMG;
  DROP TABLESPACE ECOMDB01.TSPRDVAR;
  DROP TABLESPACE ECOMDB01.TSPRDMOD;
  DROP TABLESPACE ECOMDB01.TSPRDTYP;
  DROP TABLESPACE ECOMDB01.TSSTYLMD;
  DROP TABLESPACE ECOMDB01.TSSTYLES;
  DROP TABLESPACE ECOMDB01.TSSERIES;
  DROP TABLESPACE ECOMDB01.TSTOKENS;
  DROP TABLESPACE ECOMDB01.TSUSERS1;

  -- ============================================================
  -- STEP 4: Drop database (must be completely empty)
  -- ============================================================
  DROP DATABASE ECOMDB01 RESTRICT;
/*
//*