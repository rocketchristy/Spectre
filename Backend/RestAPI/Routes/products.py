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