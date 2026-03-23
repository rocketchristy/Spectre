"""
================================================================================
File: products.py
Description: Product catalog API endpoints
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module defines FastAPI routes for product catalog browsing including
retrieving all products, product modifiers, and specific product variants.
Uses configuration-based SKU parsing for flexible product identification.
================================================================================
"""

from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.products_dao import ProductsDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.Utilities.utilities import get_token_header
from pydantic import BaseModel
import configparser

# Load SKU configuration
config = configparser.ConfigParser()
config.read('Backend/DatabaseAccess/config.ini')
SERIES_LENGTH = int(config['sku']['series_length'])
STYLE_LENGTH = int(config['sku']['style_length'])
SERIAL_LENGTH = int(config['sku']['serial_length'])
MODIFIER_LENGTH = int(config['sku']['modifier_length'])
MIN_SKU_LENGTH = SERIES_LENGTH + STYLE_LENGTH + SERIAL_LENGTH
FULL_SKU_LENGTH = MIN_SKU_LENGTH + MODIFIER_LENGTH

router = APIRouter()


@router.get("/", status_code = status.HTTP_200_OK)
def get_product_types(request: Request):
    """
    Retrieve all product types with SKU, price, and description.
    
    Response:
        200 OK: Array of product types with SKU, BASE_PRICE_CENTS, DESCRIPTION
        500 Internal Server Error: Database error
    
    Authentication:
        None required (public endpoint)
    
    Notes:
        Returns all base product types (without modifiers)
        SKU format: SERIES_CODE + STYLE_CODE + SERIAL_NUMBER
        Used for product catalog browsing
    """
    logger.info("Attempting to retrieve all products")
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    result = productsdao.get_product_types()
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve products: {result.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Failed to retrieve products"
        )
    logger.info(f"Successfully retrieved {len(result.get('output', []))} products")
    return result.get("output")

@router.get("/modifier/{style_code}", status_code = status.HTTP_200_OK)
def get_product_types(request: Request, style_code: str):
    """
    Retrieve active modifiers for a specific product style.
    
    Path Parameters:
        style_code (str): Product style code
    
    Response:
        200 OK: Array of modifiers with MODIFIER_CODE, DESCRIPTION, PRICE_MULTIPLIER
        500 Internal Server Error: Database error
    
    Authentication:
        None required (public endpoint)
    
    Notes:
        Returns only active modifiers (IS_ACTIVE = 'Y')
        Modifiers represent variants like colorways or special editions
        Price multiplier used to calculate variant-specific pricing
        TODO: Add validation for style_code format
    """
    logger.info("Attempting to retrieve all products")
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    #TODO add error checking for style code
    result = productsdao.get_modifiers(style_code)
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve product modifier: {result.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Failed to retrieve product modifier"
        )
    logger.info(f"Successfully retrieved {len(result.get('output', []))} product modifier")
    return result.get("output")

@router.get("/{sku}", status_code = status.HTTP_200_OK)
def get_specific_products(request: Request, sku: str):
    """
    Retrieve product details by SKU - supports partial or complete SKU.
    
    Path Parameters:
        sku (str): Product SKU - either:
                   - MIN_SKU_LENGTH chars (series+style+serial) - returns all variants
                   - FULL_SKU_LENGTH chars (includes modifier) - returns specific variant
    
    Response:
        200 OK: Array of product variant(s) with full details:
                SKU, SERIES_NAME, STYLE_NAME, PRODUCT_NAME, MODIFIER_NAME,
                BASE_PRICE_CENTS, URL (image)
        404 Not Found: Invalid SKU format or product not found
    
    Authentication:
        None required (public endpoint)
    
    Notes:
        Partial SKU (MIN length): Returns all color/edition variants of product
        Complete SKU (FULL length): Returns single specific variant
        SKU parsing uses config.ini for field lengths
        Validates SKU length before processing
        Used for product detail pages and variant selection
    """
    logger.info(f"Attempting to retrieve product(s) with SKU: {sku}")
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    
    # Parse SKU using config values
    series_end = SERIES_LENGTH
    style_end = series_end + STYLE_LENGTH
    serial_end = style_end + SERIAL_LENGTH
    
    if len(sku) == MIN_SKU_LENGTH or len(sku) == FULL_SKU_LENGTH:
        series_code = sku[0:series_end]
        style_code = sku[series_end:style_end]
        serial_number = sku[style_end:serial_end]
    else:
        logger.error(f"Invalid sku number: {sku}")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = f"Invalid SKU number - must be {MIN_SKU_LENGTH} or {FULL_SKU_LENGTH} characters"
        )
    
    if len(sku) == MIN_SKU_LENGTH:
        logger.info(f"Retrieving product set for SKU: {sku}")
        result = productsdao.get_specific_product_set(series_code, style_code, serial_number)
        if result.get("status") == "error":
            logger.error(f"Failed to retrieve product set: {result.get('reason')}")
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Failed to retrieve product info"
            )
    elif len(sku) == FULL_SKU_LENGTH:
        logger.info(f"Retrieving specific product for SKU: {sku}")
        modifier_code = sku[serial_end:]
        result = productsdao.get_specific_product(series_code, style_code, serial_number, modifier_code)
        if result.get("status") == "error":
            logger.error(f"Failed to retrieve specific product: {result.get('reason')}")
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Failed to retrieve product info"
            )
    
    logger.info(f"Successfully retrieved product(s) for SKU: {sku}")
    return result.get("output")