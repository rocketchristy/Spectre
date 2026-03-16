#TODO: /cart get all of shopping cart given token
# delete item in cart based on id

# TODO get past orders 

# TODO checkout from cart 
'''take in token --> userid --> update orderform --> update quantity of inventory --> delete cart'''

from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.cart_dao import CartDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.DatabaseAccess.inventory_dao import InventoryDAO
from Backend.Utilities.utilities import get_token_header
from Backend.Utilities.validation import CartItemRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_cart(request: Request, token: str = Depends(get_token_header)):
    logger.info("Attempting to retrieve cart")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid: {info.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )
    user_id = info.get("output")[0]["USER_ID"]
    logger.info(f"Retrieving cart for user ID: {user_id}")
    cartdao = CartDAO(pool)
    result = cartdao.get_cart(user_id)
    
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve cart: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )
    
    logger.info(f"Successfully retrieved cart for user ID: {user_id}")
    return result.get("output")

@router.post("/item", status_code=status.HTTP_201_CREATED)
def add_item(request: Request, payload: CartItemRequest, token: str = Depends(get_token_header)):
    logger.info("Attempting to add item to cart")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    cartdao = CartDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid: {info.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )
    user_id = info.get("output")[0]["USER_ID"]
    result = cartdao.get_cart_id(user_id)
    
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve cart ID: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart ID"
        )
    
    cart_id = result.get("output")[0]["ID"]
    inventory_id = payload.inventory_id
    quantity = payload.quantity
    unit_price_cents = payload.unit_price_cents
    currency_code = payload.currency_code
    
    result_1 = cartdao.add_item(cart_id, inventory_id, quantity, unit_price_cents, currency_code)
    
    if result_1.get("status") == "error":
        logger.error(f"Failed to add item to cart: {result_1.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )
    
    logger.info(f"Successfully added item to cart {cart_id}")
    return {"message": "Item added to cart successfully"}


@router.delete("/item/{inventory_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_cart_item(request: Request, inventory_id: int, token: str = Depends(get_token_header)):
    logger.info(f"Attempting to delete item {inventory_id} from cart")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    cartdao = CartDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid: {info.get('reason')}")
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )
    user_id = info.get("output")[0]["USER_ID"]
    result = cartdao.get_cart_id(user_id)
    
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve cart ID: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart ID"
        )
    
    cart_id = result.get("output")[0]["ID"]

    result_1 = cartdao.remove_item(cart_id, inventory_id)
    
    if result_1.get("status") == "error":
        logger.error(f"Failed to remove item from cart: {result_1.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    logger.info(f"Successfully removed item {inventory_id} from cart {cart_id}")
    return {"message": "Successfully remove item from cart"}
'''
@router.post("/buy", status_code=status.HTTP_200_OK)
def buy_cart():
    #
    # also pass an address id 
    # take in token --> userid --> 
    # 
    # update orderform --> 
    # 
    # update quantity of inventory --> 
    # 
    # delete cart

    '''