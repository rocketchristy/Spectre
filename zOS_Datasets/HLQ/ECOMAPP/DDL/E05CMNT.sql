--********************************************************************
--* MEMBER  : E05CMNT
--* PURPOSE : Add documentation comments to ECOMDB01 database
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
--*   - COMMENT ON TABLE and COMMENT ON COLUMN statements provide
--*     in-database documentation visible through catalog queries
--********************************************************************

-- ==============================================================
-- TABLE COMMENTS
-- ==============================================================

COMMENT ON TABLE <Your HLQ>.USERS
    IS 'Application users. Can act as buyer and/or seller.';

COMMENT ON TABLE <Your HLQ>.TOKENS
    IS 'Authentication tokens linked to users.';

COMMENT ON TABLE <Your HLQ>.SERIES
    IS 'First character of SKU. Defines major product series.';

COMMENT ON TABLE <Your HLQ>.STYLES
    IS 'Second character of SKU. Defines product style/category.';

COMMENT ON TABLE <Your HLQ>.PRODUCT_TYPES
    IS 'Product type defined by SERIES-STYLE-SERIAL. Base template.';

COMMENT ON TABLE <Your HLQ>.PRODUCT_VARIANTS
    IS 'Concrete SKU: SERIES-STYLE-SERIAL-MODIFIER. Sellable unit.';

COMMENT ON TABLE <Your HLQ>.VARIANT_IMAGES
    IS 'Images for specific product variants, ordered by sort.';

COMMENT ON TABLE <Your HLQ>.INVENTORY
    IS 'Seller listings. Each seller can list same SKU separately.';

COMMENT ON TABLE <Your HLQ>.CARTS
    IS 'Shopping cart per user. Converts to order at checkout.';

COMMENT ON TABLE <Your HLQ>.CART_ITEMS
    IS 'Cart line items. References inventory listing directly.';

COMMENT ON TABLE <Your HLQ>.ADDRESSES
    IS 'User addresses. Can be used as template for orders.';

COMMENT ON TABLE <Your HLQ>.ORDERS
    IS 'Order header. Addresses stored as snapshots in ORDER_ADDR.';

COMMENT ON TABLE <Your HLQ>.ORDER_ADDRESSES
    IS 'Immutable address snapshots per order (billing, shipping).';

COMMENT ON TABLE <Your HLQ>.ORDER_ITEMS
    IS 'Order lines with SKU, seller, price snapshots at purchase.';

-- ==============================================================
-- COLUMN COMMENTS - USERS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.USERS.IS_ACTIVE
    IS 'Y = active, N = suspended/soft-deleted.';

COMMENT ON COLUMN <Your HLQ>.USERS.HASHED_PASSWORD
    IS 'Password hash. 255 chars supports Argon2/bcrypt/scrypt.';

COMMENT ON COLUMN <Your HLQ>.USERS.PASSWORD_ALG
    IS 'Algorithm used: argon2id, bcrypt, scrypt, etc.';

-- ==============================================================
-- COLUMN COMMENTS - SERIES & STYLES
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.SERIES.CODE
    IS 'Single character. Examples: M=Magic, P=Pokemon, Y=YuGiOh.';

COMMENT ON COLUMN <Your HLQ>.STYLES.CODE
    IS 'Single character. Examples: C=Common, R=Rare, M=Mythic.';

-- ==============================================================
-- COLUMN COMMENTS - STYLE_MODIFIERS
-- ==============================================================

COMMENT ON TABLE <Your HLQ>.STYLE_MODIFIERS
    IS 'Valid modifiers per style (card conditions, sizes, etc).';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.STYLE_CODE
    IS 'References STYLES. Links modifiers to applicable style.';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.MODIFIER_CODE
    IS '3-character code. Examples: NMF=Near Mint Foil, MED=Medium.';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.DESCRIPTION
    IS 'Human-readable description of modifier. Max 100 chars.';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.PRICE_MULTIPLIER
    IS 'Price multiplier applied to base price 
    (e.g., 1.75 for holofoil, 0.40 for damaged).';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.DISPLAY_ORDER
    IS 'Sort order for UI display. Lower numbers appear first.';

