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
from Backend.Utilities.utilities import get_token_header
from pydantic import BaseModel

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_cart(request: Request, token: str = Depends(get_token_header)):
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve userid"
        )
    user_id = info.get("USER_ID")
    cartdao = CartDAO(pool)
    result = cartdao.get_cart(user_id)
    
    if result.get("status") == "error":
        logger.error(f"Failed to retrieve cart: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )
    
    return result.get("output")

@router.post("/item", status_code=status.HTTP_201_CREATED)
def add_item(request: Request, token: str = Depends(get_token_header)):
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    cartdao = CartDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve userid"
        )
    user_id = info.get("USER_ID")
    result = cartdao.get_cart(user_id)
    cart_id = result
    print(cart_id)
    #result_1 = cartdao.add_item(cart_id, inventory_id, quantity, unit_price_cents, currency_code)
