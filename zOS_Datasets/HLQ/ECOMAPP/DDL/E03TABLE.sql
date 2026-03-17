--********************************************************************
--* MEMBER  : E03TABLE
--* PURPOSE : Create all base tables for ECOMDB01 database
--* PRODUCT : ECOMAPP  (E-Commerce Application)
--* DB2 VER : Db2 13 for z/OS
--* AUTHOR  : Ben Edens
--* DATE    : 2026-03-11
--*------------------------------------------------------------------
--* INSTRUCTIONS:
--*   Replace <Your HLQ> with your High Level Qualifier throughout
--*   this script before running.
--*------------------------------------------------------------------
--* NOTES:
--*   - Tables created with GENERATED ALWAYS AS IDENTITY for PKs
--*   - UNIQUE constraints added via ALTER TABLE after creating
--*     explicit unique indexes to avoid incomplete table status
--*   - SKU-based design: SERIES-STYLE-SERIAL-MODIFIER
--*   - All tables use CCSID UNICODE
--********************************************************************

-- ==============================================================
-- USERS - Application users (buyers and sellers)
-- ==============================================================
CREATE TABLE <Your HLQ>.USERS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    EMAIL            VARCHAR(320) NOT NULL,
    HASHED_PASSWORD  VARCHAR(255) NOT NULL,
    PASSWORD_ALG     VARCHAR(32),
    FIRST_NAME       VARCHAR(40)  NOT NULL,
    LAST_NAME        VARCHAR(40)  NOT NULL,
    IS_ACTIVE        CHAR(1)      NOT NULL DEFAULT 'Y',
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_USERS
        PRIMARY KEY (ID),
    CONSTRAINT CK_USERS_IS_ACTIVE
        CHECK (IS_ACTIVE IN ('Y', 'N'))
  )
  IN ECOMDB01.TSUSERS1
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXUSERS 
    ON <Your HLQ>.USERS (ID);

CREATE UNIQUE INDEX <Your HLQ>.IXUSERSEMAIL 
    ON <Your HLQ>.USERS (EMAIL);

ALTER TABLE <Your HLQ>.USERS
    ADD CONSTRAINT UQ_USERS_EMAIL UNIQUE (EMAIL);

-- ==============================================================
-- TOKENS - Authentication tokens
-- ==============================================================
CREATE TABLE <Your HLQ>.TOKENS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    USER_ID          BIGINT       NOT NULL,
    CONSTRAINT PK_TOKENS
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSTOKENS
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXTOKENS 
    ON <Your HLQ>.TOKENS (ID);