COMMENT ON COLUMN <Your HLQ>.STYLE_MODIFIERS.IS_ACTIVE
    IS 'Y = available for selection, N = deprecated/unavailable.';

-- ==============================================================
-- COLUMN COMMENTS - PRODUCT_TYPES
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.PRODUCT_TYPES.SERIES_CODE
    IS 'First character of SKU. References SERIES table.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_TYPES.STYLE_CODE
    IS 'Second character of SKU. References STYLES table.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_TYPES.SERIAL_NUMBER
    IS 'Third segment of SKU. 4-digit serial. Example: 0001.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_TYPES.BASE_PRICE_CENTS
    IS 'Base price in cents. Multiplied by modifier price multiplier.';

-- ==============================================================
-- COLUMN COMMENTS - PRODUCT_VARIANTS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.PRODUCT_VARIANTS.SERIES_CODE
    IS 'Full SKU part 1: Series code.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_VARIANTS.STYLE_CODE
    IS 'Full SKU part 2: Style code.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_VARIANTS.SERIAL_NUMBER
    IS 'Full SKU part 3: 4-digit serial number.';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_VARIANTS.MODIFIER_CODE
    IS 'Full SKU part 4: 3-char modifier. Full SKU format: XX9999XXX';

COMMENT ON COLUMN <Your HLQ>.PRODUCT_VARIANTS.DISPLAY_NAME
    IS 'Human-readable name for this specific variant.';

-- ==============================================================
-- COLUMN COMMENTS - INVENTORY
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.INVENTORY.SELLER_ID
    IS 'Seller offering this SKU. Multiple sellers can list same.';

COMMENT ON COLUMN <Your HLQ>.INVENTORY.QUANTITY_AVAILABLE
    IS 'Units available for purchase by this seller.';

COMMENT ON COLUMN <Your HLQ>.INVENTORY.UNIT_PRICE_CENTS
    IS 'Listing price in cents. Each seller sets own price.';

-- ==============================================================
-- COLUMN COMMENTS - CARTS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.CARTS.STATUS
    IS 'active=in use, converted=checked out, abandoned=timeout.';

-- ==============================================================
-- COLUMN COMMENTS - CART_ITEMS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.CART_ITEMS.INVENTORY_ID
    IS 'References specific seller listing, not just variant.';

COMMENT ON COLUMN <Your HLQ>.CART_ITEMS.UNIT_PRICE_CENTS
    IS 'Price snapshot at time item added to cart.';

-- ==============================================================
-- COLUMN COMMENTS - ORDERS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.ORDERS.STATUS
    IS 'pending|confirmed|fulfilled|canceled|refunded.';

COMMENT ON COLUMN <Your HLQ>.ORDERS.BILLING_ADDRESS_ID
    IS 'FK to ORDER_ADDRESSES where TYPE=billing. Required after order.';

COMMENT ON COLUMN <Your HLQ>.ORDERS.SHIPPING_ADDRESS_ID
    IS 'FK to ORDER_ADDRESSES where TYPE=shipping. Required after order.';

COMMENT ON COLUMN <Your HLQ>.ORDERS.PLACED_AT
    IS 'Timestamp order confirmed. NULL while status=pending.';

-- ==============================================================
-- COLUMN COMMENTS - ORDER_ADDRESSES
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.ORDER_ADDRESSES.TYPE
    IS 'billing or shipping. One of each per order.';

COMMENT ON COLUMN <Your HLQ>.ORDER_ADDRESSES.FULL_NAME
    IS 'Snapshot: name cannot change if user updates address.';

-- ==============================================================
-- COLUMN COMMENTS - ORDER_ITEMS
-- ==============================================================

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.SKU
    IS 'Snapshot: full SKU at purchase time (format: XX9999XXX).';

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.PRODUCT_NAME
    IS 'Snapshot: product description at purchase time.';

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.SELLER_ID
    IS 'Seller who fulfilled this item. Important for payouts.';

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.UNIT_PRICE_CENTS
    IS 'Snapshot: price per unit at purchase time.';

COMMENT ON COLUMN <Your HLQ>.ORDER_ITEMS.TOTAL_CENTS
    IS 'Calculated: unit_price_cents * quantity.';


