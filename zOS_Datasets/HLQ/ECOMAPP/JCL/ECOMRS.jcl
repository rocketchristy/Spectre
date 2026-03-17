//ECOMRS   JOB (ACCT-INFO),'ECOMAPP RUNSTATS',CLASS=A,MSGCLASS=7,
//             NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMRS
//* PURPOSE : Gather Db2 catalog statistics for ECOMDB01
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-11
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   1. Replace <Your SSID> with your Db2 subsystem ID (e.g., DSN1, DB2P)
//*   2. Replace <Your DB2HLQ> with your Db2 software HLQ (e.g., DSNV13)
//*   3. Update PARM value in RUNSTAT step to match your SSID
//*------------------------------------------------------------------
//* NOTES:
//*   - Run after initial data load and on regular schedule
//*   - Recommended: weekly minimum or after bulk load/delete of
//*     >= 20% of rows
//*   - Accurate statistics critical for optimizer access paths
//*------------------------------------------------------------------
//* PREREQS : ECOMDB01 exists (may be empty or contain data)
//* NEXT JOB: Optional REORG + REBUILD INDEX
//* ================================================================
//*
//JOBLIB   DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNEXIT
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.SDSNLOAD
//         DD  DISP=SHR,DSN=<Your DB2HLQ>.RUNLIB.LOAD
//*
//RUNSTAT  EXEC PGM=DSNUTILB,PARM='<Your SSID>,ECOMRS01'
//SYSPRINT DD  SYSOUT=*
//UTPRINT  DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSIN    DD  *
  RUNSTATS TABLESPACE ECOMDB01.TSUSERS1
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSTOKENS
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSSERIES
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSSTYLES
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSSTYLMD
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSPRDTYP
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSPRDVAR
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSVARIMG
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSINVTRY
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSCARTS1
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSCRTITM
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSADDR01
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSORDERS
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSORDADR
           TABLE(ALL) INDEX(ALL) REPORT YES
  RUNSTATS TABLESPACE ECOMDB01.TSORDITM
           TABLE(ALL) INDEX(ALL) REPORT YES
/*
//*