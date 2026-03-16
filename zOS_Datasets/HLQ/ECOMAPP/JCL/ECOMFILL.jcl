//ECOMFILL JOB (ACCT-INFO),'ECOMAPP INVENTORY',CLASS=A,MSGCLASS=7,
//             REGION=0M,NOTIFY=&SYSUID
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
//* ================================================================
//* JOB   : ECOMFILL
//* PURPOSE: Initialize INVENTORY table with product stock
//*
//*  EXECUTION:
//*    Loads 24 inventory items for Christy D (resolved via 
//*        subquery on email)
//*    - 8 Mystery Singles (30-60 units each @ $3.00)
//*    - 8 Mystery Midis   (20-40 units each @ $5.00)
//*    - 8 Mystery Packs   (10-25 units each @ $10.00)
//*    Total: 767 units across all mystery products
//*
//*  RETURN CODE BEHAVIOR:
//*    RC=0  : Complete success, all inventory loaded
//*    RC=4  : SQL warning (e.g., data truncation)
//*    RC=8  : SQL error (e.g., -803 duplicate key on re-run)
//*    RC=12+: Severe error
//*
//* ================================================================
//*  PREREQS : ECOMDDL (tables exist)
//*            ECOMINIT (products and users exist)
//*  NEXT JOB: Optional - ECOMRS if statistics need refresh
//* ================================================================
//*
//********************************************************************
//* STEP 1 - LOAD INVENTORY DATA
//********************************************************************
//INVEN    EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E08INVEN)
//*
