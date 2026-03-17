//ECOMDDL  JOB (ACCT-INFO),'ECOMAPP DDL',CLASS=A,MSGCLASS=7,REGION=0M,
//             NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMDDL
//* PURPOSE : Execute all DDL members in dependency order
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-11
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your HLQ> in SET HLQ and SET AUTHID statements
//*   2. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   3. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*------------------------------------------------------------------
//* NOTES:
//*   - Executes via DSNTEP3 in strict dependency order
//*   - Each step conditioned on prior step RC < 12
//*   - RC=8 (e.g., -601 object exists) allows continuation
//*   - RC=12+ (severe errors) stops execution
//*   - Execution order: DATABASE → TABLESPACES → TABLES →
//*     INDEXES → COMMENTS → GRANTS
//*------------------------------------------------------------------
//* PREREQS : ECOMALOC completed; DDL members uploaded
//* NEXT JOB: ECOMLOAD or ECOMRS
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
//* ---------------------------------------------------------------
//* NOTE: This job uses DSNTEP3/PLAN(DSNTEP3) as bound on this site.
//*       Ensure AUTHID (<Your HLQ>) has EXECUTE on plan DSNTEP3.
//* ---------------------------------------------------------------
//*
//********************************************************************
//* STEP 1 - DATABASE CREATION
//********************************************************************
//STGDB    EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E01STGDB)
//*
//********************************************************************
//* STEP 2 - TABLESPACES
//* COND=(12,LT,STGDB) means skip if STGDB RC >= 12
//* RC=8 from SQLCODE -601 (already exists) is acceptable
//********************************************************************
//TBSPC    EXEC PGM=IKJEFT01,DYNAMNBR=20,COND=(12,LT,STGDB)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E02TBSPC)
//*
//********************************************************************
//* STEP 3 - BASE TABLES (PKs, FKs, CHECK constraints included)
//* COND=(12,LT,TBSPC) means skip if TBSPC RC >= 12
//* RC=8 from SQLCODE -601 (already exists) is acceptable
//********************************************************************
//TABLES   EXEC PGM=IKJEFT01,DYNAMNBR=20,COND=(12,LT,TBSPC)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E03TABLE)
//*
//********************************************************************
//* STEP 4 - NON-UNIQUE PERFORMANCE INDEXES
//* COND=(12,LT,TABLES) means skip if TABLES RC >= 12
//* RC=8 from SQLCODE -601 (already exists) is acceptable
//********************************************************************
//INDEXES  EXEC PGM=IKJEFT01,DYNAMNBR=20,COND=(12,LT,TABLES)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E04INDEX)
//*
//********************************************************************
//* STEP 5 - CATALOG COMMENTS
//* COND=(12,LT,INDEXES) means skip if INDEXES RC >= 12
//********************************************************************
//COMMENTS EXEC PGM=IKJEFT01,DYNAMNBR=20,COND=(12,LT,INDEXES)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E05CMNT)
//*
//********************************************************************
//* STEP 6 - DML GRANTS
//* COND=(12,LT,COMMENTS) means skip if COMMENTS RC >= 12
//********************************************************************
//GRANTS   EXEC PGM=IKJEFT01,DYNAMNBR=20,COND=(12,LT,COMMENTS)
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