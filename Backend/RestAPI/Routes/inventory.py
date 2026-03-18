from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.inventory_dao import InventoryDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.Utilities.utilities import get_token_header
from Backend.Utilities.validation import InventoryItemRequest
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

router = APIRouter()

@router.get("/", status_code= status.HTTP_200_OK)
def get_all_inventory(request: Request):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    result = inventorydao.get_inventory()
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve inventory: {result.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Failed to retrieve inventory"
        )
    return result.get("output")

@router.get("/me", status_code=status.HTTP_200_OK)
def get_user_inventory(request: Request,  token: str = Depends(get_token_header)):
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    userdao = UserDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve userid"
        )
    user_id = info.get("output")[0]["USER_ID"]
    result = inventorydao.get_user_inventory(user_id)
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve inventory")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve inventory"
        )
    return result.get("output")

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_item(request: Request, payload: InventoryItemRequest, token: str = Depends(get_token_header)):
    logger.info("Attempting to add inventory item")
    
    # Parse SKU
    sku = payload.sku
    if len(sku) < MIN_SKU_LENGTH:
        logger.error(f"Invalid SKU format: {sku}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SKU format - must be at least {MIN_SKU_LENGTH} characters"
        )
    
    # Parse SKU using config values
    series_end = SERIES_LENGTH
    style_end = series_end + STYLE_LENGTH
    serial_end = style_end + SERIAL_LENGTH
    
    series_code = sku[0:series_end]
    style_code = sku[series_end:style_end]
    serial_number = sku[style_end:serial_end]
    modifier_code = sku[serial_end:] if len(sku) > serial_end else ""
    quantity = payload.quantity
    unit_price_cents = payload.unitPriceCents 
    currency_code = payload.currencyCode
    
    # Get database connections
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    inventorydao = InventoryDAO(pool)
    
    # Get user ID from token
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve user ID from token: {info.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if len(info.get("output", [])) == 0:
        logger.error("User ID not found for token")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_id = info.get("output")[0]["USER_ID"]
    logger.info(f"Adding inventory for user ID: {user_id}, SKU: {sku}")
    logger.info(f"{series_code}, {style_code}, {serial_number}, {modifier_code}")
    # Check if inventory item already exists
    result = inventorydao.get_sku_details(user_id, series_code, style_code, serial_number, modifier_code)
    
    if result.get("status") == "error":
        logger.error(f"Failed to check existing inventory: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check existing inventory"
        )
    
    # Add or update inventory
    if len(result.get("output", [])) == 0:
        # Item doesn't exist, add new inventory
        logger.info(f"Adding new inventory item for SKU: {sku}")
        result_1 = inventorydao.add_inventory(
            user_id, series_code, style_code, serial_number, 
            modifier_code, quantity, unit_price_cents, currency_code
        )
        
        if result_1.get("status") == "error":
            logger.error(f"Failed to add inventory: {result_1.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add inventory: {result_1.get('reason')}"
            )
        
        logger.info(f"Successfully added new inventory item for SKU: {sku}")
        return {"message": "Inventory item added successfully", "quantity": quantity}
    
    else:
        # Item exists, update quantity
        qnt = result.get("output")[0]["QUANTITY_AVAILABLE"]
        new_quantity = qnt + quantity
        logger.info(f"Updating inventory quantity from {qnt} to {new_quantity} for SKU: {sku}")
        
        result_1 = inventorydao.update_quantity(
            new_quantity, user_id, series_code, style_code, serial_number, modifier_code
        )
        
        if result_1.get("status") == "error":
            logger.error(f"Failed to update inventory quantity: {result_1.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update inventory: {result_1.get('reason')}"
            )
        
        logger.info(f"Successfully updated inventory quantity for SKU: {sku}")
        return {"message": "Inventory quantity updated successfully", "new_quantity": new_quantity}

@router.delete("/me/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(request: Request, inventory_id: int, token: str = Depends(get_token_header)):
    logger.info(f"Attempting to delete inventory item {inventory_id}")
    pool = request.app.state.db_pool
    inventorydao = InventoryDAO(pool)
    userdao = UserDAO(pool)
    
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve user ID: {info.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = info.get("output")[0]["USER_ID"]
    logger.info(f"Deleting inventory item {inventory_id} for user {user_id}")
    
    inventory_result = inventorydao.remove_user_inventory(user_id, inventory_id)
    
    if inventory_result.get("status") == "error":
        logger.error(f"Failed to delete inventory item {inventory_id}: {inventory_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found or you don't have permission to delete it"
        )
    
    logger.info(f"Successfully deleted inventory item {inventory_id}")
    return {"message": "Inventory item deleted successfully"}

