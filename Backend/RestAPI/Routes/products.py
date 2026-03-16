from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.products_dao import ProductsDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.Utilities.utilities import get_token_header
from pydantic import BaseModel

router = APIRouter()


@router.get("/test", status_code=status.HTTP_200_OK)
def test_code(request: Request):
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    info = productsdao.get_products()
    return info

@router.get("/", status_code = status.HTTP_200_OK)
def get_products(request: Request):
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    result = productsdao.get_products()
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve products")
        raise HTTPException(
            status_code= status.HTTP_404_BAD_REQUEST,
            detail = "Failed to retrieve products"
        )
    return result.get("output")

@router.get("/{sku}", status_code = status.HTTP_200_OK)
def get_specific_products(request: Request, sku: str):
    pool = request.app.state.db_pool
    productsdao = ProductsDAO(pool)
    if len(sku) == 6 or len(sku) == 9:
        series_code = sku[0:1]
        style_code = sku[1:2]
        serial_number = sku[2:6]
    else:
        logger.error(f"Invalid sku number")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Invalid SKU number"
        )
    if len(sku) == 6:
        result = productsdao.get_specific_product_set(series_code, style_code, serial_number)
        if result.get("status") == "error":
            logger.error(f"Failed to retrieve product info")
            print(result.get("reason"))
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Failed to retrieve product info"
            )
    elif len(sku) == 9:
        modifier_code = sku[6:10]
        result = productsdao.get_specific_product(series_code, style_code, serial_number, modifier_code)
        if result.get("status") == "error":
            logger.error(f"Failed to retrieve product info")
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Failed to retrieve product info"
            )
    return result.get("output")