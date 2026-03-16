//ECOMINIT JOB (ACCT-INFO),'ECOMAPP INIT DATA',CLASS=A,MSGCLASS=7,
//             REGION=0M,NOTIFY=&SYSUID
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
//* ================================================================
//* JOB   : ECOMINIT
//* PURPOSE: Initialize ECOMDB01 with complete product catalog
//*          Executes E07INIT1 through E07INIT5 in sequence
//*
//*  EXECUTION:
//*    INIT1 - Series, Styles, Modifiers, Product Types (172 rows)
//*    INIT2 - Product Type Modifiers Part 1 (1,200 variants)
//*    INIT3 - Product Type Modifiers Part 2 (1,200 variants)
//*    INIT4 - Product Type Modifiers Part 3 (1,200 variants)
//*    INIT5 - Product Type Modifiers Part 4 + All Variants (1,224)
//*
//*  RETURN CODE BEHAVIOR:
//*    RC=0  : Complete success, all data loaded
//*    RC=4  : SQL warning (e.g., data truncation)
//*    RC=8  : SQL error (e.g., -803 duplicate key on re-run)
//*    RC=12+: Severe error - STOP
//*
//*  Each step uses COND=(12,LT,prevstep) which means:
//*    "Skip this step if previous step RC >= 12"
//*
//* ================================================================
//*  PREREQS : ECOMDDL must have completed (tables exist)
//*  NEXT JOB: ECOMRS (gather statistics after data load)
//* ================================================================
//*
//********************************************************************
//* STEP 1 - LOAD REFERENCE DATA (INIT1)
//********************************************************************
//INIT1    EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E07INIT1)
//*
//********************************************************************
//* STEP 2 - LOAD PRODUCT VARIANTS PART 1 (INIT2)
//********************************************************************
//INIT2    EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,INIT1)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E07INIT2)
//*
//********************************************************************
//* STEP 3 - LOAD PRODUCT VARIANTS PART 2 (INIT3)
//********************************************************************
//INIT3    EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,INIT2)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E07INIT3)
//*
//********************************************************************
//* STEP 4 - LOAD PRODUCT VARIANTS PART 3 (INIT4)
//********************************************************************
//INIT4    EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,INIT3)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E07INIT4)
//*
//********************************************************************
//* STEP 5 - LOAD PRODUCT VARIANTS PART 4 (INIT5)
//********************************************************************
//INIT5    EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,INIT4)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
/*
//SYSIN    DD  DISP=SHR,DSN=<Your HLQ>.ECOMAPP.DDL(E07INIT5)
//*

