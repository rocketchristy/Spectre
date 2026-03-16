//ECOMLOAD JOB (ACCT-INFO),'ECOMAPP LOAD DATA',CLASS=A,MSGCLASS=7,
//             REGION=0M,NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMLOAD
//* PURPOSE : Load sample test data into ECOMDB01 tables
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-12
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your HLQ> in SET HLQ and SET AUTHID statements
//*   2. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   3. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*------------------------------------------------------------------
//* NOTES:
//*   - Executes E07LOAD.sql with INSERT statements for all tables
//*   - Loads data in proper dependency order
//*   - Re-runnable; duplicate INSERTs will fail but job continues
//*------------------------------------------------------------------
//* PREREQS : ECOMDDL completed; all tables exist
//* NEXT JOB: ECOMRS
//* ================================================================
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
// SET SSID=<Your SSID>
// SET DB2LOAD=<Your DB2HLQ>.SDSNLOAD
// SET HLQ=<Your HLQ>.ECOMAPP
// SET AUTHID=<Your HLQ>
//*
//********************************************************************
//* STEP 1 - LOAD TEST DATA
//********************************************************************
//LOADDATA EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E07LOAD)
//*