ALTER TABLE <Your HLQ>.TOKENS
    ADD CONSTRAINT FK_TOKENS_USER
        FOREIGN KEY (USER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE CASCADE;

-- ==============================================================
-- SERIES - First two characters of SKU
-- ==============================================================
CREATE TABLE <Your HLQ>.SERIES
  (
    CODE             CHAR(2)      NOT NULL,
    DESCRIPTION      VARCHAR(255) NOT NULL,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_SERIES
        PRIMARY KEY (CODE)
  )
  IN ECOMDB01.TSSERIES
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXSERIES 
    ON <Your HLQ>.SERIES (CODE);

-- ==============================================================
-- STYLES - Second character of SKU
-- ==============================================================
CREATE TABLE <Your HLQ>.STYLES
  (
    CODE             CHAR(1)      NOT NULL,
    DESCRIPTION      VARCHAR(255) NOT NULL,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_STYLES
        PRIMARY KEY (CODE)
  )
  IN ECOMDB01.TSSTYLES
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXSTYLES 
    ON <Your HLQ>.STYLES (CODE);

-- ==============================================================
-- STYLE_MODIFIERS - Valid modifiers per style
-- ==============================================================
CREATE TABLE <Your HLQ>.STYLE_MODIFIERS
  (
    STYLE_CODE       CHAR(1)      NOT NULL,
    MODIFIER_CODE    CHAR(3)      NOT NULL,
    DESCRIPTION      VARCHAR(100) NOT NULL,
    PRICE_MULTIPLIER DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    DISPLAY_ORDER    INT          NOT NULL WITH DEFAULT 1,
    IS_ACTIVE        CHAR(1)      NOT NULL WITH DEFAULT 'Y',
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT CHK_STYLE_MOD_ACTIVE 
        CHECK (IS_ACTIVE IN ('Y', 'N'))
  )
  IN ECOMDB01.TSSTYLMD
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXSTYLMOD 
    ON <Your HLQ>.STYLE_MODIFIERS 
    (STYLE_CODE, MODIFIER_CODE);

ALTER TABLE <Your HLQ>.STYLE_MODIFIERS
    ADD CONSTRAINT PK_STYLE_MODIFIERS
    PRIMARY KEY (STYLE_CODE, MODIFIER_CODE);

ALTER TABLE <Your HLQ>.STYLE_MODIFIERS
    ADD CONSTRAINT FK_STYLE_MODIFIERS_STYLE
    FOREIGN KEY (STYLE_CODE)
    REFERENCES <Your HLQ>.STYLES (CODE);

-- ==============================================================
-- PRODUCT_TYPES - Unique product types by SKU prefix
-- ==============================================================
CREATE TABLE <Your HLQ>.PRODUCT_TYPES
  (
    SERIES_CODE      CHAR(2)      NOT NULL,
    STYLE_CODE       CHAR(1)      NOT NULL,
    SERIAL_NUMBER    CHAR(4)      NOT NULL,
    DESCRIPTION      VARCHAR(255) NOT NULL,
    BASE_PRICE_CENTS INT          NOT NULL,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT
  )
  IN ECOMDB01.TSPRDTYP
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXPRDTYP 
    ON <Your HLQ>.PRODUCT_TYPES 
    (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER);

ALTER TABLE <Your HLQ>.PRODUCT_TYPES
    ADD CONSTRAINT PK_PRODUCT_TYPES
        PRIMARY KEY (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER);

ALTER TABLE <Your HLQ>.PRODUCT_TYPES
    ADD CONSTRAINT FK_PRDTYP_SERIES
        FOREIGN KEY (SERIES_CODE) 
        REFERENCES <Your HLQ>.SERIES (CODE)
        ON DELETE RESTRICT;

ALTER TABLE <Your HLQ>.PRODUCT_TYPES
    ADD CONSTRAINT FK_PRDTYP_STYLE
        FOREIGN KEY (STYLE_CODE) 
        REFERENCES <Your HLQ>.STYLES (CODE)
        ON DELETE RESTRICT;

-- ==============================================================
-- PRODUCT_VARIANTS - Concrete SKUs
-- Directly links product types with style modifiers
-- Note: PRODUCT_TYPE_MODIFIERS table removed (was redundant)
-- ==============================================================
CREATE TABLE <Your HLQ>.PRODUCT_VARIANTS
  (
    SERIES_CODE      CHAR(2)      NOT NULL,
    STYLE_CODE       CHAR(1)      NOT NULL,
    SERIAL_NUMBER    CHAR(4)      NOT NULL,
    MODIFIER_CODE    CHAR(3)      NOT NULL,
    DISPLAY_NAME     VARCHAR(255),
    IS_ACTIVE        CHAR(1)      NOT NULL DEFAULT 'Y',
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT CK_PRDVAR_IS_ACTIVE
        CHECK (IS_ACTIVE IN ('Y', 'N'))
  )
  IN ECOMDB01.TSPRDVAR
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXPRDVAR 
    ON <Your HLQ>.PRODUCT_VARIANTS 
    (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, MODIFIER_CODE);

ALTER TABLE <Your HLQ>.PRODUCT_VARIANTS
    ADD CONSTRAINT PK_PRODUCT_VARIANTS
        PRIMARY KEY (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
                     MODIFIER_CODE);

ALTER TABLE <Your HLQ>.PRODUCT_VARIANTS
    ADD CONSTRAINT FK_PRDVAR_TYPE
        FOREIGN KEY (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER) 
        REFERENCES <Your HLQ>.PRODUCT_TYPES 
                   (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER)
        ON DELETE CASCADE;

ALTER TABLE <Your HLQ>.PRODUCT_VARIANTS
    ADD CONSTRAINT FK_PRDVAR_STYLE_MODIFIER
        FOREIGN KEY (STYLE_CODE, MODIFIER_CODE)
        REFERENCES <Your HLQ>.STYLE_MODIFIERS 
                   (STYLE_CODE, MODIFIER_CODE)
        ON DELETE RESTRICT;

-- ==============================================================
-- VARIANT_IMAGES - Images per full SKU
-- ==============================================================
CREATE TABLE <Your HLQ>.VARIANT_IMAGES
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    SERIES_CODE      CHAR(2)      NOT NULL,
    STYLE_CODE       CHAR(1)      NOT NULL,
    SERIAL_NUMBER    CHAR(4)      NOT NULL,
    MODIFIER_CODE    CHAR(3)      NOT NULL,
    URL              VARCHAR(2048) NOT NULL,
    ALT_TEXT         VARCHAR(255),
    SORT_ORDER       INT          DEFAULT 0,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_VARIANT_IMAGES
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSVARIMG
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXVARIMG 
    ON <Your HLQ>.VARIANT_IMAGES (ID);

ALTER TABLE <Your HLQ>.VARIANT_IMAGES
    ADD CONSTRAINT FK_VARIMG_VARIANT
        FOREIGN KEY (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
                     MODIFIER_CODE) 
        REFERENCES <Your HLQ>.PRODUCT_VARIANTS 
                   (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
                    MODIFIER_CODE)
        ON DELETE CASCADE;

-- ==============================================================
-- INVENTORY - Seller listings per SKU
-- ==============================================================
CREATE TABLE <Your HLQ>.INVENTORY
  (
    ID                   BIGINT       NOT NULL
                                      GENERATED ALWAYS AS IDENTITY
                                      (START WITH 1 INCREMENT BY 1
                                       CACHE 20 NO CYCLE NO ORDER),
    SELLER_ID            BIGINT       NOT NULL,
    SERIES_CODE          CHAR(2)      NOT NULL,
    STYLE_CODE           CHAR(1)      NOT NULL,
    SERIAL_NUMBER        CHAR(4)      NOT NULL,
    MODIFIER_CODE        CHAR(3)      NOT NULL,
    QUANTITY_AVAILABLE   INT          NOT NULL DEFAULT 0,
    UNIT_PRICE_CENTS     INT          NOT NULL,
    CURRENCY_CODE        CHAR(3)      NOT NULL DEFAULT 'USD',
    CREATED_AT           TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT           TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_INVENTORY
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSINVTRY
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXINVTRY 
    ON <Your HLQ>.INVENTORY (ID);

CREATE UNIQUE INDEX <Your HLQ>.IXINVLIST 
    ON <Your HLQ>.INVENTORY 
    (SELLER_ID, SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
     MODIFIER_CODE);

ALTER TABLE <Your HLQ>.INVENTORY
    ADD CONSTRAINT UQ_INVENTORY_LISTING
        UNIQUE (SELLER_ID, SERIES_CODE, STYLE_CODE, 
                SERIAL_NUMBER, MODIFIER_CODE);

ALTER TABLE <Your HLQ>.INVENTORY
    ADD CONSTRAINT FK_INVTRY_SELLER
        FOREIGN KEY (SELLER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE CASCADE;

ALTER TABLE <Your HLQ>.INVENTORY
    ADD CONSTRAINT FK_INVTRY_VARIANT
        FOREIGN KEY (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
                     MODIFIER_CODE) 
        REFERENCES <Your HLQ>.PRODUCT_VARIANTS 
                   (SERIES_CODE, STYLE_CODE, SERIAL_NUMBER, 
                    MODIFIER_CODE)
        ON DELETE RESTRICT;

-- ==============================================================
-- CARTS - Shopping carts
-- ==============================================================
CREATE TABLE <Your HLQ>.CARTS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    USER_ID          BIGINT,
    STATUS           VARCHAR(20)  NOT NULL DEFAULT 'active',
    CURRENCY_CODE    CHAR(3)      NOT NULL DEFAULT 'USD',
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_CARTS
        PRIMARY KEY (ID),
    CONSTRAINT CK_CARTS_STATUS
        CHECK (STATUS IN ('active', 'converted', 'abandoned'))
  )
  IN ECOMDB01.TSCARTS1
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXCARTS 
    ON <Your HLQ>.CARTS (ID);

ALTER TABLE <Your HLQ>.CARTS
    ADD CONSTRAINT FK_CARTS_USER
        FOREIGN KEY (USER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE CASCADE;

-- ==============================================================
-- CART_ITEMS - Items in shopping carts
-- ==============================================================
CREATE TABLE <Your HLQ>.CART_ITEMS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    CART_ID          BIGINT       NOT NULL,
    INVENTORY_ID     BIGINT       NOT NULL,
    QUANTITY         INT          NOT NULL DEFAULT 1,
    UNIT_PRICE_CENTS INT          NOT NULL,
    CURRENCY_CODE    CHAR(3)      NOT NULL DEFAULT 'USD',
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_CART_ITEMS
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSCRTITM
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXCRTITM 
    ON <Your HLQ>.CART_ITEMS (ID);

CREATE UNIQUE INDEX <Your HLQ>.IXCRTINV 
    ON <Your HLQ>.CART_ITEMS (CART_ID, INVENTORY_ID);

ALTER TABLE <Your HLQ>.CART_ITEMS
    ADD CONSTRAINT UQ_CART_INVENTORY
        UNIQUE (CART_ID, INVENTORY_ID);

ALTER TABLE <Your HLQ>.CART_ITEMS
    ADD CONSTRAINT FK_CRTITM_CART
        FOREIGN KEY (CART_ID) 
        REFERENCES <Your HLQ>.CARTS (ID)
        ON DELETE CASCADE;

ALTER TABLE <Your HLQ>.CART_ITEMS
    ADD CONSTRAINT FK_CRTITM_INVTRY
        FOREIGN KEY (INVENTORY_ID) 
        REFERENCES <Your HLQ>.INVENTORY (ID)
        ON DELETE CASCADE;

-- ==============================================================
-- ADDRESSES - User addresses
-- ==============================================================
CREATE TABLE <Your HLQ>.ADDRESSES
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    USER_ID          BIGINT,
    FULL_NAME        VARCHAR(80)  NOT NULL,
    LINE1            VARCHAR(64)  NOT NULL,
    LINE2            VARCHAR(64),
    CITY             VARCHAR(64)  NOT NULL,
    REGION           VARCHAR(64),
    POSTAL_CODE      VARCHAR(16)  NOT NULL,
    COUNTRY_CODE     CHAR(2)      NOT NULL DEFAULT 'US',
    PHONE            VARCHAR(30),
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_ADDRESSES
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSADDR01
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXADDR01 
    ON <Your HLQ>.ADDRESSES (ID);

ALTER TABLE <Your HLQ>.ADDRESSES
    ADD CONSTRAINT FK_ADDRESSES_USER
        FOREIGN KEY (USER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE CASCADE;

-- ==============================================================
-- ORDERS - Customer orders
-- ==============================================================
CREATE TABLE <Your HLQ>.ORDERS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    USER_ID          BIGINT,
    STATUS           VARCHAR(20)  NOT NULL DEFAULT 'pending',
    CURRENCY_CODE    CHAR(3)      NOT NULL DEFAULT 'USD',
    SUBTOTAL_CENTS   INT          NOT NULL DEFAULT 0,
    TAX_CENTS        INT          NOT NULL DEFAULT 0,
    SHIPPING_CENTS   INT          NOT NULL DEFAULT 0,
    DISCOUNT_CENTS   INT          NOT NULL DEFAULT 0,
    TOTAL_CENTS      INT          NOT NULL DEFAULT 0,
    BILLING_ADDRESS_ID  BIGINT,
    SHIPPING_ADDRESS_ID BIGINT,
    PLACED_AT        TIMESTAMP,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    UPDATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_ORDERS
        PRIMARY KEY (ID),
    CONSTRAINT CK_ORDERS_STATUS
        CHECK (STATUS IN ('pending', 'confirmed', 
                         'fulfilled', 'canceled', 'refunded'))
  )
  IN ECOMDB01.TSORDERS
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXORDERS 
    ON <Your HLQ>.ORDERS (ID);

ALTER TABLE <Your HLQ>.ORDERS
    ADD CONSTRAINT FK_ORDERS_USER
        FOREIGN KEY (USER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE SET NULL;

-- ==============================================================
-- ORDER_ADDRESSES - Immutable address snapshots per order
-- ==============================================================
CREATE TABLE <Your HLQ>.ORDER_ADDRESSES
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    ORDER_ID         BIGINT       NOT NULL,
    TYPE             VARCHAR(10)  NOT NULL,
    FULL_NAME        VARCHAR(80)  NOT NULL,
    LINE1            VARCHAR(64)  NOT NULL,
    LINE2            VARCHAR(64),
    CITY             VARCHAR(64)  NOT NULL,
    REGION           VARCHAR(64),
    POSTAL_CODE      VARCHAR(16)  NOT NULL,
    COUNTRY_CODE     CHAR(2)      NOT NULL DEFAULT 'US',
    PHONE            VARCHAR(30),
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_ORDER_ADDRESSES
        PRIMARY KEY (ID),
    CONSTRAINT CK_ORDADDR_TYPE
        CHECK (TYPE IN ('billing', 'shipping'))
  )
  IN ECOMDB01.TSORDADR
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXORDADR 
    ON <Your HLQ>.ORDER_ADDRESSES (ID);

CREATE UNIQUE INDEX <Your HLQ>.IXORDTYPE 
    ON <Your HLQ>.ORDER_ADDRESSES (ORDER_ID, TYPE);

ALTER TABLE <Your HLQ>.ORDER_ADDRESSES
    ADD CONSTRAINT UQ_ORDER_ADDRESS_TYPE
        UNIQUE (ORDER_ID, TYPE);

ALTER TABLE <Your HLQ>.ORDER_ADDRESSES
    ADD CONSTRAINT FK_ORDADDR_ORDER
        FOREIGN KEY (ORDER_ID) 
        REFERENCES <Your HLQ>.ORDERS (ID)
        ON DELETE CASCADE;

-- Add foreign keys from ORDERS to ORDER_ADDRESSES
ALTER TABLE <Your HLQ>.ORDERS
    ADD CONSTRAINT FK_ORDERS_BILLADDR
        FOREIGN KEY (BILLING_ADDRESS_ID)
        REFERENCES <Your HLQ>.ORDER_ADDRESSES (ID)
        ON DELETE RESTRICT;

ALTER TABLE <Your HLQ>.ORDERS
    ADD CONSTRAINT FK_ORDERS_SHIPADDR
        FOREIGN KEY (SHIPPING_ADDRESS_ID)
        REFERENCES <Your HLQ>.ORDER_ADDRESSES (ID)
        ON DELETE RESTRICT;

-- ==============================================================
-- ORDER_ITEMS - Snapshot of items in orders
-- ==============================================================
CREATE TABLE <Your HLQ>.ORDER_ITEMS
  (
    ID               BIGINT       NOT NULL
                                  GENERATED ALWAYS AS IDENTITY
                                  (START WITH 1 INCREMENT BY 1
                                   CACHE 20 NO CYCLE NO ORDER),
    ORDER_ID         BIGINT       NOT NULL,
    INVENTORY_ID     BIGINT       NOT NULL,
    SELLER_ID        BIGINT       NOT NULL,
    SKU              VARCHAR(100) NOT NULL,
    PRODUCT_NAME     VARCHAR(255) NOT NULL,
    UNIT_PRICE_CENTS INT          NOT NULL,
    CURRENCY_CODE    CHAR(3)      NOT NULL DEFAULT 'USD',
    QUANTITY         INT          NOT NULL DEFAULT 1,
    TOTAL_CENTS      INT          NOT NULL,
    CREATED_AT       TIMESTAMP    NOT NULL WITH DEFAULT,
    CONSTRAINT PK_ORDER_ITEMS
        PRIMARY KEY (ID)
  )
  IN ECOMDB01.TSORDITM
  CCSID UNICODE;

CREATE UNIQUE INDEX <Your HLQ>.IXORDITM 
    ON <Your HLQ>.ORDER_ITEMS (ID);

ALTER TABLE <Your HLQ>.ORDER_ITEMS
    ADD CONSTRAINT FK_ORDITM_ORDER
        FOREIGN KEY (ORDER_ID) 
        REFERENCES <Your HLQ>.ORDERS (ID)
        ON DELETE CASCADE;

ALTER TABLE <Your HLQ>.ORDER_ITEMS
    ADD CONSTRAINT FK_ORDITM_INVTRY
        FOREIGN KEY (INVENTORY_ID) 
        REFERENCES <Your HLQ>.INVENTORY (ID)
        ON DELETE RESTRICT;

ALTER TABLE <Your HLQ>.ORDER_ITEMS
    ADD CONSTRAINT FK_ORDITM_SELLER
        FOREIGN KEY (SELLER_ID) 
        REFERENCES <Your HLQ>.USERS (ID)
        ON DELETE RESTRICT;

-- ==============================================================
-- END OF E03TABLE.sql
-- ==============================================================
