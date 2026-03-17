//ECOMRPTS JOB (ACCT-INFO),'ECOMAPP REPORTS',CLASS=A,MSGCLASS=7,
//             REGION=0M,NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMRPTS
//* PURPOSE : Generate order history, sales, and database statistics
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-17
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your HLQ> in SET HLQ statement
//*   2. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   3. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*------------------------------------------------------------------
//* NOTES:
//*   - Executes three reports via DSNTEP3:
//*     RPT1 - Order history by day and user (last 90 days)
//*     RPT2 - Per-item order summaries (last 90 days)
//*     RPT3 - Database and table-level statistics
//*   - Each report runs in two steps: SQL execution + save to PDS
//*   - Report output saved to <Your HLQ>.ECOMAPP.REPORTS dataset
//*   - Run on-demand or schedule weekly/monthly as needed
//*------------------------------------------------------------------
//* PREREQS : ECOMALOC completed; REPORTS dataset exists
//* NEXT JOB: Review report output in <Your HLQ>.ECOMAPP.REPORTS
//* ================================================================
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
// SET SSID=<Your SSID>
// SET DB2LOAD=<Your DB2HLQ>.SDSNLOAD
// SET HLQ=<Your HLQ>.ECOMAPP
//*
//********************************************************************
//* STEP 1A - ORDER HISTORY BY DAY AND USER (RPT1) - RUN QUERY
//********************************************************************
//RPT1RUN  EXEC PGM=IKJEFT01,DYNAMNBR=20
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  DSN=&&RPT1OUT,
//             DISP=(NEW,PASS,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(10,5)),
//             DCB=(RECFM=FBA,LRECL=133,BLKSIZE=1330)
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E09RPTO1)
//*
//********************************************************************
//* STEP 1B - SAVE RPT1 OUTPUT TO REPORTS PDS
//********************************************************************
//RPT1SAVE EXEC PGM=IEBGENER,COND=(12,LT,RPT1RUN)
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN=&&RPT1OUT,DISP=(OLD,DELETE,DELETE)
//SYSUT2   DD  DSN=&HLQ..REPORTS(RPTO1),
//             DISP=OLD
//SYSIN    DD  DUMMY
//*
//********************************************************************
//* STEP 2A - PER-ITEM ORDER SUMMARIES (RPT2) - RUN QUERY
//********************************************************************
//RPT2RUN  EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,RPT1SAVE)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  DSN=&&RPT2OUT,
//             DISP=(NEW,PASS,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(10,5)),
//             DCB=(RECFM=FBA,LRECL=133,BLKSIZE=1330)
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E09RPTO2)
//*
//********************************************************************
//* STEP 2B - SAVE RPT2 OUTPUT TO REPORTS PDS
//********************************************************************
//RPT2SAVE EXEC PGM=IEBGENER,COND=(12,LT,RPT2RUN)
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN=&&RPT2OUT,DISP=(OLD,DELETE,DELETE)
//SYSUT2   DD  DSN=&HLQ..REPORTS(RPTO2),
//             DISP=OLD
//SYSIN    DD  DUMMY
//*
//********************************************************************
//* STEP 3A - DATABASE AND TABLE STATISTICS (RPT3) - RUN QUERY
//********************************************************************
//RPT3RUN  EXEC PGM=IKJEFT01,DYNAMNBR=20,
//             COND=(12,LT,RPT2SAVE)
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD  DSN=&&RPT3OUT,
//             DISP=(NEW,PASS,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(10,5)),
//             DCB=(RECFM=FBA,LRECL=133,BLKSIZE=1330)
//SYSUDUMP DD  SYSOUT=*
//SYSTSIN  DD  *
  DSN SYSTEM(<Your SSID>)
  RUN PROGRAM(DSNTEP3) PLAN(DSNTEP3)
  END
/*
//SYSIN    DD  DISP=SHR,DSN=&HLQ..DDL(E09RPTO3)
//*
//********************************************************************
//* STEP 3B - SAVE RPT3 OUTPUT TO REPORTS PDS
//********************************************************************
//RPT3SAVE EXEC PGM=IEBGENER,COND=(12,LT,RPT3RUN)
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN=&&RPT3OUT,DISP=(OLD,DELETE,DELETE)
//SYSUT2   DD  DSN=&HLQ..REPORTS(RPTO3),
//             DISP=OLD
//SYSIN    DD  DUMMY
//*
