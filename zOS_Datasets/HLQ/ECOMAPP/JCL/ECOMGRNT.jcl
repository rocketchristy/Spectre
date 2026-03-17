//ECOMGRNT JOB (ACCT-INFO),'ECOMAPP GRANTS',CLASS=A,MSGCLASS=7,
//             NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMGRNT
//* PURPOSE : Apply DML grants for ECOMDB01 objects
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-11
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your HLQ> in SET HLQ and SET AUTHID statements
//*   2. Replace <Your USERGRP> with the user ID or group for app access
//*   3. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   4. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*------------------------------------------------------------------
//* NOTES:
//*   - Standalone re-runnable grants job
//*   - Can be used after DROP/recreate without re-running full DDL
//*   - ECOMDDL also executes E06GRANT as final step
//*   - <Your USERGRP> receives SELECT, INSERT, UPDATE, DELETE on all tables
//*------------------------------------------------------------------
//* PREREQS : All ECOMDB01 tables exist (ECOMDDL completed)
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
//GRANT1   EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E06GRANT)
//*