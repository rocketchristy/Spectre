from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.cart_dao import CartDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.DatabaseAccess.products_dao import ProductsDAO
from Backend.DatabaseAccess.orders_dao import OrdersDAO
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
    
    # Check if cart exists, if not create one
    if result.get("status") == "error" or len(result.get("output", [])) == 0:
        logger.info(f"No cart found for user {user_id}, creating new cart")
        create_result = cartdao.create_cart(user_id)
        
        if create_result.get("status") == "error":
            logger.error(f"Failed to create cart: {create_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create cart"
            )
        
        # Get the newly created cart ID
        result = cartdao.get_cart_id(user_id)
        
        if result.get("status") == "error":
            logger.error(f"Failed to retrieve cart ID after creation: {result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve cart ID"
            )
    
    cart_id = result.get("output")[0]["ID"]
    inventory_id = payload.inventory_id
    quantity = payload.quantity
    unit_price_cents = payload.unit_price_cents
    currency_code = payload.currency_code
    
    # check if inventory_id exists then update quantity instead
    result_existing_cart_item = cartdao.check_existing_cart_item(cart_id, inventory_id)
    
    # Check for error
    if result_existing_cart_item.get("status") == "error":
        logger.error(f"Failed to check existing cart item: {result_existing_cart_item.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check existing cart item"
        )

    # check if output = [] then you do the add item
    if len(result_existing_cart_item.get('output', [])) == 0:
        logger.info(f"Adding new item to cart {cart_id}")
        result_1 = cartdao.add_item(cart_id, inventory_id, quantity, unit_price_cents, currency_code)
        
        if result_1.get("status") == "error":
            logger.error(f"Failed to add item to cart: {result_1.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add item to cart"
            )
    else:
        logger.info(f"Item already exists in cart, updating quantity")
        original_quantity = result_existing_cart_item.get('output')[0]["QUANTITY"]
        new_quantity = original_quantity + quantity
        result_1 = cartdao.update_quantity(result_existing_cart_item.get('output')[0]["ID"],
                                           new_quantity)
        
        if result_1.get("status") == "error":
            logger.error(f"Failed to update cart item quantity: {result_1.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cart item quantity"
            )
    
    logger.info(f"Successfully added/updated item in cart {cart_id}")
    return {"message": "Item added to cart successfully"}


