# ECOMAPP - E-Commerce Database for Db2 z/OS

**Author:** Ben Edens  
**Product:** ECOMAPP (E-Commerce Application)  
**Platform:** Db2 13 for z/OS  
**Date:** March 16, 2026

> **Note:** This documentation was created with AI assistance using GitHub Copilot.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Installation Instructions](#installation-instructions)
5. [Database Operations](#database-operations)
6. [SQL Query Examples](#sql-query-examples)
7. [Pricing Model](#pricing-model)
8. [Database Design](#database-design)
9. [Customization Guide](#customization-guide)
10. [Troubleshooting](#troubleshooting)

---

## Overview

ECOMAPP is a Db2 13 for z/OS database implementation for the NextGen America trading card e-commerce platform. This package includes all DDL (Data Definition Language) scripts and JCL (Job Control Language) jobs needed to create and initialize the product catalog database.

**Key Features:**
- Complete SKU-based product catalog (4,824 trading card variants)
- Multiplier-based dynamic pricing system
- 16 normalized tables with full referential integrity
- Performance indexes on all critical access paths
- Split initialization files for mainframe line length compliance
- Automated JCL for all database operations

**Product Catalog:**
- **80 Individual Cards** × 60 modifier combinations = 4,800 variants
- **24 Mystery Products** × 1 variant each = 24 variants
- **Total:** 4,824 sellable SKUs

**Database Components:**
- **Database:** ECOMDB01
- **Tablespaces:** 16 tablespaces (one per table for maximum flexibility)
- **Tables:** USERS, TOKENS, SERIES, STYLES, STYLE_MODIFIERS, PRODUCT_TYPES, PRODUCT_TYPE_MODIFIERS, PRODUCT_VARIANTS, VARIANT_IMAGES, INVENTORY, CARTS, CART_ITEMS, ADDRESSES, ORDERS, ORDER_ADDRESSES, ORDER_ITEMS
- **Indexes:** Primary key indexes + business key indexes
- **Sample Data:** 4,824 product variants with complete metadata

---

## Prerequisites

Before installing ECOMAPP, ensure you have:

1. **z/OS System Access**
   - TSO/ISPF access or Zowe CLI installed
   - RACF/ACF2/Top Secret security access

2. **Db2 Subsystem**
   - Db2 13 for z/OS (or compatible version)
   - Db2 subsystem ID (SSID) - e.g., DSN1, DB2P, HL2D
   - Db2 software library high-level qualifier - e.g., DSNV13, DSN.VD10

3. **User Privileges**
   - Authority to create datasets under your high-level qualifier (HLQ)
   - Db2 SYSADM or SYSCTRL authority (for database creation)
   - EXECUTE privilege on DSNTEP3 plan (Db2 sample program)

4. **Storage**
   - Approximately 100 tracks for DDL library
   - Approximately 50 tracks for JCL library
   - DASD storage for database tablespaces (estimated ~500 MB)

---

## Directory Structure

```
zOS_Datasets/
├── README.md                      (this file)
└── HLQ/
    └── ECOMAPP/
        ├── ECOMALOC.jcl          (Allocate PDS libraries - run first!)
        ├── DDL/                   (SQL Data Definition Language scripts)
        │   ├── E01STGDB.sql      (Create ECOMDB01 database)
        │   ├── E02TBSPC.sql      (Create 16 tablespaces)
        │   ├── E03TABLE.sql      (Create all tables with PKs/FKs)
        │   ├── E04INDEX.sql      (Create performance indexes)
        │   ├── E05CMNT.sql       (Add catalog comments)
        │   ├── E06GRANT.sql      (Grant privileges)
        │   ├── E07INIT1.sql      (Load reference data + initial users)
        │   ├── E07INIT2.sql      (Load Product-Modifier links part 1)
        │   ├── E07INIT3.sql      (Load Product Variants part 1)
        │   ├── E07INIT4.sql      (Load Product-Modifier links part 2)
        │   ├── E07INIT5.sql      (Load Product Variants part 2 + Mystery products)
        │   └── E08INVEN.sql      (Load mystery product inventory for seller)
        └── JCL/                   (Job Control Language jobs)
            ├── ECOMDDL.jcl       (Execute DDL pipeline: create database)
            ├── ECOMINIT.jcl      (Execute INIT pipeline: load product catalog + users)
            ├── ECOMFILL.jcl      (Load inventory: 767 units of mystery products)
            ├── ECOMDROP.jcl      (Drop all database objects)
            ├── ECOMGRNT.jcl      (Apply grants only)
            ├── ECOMLOAD.jcl      (Reserved for future test data)
            └── ECOMRS.jcl        (Run statistics)
```

**Note:** This directory structure mirrors the z/OS dataset hierarchy. Files must be uploaded to the mainframe as PDS members. ECOMALOC.jcl is located at the `HLQ/ECOMAPP/` level (not under `JCL/`) because it is the bootstrap job that creates the JCL and DDL datasets.

**Data Initialization Files:**
The product catalog is split across five E07INIT files to comply with mainframe 72-character line length limits:
- **E07INIT1:** Reference tables (1 series, 4 styles, 63 modifiers, 104 product types) + 5 initial users
- **E07INIT2-3:** Card product-modifier links (80 cards × 60 modifiers = 4,800 combinations)
- **E07INIT4-5:** Product variants (4,800 card variants + 24 mystery product variants = 4,824 total)
- **E08INVEN:** Inventory data (24 mystery product inventory items, 767 total units, seller: Christy D)

**Initial Users:**
E07INIT1 creates five starter accounts for testing:
- bryce@nxtcg.com - Bryce M
- ben@nxtcg.com - Ben E
- christy@nxtcg.com - Christy D (inventory seller)
- claire@nxtcg.com - Claire O
- jessalyn@nxtcg.com - Jessalyn H
- All users share the same hashed password for demo purposes

---

## Installation Instructions

### Step 1: Customize Placeholders

Before uploading any files, you **must** customize the following placeholders throughout all DDL and JCL files:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `<Your HLQ>` | Your z/OS High-Level Qualifier | `USER01`, `PROD01`, `DEVUSER` |
| `<Your USERGRP>` | Application user/group for DML access | `APPUSER`, `ECOMGRP`, `WEBAPP` |
| `<Your SSID>` | Db2 subsystem ID | `DSN1`, `DB2P`, `HL2D` |
| `<Your DB2HLQ>` | Db2 software library HLQ | `DSNV13`, `DSN.VD10`, `DB2V13` |

**Important Notes:**
- `<Your HLQ>` will be the schema owner and will own all database objects
- `<Your USERGRP>` will receive SELECT, INSERT, UPDATE, DELETE privileges for application runtime
- These can be the same user ID or different, depending on your security model

**Customization Methods:**

**Option A: Global Find/Replace (Recommended)**
Use your text editor to find and replace all placeholders across all files:
1. Open all DDL and JCL files in your editor
2. Find `<Your HLQ>` → Replace with your actual HLQ (e.g., `USER01`)
3. Find `<Your USERGRP>` → Replace with your application user (e.g., `APPUSER`)
4. Find `<Your SSID>` → Replace with your Db2 subsystem ID (e.g., `HL2D`)
5. Find `<Your DB2HLQ>` → Replace with your Db2 software HLQ (e.g., `DSN.VD10`)
6. Save all files

**Option B: Manual Edit**
Edit each file individually, replacing placeholders as you encounter them.

---

### Step 2: Create Initial PDS for ECOMALOC

You need to manually create one dataset and upload the ECOMALOC.jcl file to it. This job will then create the remaining datasets.

**Method A: Using TSO/ISPF**

1. **Log into TSO/ISPF**
   - Option 3.2 (Dataset Utility)

2. **Allocate the Initial PDS**
   ```
   Command ===> A
   Dataset Name: <Your HLQ>.ECOMAPP.ECOMALOC
   Management class . . . <blank>
   Storage class  . . . . <blank>
   Volume serial  . . . . <blank>
   Device type  . . . . . <blank or SYSDA>
   Data class . . . . . . <blank>
   Space units  . . . . . TRKS
   Primary quantity . . . 5
   Secondary quantity . . 2
   Directory blocks . . . 2
   Record format  . . . . FB
   Record length  . . . . 80
   Block size . . . . . . 3120
   Data set name type . . PDS
   ```

3. **Upload ECOMALOC.jcl**
   - Option 3.4 (DSLIST)
   - Navigate to `<Your HLQ>.ECOMAPP.ECOMALOC`
   - Press Enter to browse
   - Type `EDIT` on command line
   - Use option 1 (View) or 2 (Edit) on the ECOMALOC member
   - Copy/paste the contents of `HLQ/ECOMAPP/ECOMALOC.jcl` from this package
   - Save (F3)

**Method B: Using Zowe CLI**

```bash
# Create the initial PDS
zowe files create data-set-classic "<Your HLQ>.ECOMAPP.ECOMALOC" \
  --data-set-type PDS \
  --primary-space 5 \
  --secondary-space 2 \
  --directory-blocks 2 \
  --record-format FB \
  --record-length 80 \
  --block-size 3120

# Upload ECOMALOC.jcl as a member
zowe files upload file-to-data-set "HLQ/ECOMAPP/ECOMALOC.jcl" \
  "<Your HLQ>.ECOMAPP.ECOMALOC(ECOMALOC)"
```

---

### Step 3: Run ECOMALOC to Create DDL and JCL Libraries

This job creates the two main PDS libraries for your DDL and JCL files.

**What ECOMALOC Does:**
- Creates `<Your HLQ>.ECOMAPP.DDL` (for SQL scripts)
- Creates `<Your HLQ>.ECOMAPP.JCL` (for JCL jobs)

**To Submit:**

**Method A: TSO/ISPF**
1. Option 3.4 (DSLIST)
2. Navigate to `<Your HLQ>.ECOMAPP.ECOMALOC`
3. Type `SUB` next to ECOMALOC member
4. Press Enter

**Method B: Zowe CLI**
```bash
zowe jobs submit data-set "<Your HLQ>.ECOMAPP.ECOMALOC(ECOMALOC)"
```

**Expected Result:**
- Job should complete with RC=0
- Two new datasets created:
  - `<Your HLQ>.ECOMAPP.DDL`
  - `<Your HLQ>.ECOMAPP.JCL`

**Verify:**
```
TSO/ISPF Option 3.4
Filter: <Your HLQ>.ECOMAPP.*

You should see:
<Your HLQ>.ECOMAPP.DDL
<Your HLQ>.ECOMAPP.ECOMALOC
<Your HLQ>.ECOMAPP.JCL
```

---

### Step 4: Upload DDL Members

Upload all SQL DDL files to the `<Your HLQ>.ECOMAPP.DDL` library.

**Method A: TSO/ISPF**
1. Option 3.4 (DSLIST)
2. Navigate to `<Your HLQ>.ECOMAPP.DDL`
3. Press Enter to browse
4. For each DDL file, create a new member:
   - Type `E <membername>` (e.g., `E E01STGDB`)
   - Copy/paste the contents from the DDL/ directory
   - Save (F3)

**Upload these members (in order):**
- E01STGDB (from HLQ/ECOMAPP/DDL/E01STGDB.sql)
- E02TBSPC (from HLQ/ECOMAPP/DDL/E02TBSPC.sql)
- E03TABLE (from HLQ/ECOMAPP/DDL/E03TABLE.sql)
- E04INDEX (from HLQ/ECOMAPP/DDL/E04INDEX.sql)
- E05CMNT (from HLQ/ECOMAPP/DDL/E05CMNT.sql)
- E06GRANT (from HLQ/ECOMAPP/DDL/E06GRANT.sql)
- E07INIT1 (from HLQ/ECOMAPP/DDL/E07INIT1.sql)
- E07INIT2 (from HLQ/ECOMAPP/DDL/E07INIT2.sql)
- E07INIT3 (from HLQ/ECOMAPP/DDL/E07INIT3.sql)
- E07INIT4 (from HLQ/ECOMAPP/DDL/E07INIT4.sql)
- E07INIT5 (from HLQ/ECOMAPP/DDL/E07INIT5.sql)

**Method B: Zowe CLI**
```bash
# Upload all DDL files
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E01STGDB.sql" "<Your HLQ>.ECOMAPP.DDL(E01STGDB)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E02TBSPC.sql" "<Your HLQ>.ECOMAPP.DDL(E02TBSPC)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E03TABLE.sql" "<Your HLQ>.ECOMAPP.DDL(E03TABLE)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E04INDEX.sql" "<Your HLQ>.ECOMAPP.DDL(E04INDEX)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E05CMNT.sql" "<Your HLQ>.ECOMAPP.DDL(E05CMNT)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E06GRANT.sql" "<Your HLQ>.ECOMAPP.DDL(E06GRANT)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E07INIT1.sql" "<Your HLQ>.ECOMAPP.DDL(E07INIT1)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E07INIT2.sql" "<Your HLQ>.ECOMAPP.DDL(E07INIT2)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E07INIT3.sql" "<Your HLQ>.ECOMAPP.DDL(E07INIT3)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E07INIT4.sql" "<Your HLQ>.ECOMAPP.DDL(E07INIT4)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E07INIT5.sql" "<Your HLQ>.ECOMAPP.DDL(E07INIT5)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/E08INVEN.sql" "<Your HLQ>.ECOMAPP.DDL(E08INVEN)"
```

**Method C: Batch Upload Script (PowerShell)**
```powershell
# Upload all DDL files at once
$hlq = "<Your HLQ>"  # Change to your HLQ
$ddlFiles = @("E01STGDB", "E02TBSPC", "E03TABLE", "E04INDEX", "E05CMNT", "E06GRANT", 
              "E07INIT1", "E07INIT2", "E07INIT3", "E07INIT4", "E07INIT5", "E08INVEN")

foreach ($file in $ddlFiles) {
    zowe files upload file-to-data-set "HLQ/ECOMAPP/DDL/$file.sql" "$hlq.ECOMAPP.DDL($file)"
    Write-Host "Uploaded $file"
}
```

---

### Step 5: Upload JCL Members

Upload all JCL job files to the `<Your HLQ>.ECOMAPP.JCL` library.

**Method A: TSO/ISPF**
1. Option 3.4 (DSLIST)
2. Navigate to `<Your HLQ>.ECOMAPP.JCL`
3. Press Enter to browse
4. For each JCL file, create a new member:
   - Type `E <membername>` (e.g., `E ECOMDDL`)
   - Copy/paste the contents from the JCL/ directory
   - Save (F3)

**Upload these members:**
- ECOMDDL (from HLQ/ECOMAPP/JCL/ECOMDDL.jcl)
- ECOMINIT (from HLQ/ECOMAPP/JCL/ECOMINIT.jcl)
- ECOMFILL (from HLQ/ECOMAPP/JCL/ECOMFILL.jcl)
- ECOMDROP (from HLQ/ECOMAPP/JCL/ECOMDROP.jcl)
- ECOMGRNT (from HLQ/ECOMAPP/JCL/ECOMGRNT.jcl)
- ECOMLOAD (from HLQ/ECOMAPP/JCL/ECOMLOAD.jcl)
- ECOMRS (from HLQ/ECOMAPP/JCL/ECOMRS.jcl)

**Method B: Zowe CLI**
```bash
# Upload all JCL files
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMDDL.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMDDL)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMINIT.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMINIT)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMFILL.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMFILL)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMDROP.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMDROP)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMGRNT.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMGRNT)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMLOAD.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMLOAD)"
zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/ECOMRS.jcl" "<Your HLQ>.ECOMAPP.JCL(ECOMRS)"
```

**Method C: Batch Upload Script (PowerShell)**
```powershell
# Upload all JCL files at once
$hlq = "<Your HLQ>"  # Change to your HLQ
$jclFiles = @("ECOMDDL", "ECOMINIT", "ECOMFILL", "ECOMDROP", "ECOMGRNT", "ECOMLOAD", "ECOMRS")

foreach ($file in $jclFiles) {
    zowe files upload file-to-data-set "HLQ/ECOMAPP/JCL/$file.jcl" "$hlq.ECOMAPP.JCL($file)"
    Write-Host "Uploaded $file"
}
```

---

### Step 6: Create the Database

Now you're ready to create the ECOMAPP database!

**Submit ECOMDDL Job:**

**Method A: TSO/ISPF**
1. Option 3.4 (DSLIST)
2. Navigate to `<Your HLQ>.ECOMAPP.JCL`
3. Type `SUB` next to ECOMDDL member
4. Press Enter

**Method B: Zowe CLI**
```bash
zowe jobs submit data-set "<Your HLQ>.ECOMAPP.JCL(ECOMDDL)"
```

**What ECOMDDL Does:**
This job executes the complete DDL pipeline in dependency order:

1. **STGDB Step** - Creates ECOMDB01 database (E01STGDB)
2. **TBSPC Step** - Creates 16 tablespaces (E02TBSPC)
3. **TABLES Step** - Creates all tables with PKs, FKs, constraints (E03TABLE)
4. **INDEXES Step** - Creates performance indexes (E04INDEX)
5. **COMMENTS Step** - Adds catalog comments (E05CMNT)
6. **GRANTS Step** - Grants privileges to owner and application user (E06GRANT)

**Expected Return Codes:**
- **RC=0**: Complete success - all DDL executed successfully
- **RC=4**: Warning (e.g., data truncation) - generally safe to continue
- **RC=8**: SQL error (e.g., -601 object already exists on re-run) - review SYSTSPRT
- **RC=12+**: Severe error (plan not found, authorization failure) - STOP and investigate

**Job Conditioning:**
Each step is conditioned on the previous step completing with RC < 12. This means:
- RC=8 (e.g., object already exists) allows the job to continue
- RC=12+ stops the job immediately

**Verify Database Creation:**

**Method A: TSO/ISPF with Db2I**
```
Option ==> D (Db2I Primary Menu)
Option ==> 2 (SPUFI)

Enter SQL:
SELECT * FROM SYSIBM.SYSTABLES WHERE CREATOR = '<Your HLQ>';

You should see 16 tables:
USERS, TOKENS, SERIES, STYLES, STYLE_MODIFIERS, PRODUCT_TYPES,
PRODUCT_TYPE_MODIFIERS, PRODUCT_VARIANTS, VARIANT_IMAGES,
INVENTORY, CARTS, CART_ITEMS, ADDRESSES, ORDERS,
ORDER_ADDRESSES, ORDER_ITEMS
```

**Method B: Db2 Command**
```
-DIS DATABASE(ECOMDB01) SPACENAM(*)

Should show all 16 tablespaces in RW (read-write) status
```

---

### Step 7: Initialize Product Catalog

After creating the database structure, initialize it with the NextGen America trading card catalog (4,824 product variants).

**Submit ECOMINIT Job:**

**Method A: TSO/ISPF**
1. Navigate to `<Your HLQ>.ECOMAPP.JCL`
2. Type `SUB` next to ECOMINIT member

**Method B: Zowe CLI**
```bash
zowe jobs submit data-set "<Your HLQ>.ECOMAPP.JCL(ECOMINIT)"
```

**What ECOMINIT Does:**
Executes E07INIT1 through E07INIT5 in sequence to populate the product catalog:

1. **INIT1 Step** - Loads reference data (E07INIT1):
   - 1 Series (NextGen America)
   - 4 Styles (Card Single, Mystery Single, Mystery Midi, Mystery Pack)
   - 63 Style Modifiers (language, foil, condition combinations + NIB)
   - 104 Product Types (80 cards + 24 mystery products)

2. **INIT2 Step** - Links cards to modifiers part 1 (E07INIT2):
   - ~2,400 PRODUCT_TYPE_MODIFIERS rows

3. **INIT3 Step** - Creates product variants part 1 (E07INIT3):
   - ~2,400 PRODUCT_VARIANTS rows

4. **INIT4 Step** - Links cards to modifiers part 2 (E07INIT4):
   - ~2,400 PRODUCT_TYPE_MODIFIERS rows

5. **INIT5 Step** - Creates product variants part 2 + mystery products (E07INIT5):
   - ~2,424 PRODUCT_VARIANTS rows (includes 24 mystery product variants)

**Expected Return Codes:**
- **RC=0**: Complete success - all 4,824 product variants loaded
- **RC=4**: Warning (e.g., data truncation) - generally safe to continue
- **RC=8**: SQL error (e.g., -803 duplicate key on re-run) - review SYSTSPRT
- **RC=12+**: Severe error (plan not found, authorization failure) - STOP and investigate

**Job Conditioning:**
Each step is conditioned on the previous step completing with RC < 12. This means:
- RC=8 (e.g., duplicate key) allows the job to continue to next step
- RC=12+ stops the job immediately

**Verify Data Load:**
```sql
-- Check catalog summary
SELECT 
    (SELECT COUNT(*) FROM <Your HLQ>.SERIES) AS SERIES_COUNT,
    (SELECT COUNT(*) FROM <Your HLQ>.STYLES) AS STYLES_COUNT,
    (SELECT COUNT(*) FROM <Your HLQ>.STYLE_MODIFIERS) AS MODIFIERS_COUNT,
    (SELECT COUNT(*) FROM <Your HLQ>.PRODUCT_TYPES) AS PRODUCT_TYPES_COUNT,
    (SELECT COUNT(*) FROM <Your HLQ>.PRODUCT_TYPE_MODIFIERS) AS PTM_COUNT,
    (SELECT COUNT(*) FROM <Your HLQ>.PRODUCT_VARIANTS) AS VARIANTS_COUNT
FROM SYSIBM.SYSDUMMY1;

Expected results:
SERIES: 1
STYLES: 4  
MODIFIERS: 63
PRODUCT_TYPES: 104
PTM: 4,800
VARIANTS: 4,824
```

---

### Step 8: Gather Statistics (Recommended)

After creating the database (and loading data if applicable), run statistics for optimal query performance:

**Submit ECOMRS Job:**

**Method A: TSO/ISPF**
1. Navigate to `<Your HLQ>.ECOMAPP.JCL`
2. Type `SUB` next to ECOMRS member

**Method B: Zowe CLI**
```bash
zowe jobs submit data-set "<Your HLQ>.ECOMAPP.JCL(ECOMRS)"
```

**What ECOMRS Does:**
- Runs RUNSTATS on all 16 tablespaces
- Runs RUNSTATS on all indexes (both primary key and performance indexes)
- Updates Db2 catalog statistics for query optimization

**Expected Result:**
- RC=0: All statistics gathered successfully
- Db2 optimizer can now make informed access path decisions

**When to Run:**
- After initial database creation
- After loading or significantly modifying data
- Periodically as part of database maintenance (weekly/monthly)

---

## Database Operations

### Standard Operations

#### **Create Database (Full Build)**
```
Submit: ECOMDDL
Purpose: Build complete database structure
Time: ~2-5 minutes
Prerequisites: None (or previous database dropped)
Result: Empty database with all tables, indexes, constraints
```

#### **Initialize Product Catalog**
```
Submit: ECOMINIT
Purpose: Load 4,824 NextGen America product variants + 5 initial users
Time: ~3-5 minutes
Prerequisites: ECOMDDL completed successfully
Result: Complete product catalog + user accounts ready for operations
```

#### **Load Inventory Data**
```
Submit: ECOMFILL
Purpose: Load mystery product inventory (767 units, 24 SKUs)
Time: <1 minute
Prerequisites: ECOMINIT completed (products and users must exist)
Result: Sellable inventory owned by Christy D (christy@nxtcg.com)
```

#### **Gather Statistics**
```
Submit: ECOMRS
Purpose: Update Db2 catalog statistics
Time: ~2-5 minutes
Prerequisites: Database created (ECOMDDL completed)
Frequency: After data loads, weekly/monthly
```

#### **Apply Grants Only**
```
Submit: ECOMGRNT
Purpose: Re-apply privileges without full rebuild
Time: <1 minute
Prerequisites: Database already exists
Use Case: Adding new application users
```

#### **Drop Database (Complete Teardown)**
```
Submit: ECOMDROP
Purpose: Remove all database objects
Time: ~1-2 minutes
Prerequisites: No active connections to ECOMDB01
⚠️ WARNING: Destroys all data - use with caution!
```

#### **Load Additional Test Data** (Reserved)
```
Submit: ECOMLOAD
Purpose: Reserved for future user/order test data
Status: Not yet implemented
Note: Product catalog uses ECOMINIT instead
```

---

### Job Execution Order (Typical Workflow)

**Initial Setup:**
```
1. Customize all files (replace placeholders)
2. Create <Your HLQ>.ECOMAPP.ECOMALOC dataset
3. Upload ECOMALOC.jcl
4. Submit ECOMALOC → Creates DDL and JCL libraries
5. Upload all DDL members to <Your HLQ>.ECOMAPP.DDL
6. Upload all JCL members to <Your HLQ>.ECOMAPP.JCL
7. Submit ECOMDDL → Creates database structure
8. Submit ECOMINIT → Loads product catalog + users (4,824 variants + 5 users)
9. Submit ECOMFILL → Loads inventory (767 mystery product units)
10. Submit ECOMRS → Gathers statistics
```

**Rebuild Database:**
```
1. Submit ECOMDROP → Removes all objects
2. Submit ECOMDDL → Rebuilds database structure
3. Submit ECOMINIT → Reloads product catalog + users
4. Submit ECOMFILL → Reloads inventory
5. Submit ECOMRS → Gathers statistics
```

**Add New Application User:**
```
1. Edit E06GRANT.sql: Update <Your USERGRP> placeholder
2. Re-upload E06GRANT to <Your HLQ>.ECOMAPP.DDL
3. Submit ECOMGRNT → Applies grants
```

---

## SQL Query Examples

This section provides common SQL queries for typical e-commerce operations. Replace `<Your HLQ>` with your actual High-Level Qualifier.

### User Management

#### **Create a New User**
```sql
INSERT INTO <Your HLQ>.USERS
  (EMAIL, HASHED_PASSWORD, PASSWORD_ALG, FIRST_NAME, LAST_NAME)
VALUES 
  ('newuser@example.com',
   'c7da87713c8e2a933acb2786ea9f7a0c23de42473bce00e46b1e6a37ed48d079',
   'SHA256',
   'John',
   'Doe');
```

#### **Verify User Login (Check Password Hash)**
```sql
SELECT ID, EMAIL, FIRST_NAME, LAST_NAME, IS_ACTIVE
FROM <Your HLQ>.USERS
WHERE EMAIL = 'ben@nxtcg.com'
  AND HASHED_PASSWORD = 'c7da87713c8e2a933acb2786ea9f7a0c23de42473bce00e46b1e6a37ed48d079'
  AND IS_ACTIVE = 'Y';
```

#### **List All Active Users**
```sql
SELECT ID, EMAIL, FIRST_NAME, LAST_NAME, CREATED_AT
FROM <Your HLQ>.USERS
WHERE IS_ACTIVE = 'Y'
ORDER BY CREATED_AT DESC;
```

#### **Deactivate a User Account**
```sql
UPDATE <Your HLQ>.USERS
SET IS_ACTIVE = 'N',
    UPDATED_AT = CURRENT TIMESTAMP
WHERE EMAIL = 'olduser@example.com';
```

### Inventory Management

#### **Add Inventory for a Product Variant**
```sql
INSERT INTO <Your HLQ>.INVENTORY
  (SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE,
   QUANTITY_AVAILABLE, UNIT_PRICE_CENTS)
VALUES
  ((SELECT ID FROM <Your HLQ>.USERS WHERE EMAIL = 'christy@nxtcg.com'),
   'NA', 'C', 'SE01', 'ENM', 10, 100);
```

#### **Update Inventory Quantity**
```sql
UPDATE <Your HLQ>.INVENTORY
SET QUANTITY_AVAILABLE = QUANTITY_AVAILABLE + 50,
    UPDATED_AT = CURRENT TIMESTAMP
WHERE SELLER_ID = 3
  AND SERIES_CODE = 'NA'
  AND STYLE_CODE = 'S'
  AND SERIAL_NUMBER = 'XW01'
  AND MODIFIER_CODE = 'NIB';
```

#### **View Available Inventory by Seller**
```sql
SELECT 
    I.ID AS INVENTORY_ID,
    U.EMAIL AS SELLER_EMAIL,
    U.FIRST_NAME || ' ' || U.LAST_NAME AS SELLER_NAME,
    PV.DISPLAY_NAME,
    I.QUANTITY_AVAILABLE,
    I.UNIT_PRICE_CENTS,
    CAST(I.UNIT_PRICE_CENTS / 100.00 AS DECIMAL(10,2)) AS PRICE_USD
FROM <Your HLQ>.INVENTORY I
JOIN <Your HLQ>.USERS U ON I.SELLER_ID = U.ID
JOIN <Your HLQ>.PRODUCT_VARIANTS PV 
  ON I.SERIES_CODE = PV.SERIES_CODE
 AND I.STYLE_CODE = PV.STYLE_CODE
 AND I.SERIAL_NUMBER = PV.SERIAL_NUMBER
 AND I.MODIFIER_CODE = PV.MODIFIER_CODE
WHERE U.EMAIL = 'christy@nxtcg.com'
  AND I.QUANTITY_AVAILABLE > 0
ORDER BY PV.DISPLAY_NAME;
```

#### **Check Total Inventory Value by Seller**
```sql
SELECT 
    U.EMAIL,
    U.FIRST_NAME || ' ' || U.LAST_NAME AS SELLER_NAME,
    COUNT(*) AS TOTAL_SKUS,
    SUM(I.QUANTITY_AVAILABLE) AS TOTAL_UNITS,
    SUM(I.QUANTITY_AVAILABLE * I.UNIT_PRICE_CENTS) AS TOTAL_VALUE_CENTS,
    CAST(SUM(I.QUANTITY_AVAILABLE * I.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(12,2)) AS TOTAL_VALUE_USD
FROM <Your HLQ>.INVENTORY I
JOIN <Your HLQ>.USERS U ON I.SELLER_ID = U.ID
WHERE I.QUANTITY_AVAILABLE > 0
GROUP BY U.EMAIL, U.FIRST_NAME, U.LAST_NAME
ORDER BY TOTAL_VALUE_CENTS DESC;
```

### Shopping Cart Operations

#### **Create a New Cart for a User**
```sql
INSERT INTO <Your HLQ>.CARTS (USER_ID)
VALUES ((SELECT ID FROM <Your HLQ>.USERS WHERE EMAIL = 'ben@nxtcg.com'));
```

#### **Add Item to Cart**
```sql
INSERT INTO <Your HLQ>.CART_ITEMS
  (CART_ID, INVENTORY_ID, QUANTITY, UNIT_PRICE_CENTS)
VALUES
  ((SELECT ID FROM <Your HLQ>.CARTS 
    WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                     WHERE EMAIL = 'ben@nxtcg.com')
      AND IS_ACTIVE = 'Y'
    FETCH FIRST 1 ROW ONLY),
   25,  -- Inventory ID
   2,   -- Quantity
   300); -- Price at time of add
```

#### **View Cart Contents with Product Details**
```sql
SELECT 
    C.ID AS CART_ID,
    U.EMAIL AS BUYER_EMAIL,
    CI.ID AS CART_ITEM_ID,
    PV.DISPLAY_NAME AS PRODUCT,
    CI.QUANTITY,
    CI.UNIT_PRICE_CENTS,
    CAST(CI.UNIT_PRICE_CENTS / 100.00 AS DECIMAL(10,2)) AS UNIT_PRICE_USD,
    CI.QUANTITY * CI.UNIT_PRICE_CENTS AS LINE_TOTAL_CENTS,
    CAST((CI.QUANTITY * CI.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(10,2)) AS LINE_TOTAL_USD
FROM <Your HLQ>.CARTS C
JOIN <Your HLQ>.USERS U ON C.USER_ID = U.ID
JOIN <Your HLQ>.CART_ITEMS CI ON C.ID = CI.CART_ID
JOIN <Your HLQ>.INVENTORY I ON CI.INVENTORY_ID = I.ID
JOIN <Your HLQ>.PRODUCT_VARIANTS PV
  ON I.SERIES_CODE = PV.SERIES_CODE
 AND I.STYLE_CODE = PV.STYLE_CODE
 AND I.SERIAL_NUMBER = PV.SERIAL_NUMBER
 AND I.MODIFIER_CODE = PV.MODIFIER_CODE
WHERE U.EMAIL = 'ben@nxtcg.com'
  AND C.IS_ACTIVE = 'Y'
ORDER BY CI.CREATED_AT;
```

#### **Calculate Cart Total**
```sql
SELECT 
    C.ID AS CART_ID,
    U.EMAIL,
    COUNT(CI.ID) AS ITEM_COUNT,
    SUM(CI.QUANTITY) AS TOTAL_UNITS,
    SUM(CI.QUANTITY * CI.UNIT_PRICE_CENTS) AS CART_TOTAL_CENTS,
    CAST(SUM(CI.QUANTITY * CI.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(10,2)) AS CART_TOTAL_USD
FROM <Your HLQ>.CARTS C
JOIN <Your HLQ>.USERS U ON C.USER_ID = U.ID
JOIN <Your HLQ>.CART_ITEMS CI ON C.ID = CI.CART_ID
WHERE U.EMAIL = 'ben@nxtcg.com'
  AND C.IS_ACTIVE = 'Y'
GROUP BY C.ID, U.EMAIL;
```

#### **Remove Item from Cart**
```sql
DELETE FROM <Your HLQ>.CART_ITEMS
WHERE CART_ID = (SELECT ID FROM <Your HLQ>.CARTS 
                 WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                                  WHERE EMAIL = 'ben@nxtcg.com')
                   AND IS_ACTIVE = 'Y'
                 FETCH FIRST 1 ROW ONLY)
  AND INVENTORY_ID = 25;
```

#### **Clear Entire Cart**
```sql
DELETE FROM <Your HLQ>.CART_ITEMS
WHERE CART_ID = (SELECT ID FROM <Your HLQ>.CARTS 
                 WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                                  WHERE EMAIL = 'ben@nxtcg.com')
                   AND IS_ACTIVE = 'Y'
                 FETCH FIRST 1 ROW ONLY);
```

### Product Catalog Queries

#### **Search Products by Name**
```sql
SELECT 
    PT.SERIES_CODE,
    PT.STYLE_CODE,
    PT.SERIAL_NUMBER,
    PT.DESCRIPTION AS PRODUCT_NAME,
    PT.BASE_PRICE_CENTS,
    CAST(PT.BASE_PRICE_CENTS / 100.00 AS DECIMAL(10,2)) AS BASE_PRICE_USD,
    S.DESCRIPTION AS STYLE
FROM <Your HLQ>.PRODUCT_TYPES PT
JOIN <Your HLQ>.STYLES S ON PT.STYLE_CODE = S.CODE
WHERE PT.DESCRIPTION LIKE '%Mystery%'
ORDER BY PT.DESCRIPTION;
```

#### **View Product Variants with Calculated Prices**
```sql
SELECT 
    PT.DESCRIPTION AS PRODUCT,
    SM.DESCRIPTION AS MODIFIER,
    PV.DISPLAY_NAME,
    PT.BASE_PRICE_CENTS,
    SM.PRICE_MULTIPLIER,
    CAST(PT.BASE_PRICE_CENTS * SM.PRICE_MULTIPLIER AS INTEGER) 
        AS FINAL_PRICE_CENTS,
    CAST((PT.BASE_PRICE_CENTS * SM.PRICE_MULTIPLIER) / 100.00 
         AS DECIMAL(10,2)) AS FINAL_PRICE_USD
FROM <Your HLQ>.PRODUCT_VARIANTS PV
JOIN <Your HLQ>.PRODUCT_TYPES PT
  ON PV.SERIES_CODE = PT.SERIES_CODE
 AND PV.STYLE_CODE = PT.STYLE_CODE
 AND PV.SERIAL_NUMBER = PT.SERIAL_NUMBER
JOIN <Your HLQ>.STYLE_MODIFIERS SM
  ON PV.STYLE_CODE = SM.STYLE_CODE
 AND PV.MODIFIER_CODE = SM.MODIFIER_CODE
WHERE PT.DESCRIPTION = 'Ben'
ORDER BY FINAL_PRICE_CENTS DESC;
```

#### **Find Available Products with Inventory**
```sql
SELECT 
    PV.DISPLAY_NAME AS PRODUCT,
    I.QUANTITY_AVAILABLE,
    I.UNIT_PRICE_CENTS,
    CAST(I.UNIT_PRICE_CENTS / 100.00 AS DECIMAL(10,2)) AS PRICE_USD,
    U.FIRST_NAME || ' ' || U.LAST_NAME AS SELLER
FROM <Your HLQ>.PRODUCT_VARIANTS PV
JOIN <Your HLQ>.INVENTORY I
  ON PV.SERIES_CODE = I.SERIES_CODE
 AND PV.STYLE_CODE = I.STYLE_CODE
 AND PV.SERIAL_NUMBER = I.SERIAL_NUMBER
 AND PV.MODIFIER_CODE = I.MODIFIER_CODE
JOIN <Your HLQ>.USERS U ON I.SELLER_ID = U.ID
WHERE I.QUANTITY_AVAILABLE > 0
  AND PV.DISPLAY_NAME LIKE '%Mystery%'
ORDER BY I.UNIT_PRICE_CENTS, PV.DISPLAY_NAME;
```

### Order Management

#### **Create New Order from Cart**
```sql
-- Step 1: Create order
INSERT INTO <Your HLQ>.ORDERS
  (USER_ID, TOTAL_CENTS, STATUS)
SELECT 
    C.USER_ID,
    SUM(CI.QUANTITY * CI.UNIT_PRICE_CENTS) AS TOTAL_CENTS,
    'PENDING'
FROM <Your HLQ>.CARTS C
JOIN <Your HLQ>.CART_ITEMS CI ON C.ID = CI.CART_ID
WHERE C.USER_ID = (SELECT ID FROM <Your HLQ>.USERS WHERE EMAIL = 'ben@nxtcg.com')
  AND C.IS_ACTIVE = 'Y'
GROUP BY C.USER_ID;

-- Step 2: Copy cart items to order items
INSERT INTO <Your HLQ>.ORDER_ITEMS
  (ORDER_ID, INVENTORY_ID, QUANTITY, UNIT_PRICE_CENTS)
SELECT 
    (SELECT MAX(ID) FROM <Your HLQ>.ORDERS 
     WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                      WHERE EMAIL = 'ben@nxtcg.com')),
    CI.INVENTORY_ID,
    CI.QUANTITY,
    CI.UNIT_PRICE_CENTS
FROM <Your HLQ>.CART_ITEMS CI
WHERE CI.CART_ID = (SELECT ID FROM <Your HLQ>.CARTS 
                    WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                                     WHERE EMAIL = 'ben@nxtcg.com')
                      AND IS_ACTIVE = 'Y'
                    FETCH FIRST 1 ROW ONLY);

-- Step 3: Deactivate cart
UPDATE <Your HLQ>.CARTS
SET IS_ACTIVE = 'N',
    UPDATED_AT = CURRENT TIMESTAMP
WHERE USER_ID = (SELECT ID FROM <Your HLQ>.USERS WHERE EMAIL = 'ben@nxtcg.com')
  AND IS_ACTIVE = 'Y';
```

#### **View Order History for User**
```sql
SELECT 
    O.ID AS ORDER_ID,
    O.STATUS,
    O.TOTAL_CENTS,
    CAST(O.TOTAL_CENTS / 100.00 AS DECIMAL(10,2)) AS TOTAL_USD,
    O.CREATED_AT AS ORDER_DATE,
    COUNT(OI.ID) AS ITEM_COUNT,
    SUM(OI.QUANTITY) AS TOTAL_UNITS
FROM <Your HLQ>.ORDERS O
JOIN <Your HLQ>.ORDER_ITEMS OI ON O.ID = OI.ORDER_ID
WHERE O.USER_ID = (SELECT ID FROM <Your HLQ>.USERS 
                   WHERE EMAIL = 'ben@nxtcg.com')
GROUP BY O.ID, O.STATUS, O.TOTAL_CENTS, O.CREATED_AT
ORDER BY O.CREATED_AT DESC;
```

#### **View Order Details with Line Items**
```sql
SELECT 
    O.ID AS ORDER_ID,
    O.STATUS,
    U.EMAIL AS CUSTOMER_EMAIL,
    PV.DISPLAY_NAME AS PRODUCT,
    OI.QUANTITY,
    OI.UNIT_PRICE_CENTS,
    CAST(OI.UNIT_PRICE_CENTS / 100.00 AS DECIMAL(10,2)) AS UNIT_PRICE_USD,
    OI.QUANTITY * OI.UNIT_PRICE_CENTS AS LINE_TOTAL_CENTS,
    CAST((OI.QUANTITY * OI.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(10,2)) AS LINE_TOTAL_USD
FROM <Your HLQ>.ORDERS O
JOIN <Your HLQ>.USERS U ON O.USER_ID = U.ID
JOIN <Your HLQ>.ORDER_ITEMS OI ON O.ID = OI.ORDER_ID
JOIN <Your HLQ>.INVENTORY I ON OI.INVENTORY_ID = I.ID
JOIN <Your HLQ>.PRODUCT_VARIANTS PV
  ON I.SERIES_CODE = PV.SERIES_CODE
 AND I.STYLE_CODE = PV.STYLE_CODE
 AND I.SERIAL_NUMBER = PV.SERIAL_NUMBER
 AND I.MODIFIER_CODE = PV.MODIFIER_CODE
WHERE O.ID = 1
ORDER BY OI.ID;
```

#### **Update Order Status**
```sql
UPDATE <Your HLQ>.ORDERS
SET STATUS = 'SHIPPED',
    UPDATED_AT = CURRENT TIMESTAMP
WHERE ID = 1;
```

### Reporting Queries

#### **Top Selling Products**
```sql
SELECT 
    PV.DISPLAY_NAME AS PRODUCT,
    COUNT(OI.ID) AS TIMES_ORDERED,
    SUM(OI.QUANTITY) AS TOTAL_UNITS_SOLD,
    SUM(OI.QUANTITY * OI.UNIT_PRICE_CENTS) AS TOTAL_REVENUE_CENTS,
    CAST(SUM(OI.QUANTITY * OI.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(12,2)) AS TOTAL_REVENUE_USD
FROM <Your HLQ>.ORDER_ITEMS OI
JOIN <Your HLQ>.INVENTORY I ON OI.INVENTORY_ID = I.ID
JOIN <Your HLQ>.PRODUCT_VARIANTS PV
  ON I.SERIES_CODE = PV.SERIES_CODE
 AND I.STYLE_CODE = PV.STYLE_CODE
 AND I.SERIAL_NUMBER = PV.SERIAL_NUMBER
 AND I.MODIFIER_CODE = PV.MODIFIER_CODE
GROUP BY PV.DISPLAY_NAME
ORDER BY TOTAL_REVENUE_CENTS DESC
FETCH FIRST 10 ROWS ONLY;
```

#### **Sales by Seller**
```sql
SELECT 
    U.EMAIL AS SELLER_EMAIL,
    U.FIRST_NAME || ' ' || U.LAST_NAME AS SELLER_NAME,
    COUNT(DISTINCT OI.ORDER_ID) AS ORDERS_FULFILLED,
    SUM(OI.QUANTITY) AS UNITS_SOLD,
    SUM(OI.QUANTITY * OI.UNIT_PRICE_CENTS) AS REVENUE_CENTS,
    CAST(SUM(OI.QUANTITY * OI.UNIT_PRICE_CENTS) / 100.00 
         AS DECIMAL(12,2)) AS REVENUE_USD
FROM <Your HLQ>.ORDER_ITEMS OI
JOIN <Your HLQ>.INVENTORY I ON OI.INVENTORY_ID = I.ID
JOIN <Your HLQ>.USERS U ON I.SELLER_ID = U.ID
GROUP BY U.EMAIL, U.FIRST_NAME, U.LAST_NAME
ORDER BY REVENUE_CENTS DESC;
```

### Data Verification Queries

#### **Validate Referential Integrity**
```sql
-- Check for orphaned inventory (no matching product variant)
SELECT COUNT(*) AS ORPHANED_INVENTORY
FROM <Your HLQ>.INVENTORY I
WHERE NOT EXISTS (
    SELECT 1 FROM <Your HLQ>.PRODUCT_VARIANTS PV
    WHERE PV.SERIES_CODE = I.SERIES_CODE
      AND PV.STYLE_CODE = I.STYLE_CODE
      AND PV.SERIAL_NUMBER = I.SERIAL_NUMBER
      AND PV.MODIFIER_CODE = I.MODIFIER_CODE
);

-- Check for orphaned cart items (no matching cart)
SELECT COUNT(*) AS ORPHANED_CART_ITEMS
FROM <Your HLQ>.CART_ITEMS CI
WHERE NOT EXISTS (
    SELECT 1 FROM <Your HLQ>.CARTS C WHERE C.ID = CI.CART_ID
);
```

#### **Database Statistics Summary**
```sql
SELECT 
    'Users' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT
FROM <Your HLQ>.USERS
UNION ALL
SELECT 'Product Types', COUNT(*) FROM <Your HLQ>.PRODUCT_TYPES
UNION ALL
SELECT 'Product Variants', COUNT(*) FROM <Your HLQ>.PRODUCT_VARIANTS
UNION ALL
SELECT 'Inventory Items', COUNT(*) FROM <Your HLQ>.INVENTORY
UNION ALL
SELECT 'Active Carts', COUNT(*) FROM <Your HLQ>.CARTS WHERE IS_ACTIVE = 'Y'
UNION ALL
SELECT 'Orders', COUNT(*) FROM <Your HLQ>.ORDERS
UNION ALL
SELECT 'Order Items', COUNT(*) FROM <Your HLQ>.ORDER_ITEMS
ORDER BY TABLE_NAME;
```

---

## Pricing Model

### Multiplier-Based Dynamic Pricing

ECOMAPP uses a **multiplier-based pricing system** where each product variant's final price is calculated by multiplying the base price by a modifier-specific multiplier.

#### Formula

```
Final Price = BASE_PRICE_CENTS × PRICE_MULTIPLIER
```

#### Schema Design

**PRODUCT_TYPES Table:**
- `BASE_PRICE_CENTS` - Base price for the product type (e.g., 100 cents = $1.00 for cards)

**STYLE_MODIFIERS Table:**
- `PRICE_MULTIPLIER` - Decimal multiplier applied to base price (e.g., 1.75 for reverse holofoil)

**PRODUCT_TYPE_MODIFIERS Table:**
- Links product types to applicable modifiers
- **Note:** Does NOT contain `PRICE_DELTA_CENTS` (removed in March 2026 update)

**PRODUCT_VARIANTS Table:**
- Represents sellable SKUs
- Price calculated dynamically from PRODUCT_TYPES.BASE_PRICE_CENTS × STYLE_MODIFIERS.PRICE_MULTIPLIER

#### Pricing Examples

**NextGen America Card (NA-C-SE01 "Ben Card") - Base Price: $1.00**

| Modifier | Description | Multiplier | Final Price |
|----------|-------------|------------|-------------|
| ENM | English, Non-Foil, Mint | 1.00 | $1.00 |
| ENN | English, Non-Foil, Near-Mint | 0.85 | $0.85 |
| ENL | English, Non-Foil, Light Play | 0.60 | $0.60 |
| ENP | English, Non-Foil, Moderate Play | 0.40 | $0.40 |
| ERM | English, Reverse Holofoil, Mint | 1.75 | $1.75 |
| ERN | English, Reverse Holofoil, Near-Mint | 1.49 | $1.49 |
| ERL | English, Reverse Holofoil, Light Play | 1.05 | $1.05 |
| ERP | English, Reverse Holofoil, Moderate Play | 0.70 | $0.70 |
| EHM | English, Holofoil, Mint | 2.50 | $2.50 |
| EHN | English, Holofoil, Near-Mint | 2.13 | $2.13 |
| EHL | English, Holofoil, Light Play | 1.50 | $1.50 |
| EHP | English, Holofoil, Moderate Play | 1.00 | $1.00 |

**Mystery Products - Base Prices:**
- Mystery Singles (NA-S): $3.00 × 1.00 (NIB) = $3.00
- Mystery Midis (NA-M): $5.00 × 1.00 (NIB) = $5.00
- Mystery Packs (NA-P): $10.00 × 1.00 (NIB) = $10.00

#### Price Calculation in SQL

```sql
-- Calculate final price for a product variant
SELECT 
    PV.SERIES_CODE || PV.STYLE_CODE || PV.SERIAL_NUMBER || PV.MODIFIER_CODE AS SKU,
    PT.DESCRIPTION AS PRODUCT_NAME,
    SM.DESCRIPTION AS MODIFIER_NAME,
    PT.BASE_PRICE_CENTS,
    SM.PRICE_MULTIPLIER,
    CAST(PT.BASE_PRICE_CENTS * SM.PRICE_MULTIPLIER AS INTEGER) AS FINAL_PRICE_CENTS,
    CAST(PT.BASE_PRICE_CENTS * SM.PRICE_MULTIPLIER / 100.0 AS DECIMAL(10,2)) AS FINAL_PRICE_DOLLARS
FROM <Your HLQ>.PRODUCT_VARIANTS PV
INNER JOIN <Your HLQ>.PRODUCT_TYPES PT 
    ON PV.SERIES_CODE = PT.SERIES_CODE
   AND PV.STYLE_CODE = PT.STYLE_CODE
   AND PV.SERIAL_NUMBER = PT.SERIAL_NUMBER
INNER JOIN <Your HLQ>.STYLE_MODIFIERS SM
    ON PV.STYLE_CODE = SM.STYLE_CODE
   AND PV.MODIFIER_CODE = SM.MODIFIER_CODE
WHERE PV.SERIES_CODE = 'NA'
  AND PV.STYLE_CODE = 'C'
  AND PV.SERIAL_NUMBER = 'SE01';
```

#### Benefits of Multiplier-Based Pricing

1. **Flexibility** - Easy to adjust pricing for entire modifier categories (e.g., increase all holofoil multipliers by 10%)
2. **Consistency** - Same multiplier applies to all products with that modifier
3. **Simplicity** - No per-product price overrides; pricing rules are centralized
4. **Performance** - Calculation happens at query time; no denormalized price columns to maintain
5. **Accuracy** - Eliminates rounding errors from additive price deltas

#### Schema Changes (March 2026)

**Previous Model (Additive - Deprecated):**
```sql
-- Old schema (removed)
PRODUCT_TYPE_MODIFIERS.PRICE_DELTA_CENTS INT
Final Price = BASE_PRICE_CENTS + PRICE_DELTA_CENTS
```

**Current Model (Multiplicative):**
```sql
-- Current schema
STYLE_MODIFIERS.PRICE_MULTIPLIER DECIMAL(5,2)
Final Price = BASE_PRICE_CENTS × PRICE_MULTIPLIER
```

**Why We Changed:**
- Additive model doesn't scale (must set delta for every product-modifier combination)
- Multiplier model is more intuitive (damaged cards are 40% of base, not "minus X cents")
- Easier to maintain (change one multiplier vs. thousands of deltas)
- Better reflects real-world pricing (condition affects percentage, not fixed amount)

---

## Database Design

### SKU Architecture

ECOMAPP uses a hierarchical SKU system: **SERIES-STYLE-SERIAL-MODIFIER**

**Example SKU:** `NAC-SE01-EHM`
- **NA** = Series (NextGen America)
- **C** = Style (Card Single)
- **SE01** = Serial Number (Ben card)
- **EHM** = Modifier (English, Holofoil, Mint)

### Product Catalog Summary

| Component | Count | Description |
|-----------|-------|-------------|
| **Series** | 1 | NextGen America |
| **Styles** | 4 | Card Single, Mystery Single, Mystery Midi, Mystery Pack |
| **Style Modifiers** | 63 | 60 card modifiers (5 languages × 3 foil types × 4 conditions) + NIB |
| **Product Types** | 104 | 80 individual cards + 24 mystery products |
| **Product-Modifier Links** | 4,824 | PRODUCT_TYPE_MODIFIERS entries |
| **Product Variants (SKUs)** | 4,824 | Sellable items in catalog |

**Card Modifiers (60 combinations):**
- **Languages:** English, Japanese, Korean, Australian, Spanish (5)
- **Foil Types:** Holofoil, Reverse Holofoil, Non-Foil (3)
- **Conditions:** Mint, Near-Mint, Light Play, Moderate Play (4)

**Mystery Product Modifier:**
- **NIB** (New In Box) - Only modifier for sealed mystery products

### E-Commerce Support Tables

The remaining tables support e-commerce operations:
- **USERS** - Customer accounts
- **TOKENS** - Authentication tokens
- **VARIANT_IMAGES** - Product images (URLs)
- **INVENTORY** - Stock levels per variant
- **CARTS** - Shopping carts (1 per user)
- **CART_ITEMS** - Line items in carts
- **ADDRESSES** - Customer shipping addresses
- **ORDERS** - Completed purchases
- **ORDER_ADDRESSES** - Shipping details for orders
- **ORDER_ITEMS** - Line items in orders

These tables are defined in E03TABLE.sql but are NOT populated by ECOMINIT. They will be populated by the e-commerce application at runtime.

---

## Customization Guide

### Modifying the Product Catalog

#### **Adding New Cards**

1. **Update E07INIT1.sql** - Add new PRODUCT_TYPES INSERT:
```sql
INSERT INTO <Your HLQ>.PRODUCT_TYPES
(SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, DESCRIPTION, BASE_PRICE_CENTS)
VALUES ('NA', 'C', 'NEW1', 'New Card Name', 100);
```

2. **Update E07INIT2.sql or E07INIT4.sql** - Link to 60 modifiers (repeat for all 60 card modifiers)

3. **Update E07INIT3.sql or E07INIT5.sql** - Create variants (repeat for all 60 modifiers)

4. **Re-upload and reinitialize:**
```
Submit: ECOMDROP (if rebuilding)
Submit: ECOMDDL
Submit: ECOMINIT
```

#### **Changing Prices**

**Option A: Change Base Prices (affects all variants)**
```sql
UPDATE <Your HLQ>.PRODUCT_TYPES
SET BASE_PRICE_CENTS = 150
WHERE SERIES_CODE = 'NA' AND STYLE_CODE = 'C';
```

**Option B: Change Multipliers (affects specific modifiers)**
```sql
UPDATE <Your HLQ>.STYLE_MODIFIERS
SET PRICE_MULTIPLIER = 2.75
WHERE STYLE_CODE = 'C' AND MODIFIER_CODE = 'EHM';
```

### Modifying Schema Objects

#### **Adding a New Table**

1. **Update E03TABLE.sql**
   - Add CREATE TABLE statement in appropriate section
   - Add CREATE UNIQUE INDEX for primary key
   - Add foreign key constraints if needed

2. **Update E04INDEX.sql** (if needed)
   - Add performance indexes for new table

3. **Update E05CMNT.sql** (if needed)
   - Add COMMENT statements for new table/columns

4. **Update E06GRANT.sql**
   - Add GRANT statement for new table

5. **Update E07LOAD.sql** (if needed)
   - Add INSERT statements for test data

6. **Update ECOMDROP.jcl**
   - Add DROP TABLE statement in appropriate position (drop dependent objects first)

7. **Re-upload and re-run**
   - Upload modified DDL files
   - Submit ECOMDROP (if rebuilding)
   - Submit ECOMDDL

#### **Modifying Existing Table**

**Option A: Rebuild (destructive)**
```
1. Update E03TABLE.sql with new table definition
2. Submit ECOMDROP
3. Submit ECOMDDL
4. Submit ECOMLOAD (reloads test data)
```

**Option B: ALTER (preserves data)**
```
1. Create new DDL member with ALTER TABLE statements
2. Update ECOMDDL.jcl to include new step
3. Submit ECOMDDL (or create separate JCL job)
```

#### **Adding New Indexes**

1. Update E04INDEX.sql
2. Re-upload E04INDEX member
3. Submit ECOMDDL (only INDEXES step will add new indexes)
   - Existing objects will return RC=8 (-601), new indexes will be created

### Changing Placeholders After Installation

If you need to migrate objects to a different schema or Db2 subsystem:

1. **Export Data** (if preserving data)
   ```sql
   -- Use UNLOAD or SELECT INTO to export data
   ```

2. **Update All Files**
   - Perform global find/replace with new values
   - Re-upload all DDL and JCL members

3. **Drop Old Database**
   ```
   Submit ECOMDROP (using old values)
   ```

4. **Create New Database**
   ```
   Submit ECOMDDL (using new values)
   ```

5. **Reload Data** (if applicable)
   ```
   -- Use LOAD or INSERT to restore data
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### **Issue: ECOMDDL Fails with RC=12 - "PLAN NOT FOUND"**

**Cause:** Db2 plan DSNTEP3 not available or no EXECUTE privilege

**Solution:**
```
1. Verify DSNTEP3 plan exists:
   -DIS THREAD(*) TYPE(PLAN)
   
2. Check your privileges:
   SELECT GRANTEE, GRANTEETYPE, AUTHHOWGOT
   FROM SYSIBM.SYSPLANAUTH
   WHERE NAME = 'DSNTEP3';

3. If missing privilege, have DBA grant:
   GRANT EXECUTE ON PLAN DSNTEP3 TO <Your HLQ>;
```

#### **Issue: ECOMDDL Fails with RC=12 - "SQLCODE=-204 OBJECT NOT FOUND"**

**Cause:** DDL members not uploaded or incorrect dataset names

**Solution:**
```
1. Verify DDL members exist:
   TSO/ISPF 3.4 → <Your HLQ>.ECOMAPP.DDL
   
2. Check member names match exactly:
   E01STGDB, E02TBSPC, E03TABLE, E04INDEX, E05CMNT, E06GRANT
   E07INIT1, E07INIT2, E07INIT3, E07INIT4, E07INIT5
   
3. Verify SET HLQ statement in ECOMDDL.jcl matches your dataset name
```

#### **Issue: ECOMDDL Fails with RC=8 - "SQLCODE=-601 OBJECT ALREADY EXISTS"**

**Cause:** Database objects already exist (normal on re-run)

**Solution:**
```
This is expected behavior when re-running ECOMDDL on existing database.
Job will continue and create any missing objects.

To start fresh:
1. Submit ECOMDROP first
2. Then submit ECOMDDL
```

#### **Issue: ECOMINIT Fails with RC=12 - "Rest API failure with HTTP(S) status 500"**

**Cause:** SQL files have lines exceeding 72 characters (ISPF limitation)

**Solution:**
```
All E07INIT files in zOS_Datasets have been pre-processed to comply
with 72-character line limits. If you modified them:

1. Check for long lines:
   Edit member with ISPF
   COLS ON (show column numbers)
   Look for lines extending past column 72

2. Split long lines:
   - Break INSERT statements after table name
   - Continue column list on next line with leading spaces
   - Ensure VALUES clause on separate line

3. Re-upload corrected members
```

#### **Issue: ECOMINIT Fails with "SQLCODE=-803 DUPLICATE KEY"**

**Cause:** Product catalog already loaded (normal on re-run)

**Solution:**
```
This is expected behavior with RC=8. Job continues to next step.
Each step is conditioned on RC < 12.

To reload catalog from scratch:
1. Submit ECOMDROP first
2. Submit ECOMDDL
3. Submit ECOMINIT
```

#### **Issue: ECOMINIT Shows Wrong Row Counts**

**Cause:** Previous data not cleared, or partial load

**Solution:**
```sql
-- Check current counts
SELECT 'PRODUCT_VARIANTS' AS TABLE_NAME, COUNT(*) AS COUNT
FROM <Your HLQ>.PRODUCT_VARIANTS
UNION ALL
SELECT 'PRODUCT_TYPE_MODIFIERS', COUNT(*) 
FROM <Your HLQ>.PRODUCT_TYPE_MODIFIERS;

Expected:
PRODUCT_VARIANTS: 4,824
PRODUCT_TYPE_MODIFIERS: 4,824

If counts don't match:
1. Submit ECOMDROP
2. Submit ECOMDDL  
3. Submit ECOMINIT
```

#### **Issue: "NOT AUTHORIZED TO CREATE DATABASE"**

**Cause:** Insufficient Db2 privileges

**Solution:**
```
Contact your Db2 DBA to grant CREATEDB authority:

GRANT CREATEDB ON SYSTEM TO <Your HLQ>;
```

#### **Issue: JOBLIB Libraries Not Found**

**Cause:** Incorrect Db2 software library HLQ

**Solution:**
```
1. Find correct Db2 HLQ on your system:
   TSO/ISPF 3.4 → DSN* (or DSNV*)
   Look for: SDSNLOAD, SDSNEXIT, RUNLIB.LOAD
   
2. Update JOBLIB statements in all JCL files:
   //JOBLIB   DD  DISP=SHR,DSN=<Correct HLQ>.SDSNEXIT
   //         DD  DISP=SHR,DSN=<Correct HLQ>.SDSNLOAD
   //         DD  DISP=SHR,DSN=<Correct HLQ>.RUNLIB.LOAD
```

#### **Issue: "STORAGE GROUP NOT DEFINED"**

**Cause:** E01STGDB.sql uses default storage group

**Solution:**
```
1. Find available storage groups:
   SELECT * FROM SYSIBM.SYSSTOGROUP;
   
2. Update E01STGDB.sql:
   CREATE DATABASE ECOMDB01
       STOGROUP <Your STOGROUP>
       BUFFERPOOL BP0
       ...
```

#### **Issue: Price Calculations Return Wrong Values**

**Cause:** Query not joining to STYLE_MODIFIERS table

**Solution:**
```sql
-- Incorrect (missing PRICE_MULTIPLIER):
SELECT PT.BASE_PRICE_CENTS
FROM PRODUCT_VARIANTS PV
INNER JOIN PRODUCT_TYPES PT ON ...;

-- Correct (includes multiplier):
SELECT 
    PT.BASE_PRICE_CENTS,
    SM.PRICE_MULTIPLIER,
    CAST(PT.BASE_PRICE_CENTS * SM.PRICE_MULTIPLIER AS INT) AS FINAL_PRICE
FROM PRODUCT_VARIANTS PV
INNER JOIN PRODUCT_TYPES PT ON ...
INNER JOIN STYLE_MODIFIERS SM 
    ON PV.STYLE_CODE = SM.STYLE_CODE
   AND PV.MODIFIER_CODE = SM.MODIFIER_CODE;
```

#### **Issue: Performance Issues / Slow Queries**

**Cause:** Statistics not gathered or outdated

**Solution:**
```
1. Submit ECOMRS to gather/refresh statistics
2. Verify statistics exist:
   SELECT NAME, CARD, NPAGES
   FROM SYSIBM.SYSTABLES
   WHERE CREATOR = '<Your HLQ>';
   
   If CARD = -1, statistics not gathered
```

---

## Additional Resources

### Db2 for z/OS Documentation
- [IBM Db2 13 for z/OS Documentation](https://www.ibm.com/docs/en/db2-for-zos/13)
- [Db2 SQL Reference](https://www.ibm.com/docs/en/db2-for-zos/13?topic=guide-sql-reference)

### Zowe CLI Documentation
- [Zowe CLI Documentation](https://docs.zowe.org/stable/user-guide/cli-using/)
- [Zowe Files Commands](https://docs.zowe.org/stable/web_help/index.html)

### Contact
For questions, issues, or contributions, please contact:
- **Author:** Ben Edens
- **Date:** March 16, 2026

---

## License

This database implementation is provided as-is for educational and commercial use. Modify as needed for your environment.

---

**End of README**