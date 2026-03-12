from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.inventory_dao import InventoryDAO, LoginDAO
from Backend.Utilities.utilities import get_token_header
from pydantic import BaseModel

router = APIRouter()

@router.get("/test", status_code=status.HTTP_200_OK)
def test_code(request: Request):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    info = inventorydao.test()
    return info

@router.get("/products", status_code = status.HTTP_200_OK)
def get_products(request: Request):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    result = inventorydao.get_products()
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve products")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve products"
        )
    return result.get("output")

@router.get("/products/{sku}", status_code = status.HTTP_200_OK)
def get_specific_products(request: Request, sku: int):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    result = inventorydao.get_specific_products(sku)
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve product info")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve product info"
        )
    return result.get("output")

@router.get("/inventory", status_code= status.HTTP_200_OK)
def get_all_inventory(request: Request):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    result = inventorydao.get_inventory()
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve inventory")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve inventory"
        )
    return result.get("output")

@router.get("/inventory/me", status_code=status.HTTP_201_CREATED)
def get_user_inventory(request: Request,  token: str = Depends(get_token_header)):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    logindao = LoginDAO(pool)
    info = logindao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve userid"
        )
    user_id = info.get("USER_ID")
    result = inventorydao.get_user_inventory(user_id)
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve inventory")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve inventory"
        )
    return result.get("output")

class InventoryItemRequest(BaseModel):
    sku: str
    quantity: str
    unitPriceCents: str
    currencyCode: str

@router.post("/inventory", status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: InventoryItemRequest, token):
    # TODO add inventory code
    # get user id 
    # break up sku into parts
    # check quantity of existing product (based on seller id and sku) get_sku_details
    # update quantity if existing update_quantity
    # add to inventory if not add_product

    return {"message": "User registered successfully"}