@router.delete("/item/{cart_item_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_cart_item(request: Request, cart_item_id: int, token: str = Depends(get_token_header)):
    logger.info(f"Attempting to delete item {cart_item_id} from cart")
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

    result_1 = cartdao.remove_item(cart_id, cart_item_id)
    
    if result_1.get("status") == "error":
        logger.error(f"Failed to remove item from cart: {result_1.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    logger.info(f"Successfully removed item {cart_item_id} from cart {cart_id}")
    return {"message": "Successfully remove item from cart"}

class AddressRequest(BaseModel):
    billing_address_id: str
    shipping_address_id: str

@router.post("/buy", status_code=status.HTTP_200_OK)
def buy_cart(request: Request, payload: AddressRequest, token: str = Depends(get_token_header)):
    logger.info("Attempting to process cart checkout")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    
    # Get user ID from token
    info = userdao.get_user_id(token)
    if info.get("status") == "error":
        logger.error(f"Failed to retrieve user ID: {info.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user_id = info.get("output")[0]["USER_ID"]
    logger.info(f"Processing checkout for user ID: {user_id}")

    cartdao = CartDAO(pool)
    ordersdao = OrdersDAO(pool)
    productsdao = ProductsDAO(pool)
    inventorydao = InventoryDAO(pool)
    
    # Get cart contents
    cart_result = cartdao.get_cart(user_id)
    if cart_result.get("status") == "error":
        logger.error(f"Failed to retrieve cart: {cart_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )
    
    if len(cart_result.get("output", [])) == 0:
        logger.error(f"Cart is empty for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    currency_code = cart_result.get("output")[0]["CURRENCY_CODE"]
    billing_address_id = payload.billing_address_id
    shipping_address_id = payload.shipping_address_id
    logger.info(f"Billing address: {billing_address_id}, Shipping address: {shipping_address_id}")
    
    # Check and add billing address to order addresses
    billing_order_result = ordersdao.check_address_in_order(billing_address_id)
    
    if billing_order_result.get("status") == "error":
        logger.error(f"Failed to check billing address: {billing_order_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate billing address"
        )
    
    if len(billing_order_result.get("output", [])) == 0 or billing_order_result.get("output")[0]["ID"] == None:
        logger.info(f"Adding billing address {billing_address_id} to order addresses")
        add_billing_result = ordersdao.add_order_address(billing_order_result.get("output")[0]["FULL_NAME"], 
                                                         billing_order_result.get("output")[0]["LINE1"], 
                                                         billing_order_result.get("output")[0]["LINE2"],
                                                         billing_order_result.get("output")[0]["CITY"],
                                                         billing_order_result.get("output")[0]["REGION"],
                                                         billing_order_result.get("output")[0]["POSTAL_CODE"],
                                                         billing_order_result.get("output")[0]["COUNTRY_CODE"],
                                                         billing_order_result.get("output")[0]["PHONE"])
        if add_billing_result.get("status") == "error":
            logger.error(f"Failed to add billing address: {add_billing_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add billing address"
            )
        billing_order_result = ordersdao.check_address_in_order(billing_address_id)
    
    billing_order_address_id = billing_order_result.get("output")[0]["ID"]
    
    # Check and add shipping address to order addresses
    shipping_order_result = ordersdao.check_address_in_order(shipping_address_id)
    if shipping_order_result.get("status") == "error":
        logger.error(f"Failed to check shipping address: {shipping_order_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate shipping address"
        )
    
    if len(shipping_order_result.get("output", [])) == 0 or shipping_order_result.get("output")[0]["ID"] == None:
        logger.info(f"Adding shipping address {shipping_address_id} to order addresses")
        add_shipping_result = ordersdao.add_order_address(shipping_order_result.get("output")[0]["FULL_NAME"], 
                                                         shipping_order_result.get("output")[0]["LINE1"], 
                                                         shipping_order_result.get("output")[0]["LINE2"],
                                                         shipping_order_result.get("output")[0]["CITY"],
                                                         shipping_order_result.get("output")[0]["REGION"],
                                                         shipping_order_result.get("output")[0]["POSTAL_CODE"],
                                                         shipping_order_result.get("output")[0]["COUNTRY_CODE"],
                                                         shipping_order_result.get("output")[0]["PHONE"])
        if add_shipping_result.get("status") == "error":
            logger.error(f"Failed to add shipping address: {add_shipping_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add shipping address"
            )
        shipping_order_result = ordersdao.check_address_in_order(shipping_address_id)
    
    shipping_order_address_id = shipping_order_result.get("output")[0]["ID"]

    # Create order
    logger.info(f"Creating order for user {user_id}")
    order_result = ordersdao.add_order(user_id, currency_code, 0,
                            billing_order_address_id, shipping_order_address_id)
    if order_result.get("status") == "error":
        logger.error(f"Failed to create order: {order_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )
    
    # Get order ID
    order_result_1 = ordersdao.get_order_id(user_id)
    if order_result_1.get("status") == "error":
        logger.error(f"Failed to retrieve order ID: {order_result_1.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order ID"
        )
    
    order_id = order_result_1.get("output")[0]["ID"]
    logger.info(f"Order created with ID: {order_id}")
    
    total_cost = 0
    
    # Process each cart item
    for i in range(len(cart_result.get("output"))):
        series_code = cart_result.get("output")[i]["SERIES_CODE"]
        style_code = cart_result.get("output")[i]["STYLE_CODE"]
        serial_number = cart_result.get("output")[i]["SERIAL_NUMBER"]
        modifier_code = cart_result.get("output")[i]["MODIFIER_CODE"]
        seller_id = cart_result.get("output")[i]["SELLER_ID"]
        sku = cart_result.get("output")[i]["SKU"]
        
        logger.info(f"Processing cart item {i+1}: SKU {sku}, Seller {seller_id}")
        
        # Get inventory details
        inventory_result = inventorydao.get_sku_details(seller_id, series_code, style_code, serial_number, modifier_code)
        if inventory_result.get("status") == "error":
            logger.error(f"Failed to get inventory details for SKU {sku}: {inventory_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve inventory for SKU {sku}"
            )
        
        if len(inventory_result.get("output", [])) == 0:
            logger.error(f"Inventory not found for SKU {sku}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory not found for SKU {sku}"
            )
        
        quantity_available = inventory_result.get("output")[0]["QUANTITY_AVAILABLE"]
        quantity_requested = cart_result.get("output")[i]["QUANTITY"]
        
        # Check if sufficient inventory available
        if quantity_requested > quantity_available:
            logger.error(f"Insufficient inventory for SKU {sku}: requested {quantity_requested}, available {quantity_available}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory for SKU {sku}. Only {quantity_available} available",
                headers={"X-SKU": sku, "X-Available-Quantity": str(quantity_available)}
            )
        
        # Update inventory quantity
        new_quantity = quantity_available - quantity_requested
        logger.info(f"Updating inventory for SKU {sku}: {quantity_available} -> {new_quantity}")
        
        update_result = inventorydao.update_quantity(new_quantity, seller_id, series_code, style_code, serial_number, modifier_code)
        if update_result.get("status") == "error":
            logger.error(f"Failed to update inventory for SKU {sku}: {update_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update inventory for SKU {sku}"
            )
        
        # Add order item
        unit_price_cents = cart_result.get("output")[i]["UNIT_PRICE_CENTS"]
        inventory_id = cart_result.get("output")[i]["INVENTORY_ID"]
        product_name = cart_result.get("output")[i]["PRODUCT_NAME"]
        quantity = cart_result.get("output")[i]["QUANTITY"]
        
        logger.info(f"Adding order item: {product_name} x{quantity} @ {unit_price_cents} cents")
        
        add_item_result = ordersdao.add_order_item(order_id, inventory_id, seller_id, 
                       sku, product_name, unit_price_cents,
                       currency_code, quantity)
        if add_item_result.get("status") == "error":
            logger.error(f"Failed to add order item for SKU {sku}: {add_item_result.get('reason')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add order item for SKU {sku}"
            )
        
        total_cost += (unit_price_cents) * quantity_requested

    # Update order total cost
    logger.info(f"Updating order {order_id} total cost: {total_cost} cents")
    update_cost_result = ordersdao.update_order_cost(total_cost, order_id)
    if update_cost_result.get("status") == "error":
        logger.error(f"Failed to update order cost: {update_cost_result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order total"
        )
    
    # Clear cart
    logger.info(f"Removing cart for user {user_id}")
    clear_cart_result = cartdao.remove_entire_cart(user_id)
    if clear_cart_result.get("status") == "error":
        logger.warning(f"Failed to clear cart: {clear_cart_result.get('reason')}")
        # Don't fail the whole checkout if cart clearing fails
    
    logger.info(f"Checkout completed successfully for user {user_id}, order {order_id}")
    return {"message": "Order placed successfully", "order_id": order_id, "total_cost": total_cost}
    