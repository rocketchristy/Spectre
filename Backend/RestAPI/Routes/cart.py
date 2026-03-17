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

class AddressRequest(BaseModel):
    billing_address_id: str
    shipping_address_id: str

@router.post("/buy", status_code=status.HTTP_200_OK)
def buy_cart(request: Request, payload: AddressRequest, token: str = Depends(get_token_header)):
    #
    # also pass an address id 
    # take in token --> userid --> 
    # 
    # update orderform --> 
    # 
    # update quantity of inventory --> 
    # 
    # delete cart
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve userid")
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail = "Failed to retrieve userid"
        )
    user_id = info.get("output")[0]["USER_ID"]

    cartdao = CartDAO(pool)
    ordersdao = OrdersDAO(pool)
    productsdao = ProductsDAO(pool)

    cart_result = cartdao.get_cart(user_id)

    # create order in orders table here (dont update price yet)
    #get order id to add to 
    # get variant id from product_variants
    currency_code = result.get("output")[0]["CURRENCY_CODE"]
    billing_address_id = payload.billing_address_id
    shipping_address_id = payload.shipping_address_id
    order_result = ordersdao.add_order(user_id, currency_code, 0,
                            billing_address_id, shipping_address_id)
    
    order_result_1 = ordersdao.get_order_id(user_id) 
    order_id = order_result_1.get("output")[0]["ID"]
    total_cost = 0
    for i in range(len(cart_result)):
        # udate quantity
        inventory_result = inventorydao.get_sku_details(seller_id, series_code, serial_number, modifier_code)
        quantity_available = result_1.get("output")[0]["QUANTITY_AVAILABLE"]
        quantity_requested = cart_result.get("output")[i]["QUANTITY"]
        # check if plenty available

        # add order to placed order
        #series_code = cart_result.get("output")[i]["SERIES_CODE"]
        #style_code = cart_result.get("output")[i]["STYLE_CODE"]
        #serial_number = cart_result.get("output")[i]["SERIAL_NUMBER"]
        #modifier_code = cart_result.get("output")[i]["MODIFIER_CODE"]
        # may just be called sku actually
        #sku = series_code + style_code + serial_number + modifier_code
        sku = cart_result.get("output")[i]["SKU"]
        product_result = productsdao.get_product_variant_ids(sku) --> variant_id, product_id
        variant_id = product_result.get("output")[0]["ID"]
        product_id = product_result.get("output")[0]["PRODUCT_ID"]
        seller_id = cart_result.get("output")[i]["SELLER_ID"]
        unit_price_cents = cart_result.get("output")[i]["UNIT_PRICE_CENTS"]

        ordersdao.add_order_item(order_id, variant_id, product_id,
                    seller_user_id, sku, product_name, unit_price_cents)
        

        total_cost += unit_price_cents

    ordersdao.update_order_cost()
    cartdao.remove_entire_cart(user_id)
    '''