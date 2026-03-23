"""
================================================================================
File: orders.py
Description: Order history API endpoints
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module defines FastAPI routes for viewing order history. Retrieves
complete order information including order details, items, and product
information via multi-table JOIN.
================================================================================
"""

from fastapi import APIRouter, Body
from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.orders_dao import OrdersDAO
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.Utilities.utilities import get_token_header
from pydantic import BaseModel

router = APIRouter()

@router.get("/me", status_code=status.HTTP_200_OK)
def get_my_orders(request: Request, token: str = Depends(get_token_header)):
    """
    Retrieve authenticated user's complete order history.
    
    Request Headers:
        Authorization: Bearer <token>
    
    Response:
        200 OK: Array of orders with complete details including:
                - Order info (ID, totals, status, timestamps)
                - Order items (quantity, price, SKU)
                - Product details (series, style, variant, color, size, condition)
        401 Unauthorized: Invalid or expired token (implied by get_token_header)
        404 Not Found: User not found
        500 Internal Server Error: Database error
    
    Authentication:
        Required - Bearer token in Authorization header
    
    Notes:
        Returns orders sorted by creation date (newest first)
        Includes full product details via 10-table JOIN
        Used for order history and tracking
    """
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
    ordersdao = OrdersDAO(pool)
    result = ordersdao.get_user_orders(user_id)

    if result.get("status") == "error":
        logger.error(f"Failed to retrieve orders: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )
    
    return result.get("output")