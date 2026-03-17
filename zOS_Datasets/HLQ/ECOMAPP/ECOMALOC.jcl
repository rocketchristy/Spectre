//ECOMALOC JOB (ACCT-INFO),'ECOMAPP ALLOC PDS',CLASS=A,MSGCLASS=7,
//             NOTIFY=&SYSUID
//*
//* ================================================================
//* JOB     : ECOMALOC
//* PURPOSE : Allocate PDS libraries for ECOMAPP project
//* AUTHOR  : Ben Edens
//* DATE    : 2026-03-11
//*------------------------------------------------------------------
//* INSTRUCTIONS:
//*   Replace <Your HLQ> in the SET HLQ statement below before
//*   submitting this job.
//*------------------------------------------------------------------
//* NOTES:
//*   - Run ONCE per environment (DEV/TEST/PROD)
//*   - Creates <Your HLQ>.ECOMAPP.DDL for SQL DDL source
//*   - Creates <Your HLQ>.ECOMAPP.JCL for JCL members
//*   - Creates <Your HLQ>.ECOMAPP.REPORTS for report output
//*   - After running, upload DDL/JCL members via Zowe or ISPF
//*------------------------------------------------------------------
//* PREREQS : None
//* NEXT JOB: Upload members, then submit ECOMDDL
//* ================================================================
//*
// SET HLQ=<Your HLQ>.ECOMAPP
//*
//********************************************************************
//* STEP 1 - Allocate three PDS libraries
//*           DDL/JCL: LRECL=80 standard card-image SQL/JCL
//*           REPORTS: LRECL=133 for DSNTEP3 report output
//*           BLKSIZE optimized for 3390 DASD
//*           SPACE: primary TRKs, secondary TRKs, directory blocks
//********************************************************************
//ALLPDS   EXEC PGM=IEFBR14
//DDL      DD  DSN=&HLQ..DDL,
//             DISP=(MOD,CATLG,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(150,20,20)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=3120,DSORG=PO)
//JCLPDS   DD  DSN=&HLQ..JCL,
//             DISP=(MOD,CATLG,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(15,5,10)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=3120,DSORG=PO)
//REPORTS  DD  DSN=&HLQ..REPORTS,
//             DISP=(MOD,CATLG,DELETE),
//             UNIT=SYSDA,
//             SPACE=(TRK,(50,10,10)),
//             DCB=(RECFM=FBA,LRECL=133,BLKSIZE=1330,DSORG=PO)
//*