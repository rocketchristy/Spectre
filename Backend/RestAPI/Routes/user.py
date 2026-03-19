"""
================================================================================
File: user.py
Description: User authentication and profile management API endpoints
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module defines FastAPI routes for user authentication (login/register),
profile management (get/update user data), and address management (add/delete
addresses). All endpoints except login and register require authentication via
bearer token.
================================================================================
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.DatabaseAccess.cart_dao import CartDAO
from Backend.Utilities.utilities import hash_password, get_token_header
from Backend.Utilities.validation import LoginRequest, RegisterRequest, UpdateUserRequest, AddressRequest
from pydantic import BaseModel

router = APIRouter()

@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, payload: LoginRequest):
    """
    Authenticate user with email and password.
    
    Request Body:
        email (str): User's email address
        password (str): User's password (will be hashed)
    
    Response:
        200 OK: {"token": str, "first_name": str}
        401 Unauthorized: Invalid email or password
        500 Internal Server Error: Database error
    
    Authentication:
        None required (public endpoint)
    
    Notes:
        Password is hashed using SHA-256 before comparison
        On success, creates new token and returns latest token ID
        Token is used for subsequent authenticated requests
    """
    email = payload.email
    password = payload.password
    password_hash = hash_password(password)
    logger.info("Attempted login by " + email)
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user(email)
    
    if result.get("status") == "error":
        logger.info(f"Failed to login : {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("reason")
        )
    
    if result.get("output") == []:
        logger.info(f"Invalid logon attempt from {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    
    if result.get("output")[0]["HASHED_PASSWORD"] != password_hash:
        logger.info(f"Invalid Password attempt from {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    logger.info(f"Valid login from {email}")
    userdao.add_token(result.get("output")[0]["ID"])
    result_token = userdao.get_token(email)
    return {
        "token": result_token.get("output")[-1]['ID'],
        "first_name": result.get("output")[-1]['FIRST_NAME']
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: RegisterRequest):
    """
    Register a new user account.
    
    Request Body:
        email (str): User's email address (must be unique)
        password (str): User's password (will be hashed)
        first_name (str): User's first name
        last_name (str): User's last name
    
    Response:
        201 Created: {"message": "User registered successfully"}
        400 Bad Request: Email already exists or invalid data
        500 Internal Server Error: Database error
    
    Authentication:
        None required (public endpoint)
    
    Side Effects:
        Creates new user in USERS table
        Automatically creates empty cart for new user
        Password is hashed using SHA-256 before storage
    
    Notes:
        Email must be unique (enforced by database)
        Cart creation is automatic (required for shopping functionality)
    """
    # TODO create a cart too
    email = payload.email
    password = payload.password
    password_hash = hash_password(password)
    first_name = payload.first_name
    last_name = payload.last_name
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    cartdao = CartDAO(pool)
    result = userdao.add_user(email, password_hash, first_name, last_name)
    if result.get("status") == "error":
        logger.info(f"Failed to register email: {result.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("reason")
        )
    
    result_1 = userdao.get_user(email)
    if result_1.get("status") == "error":
        logger.error(f"Failed to retrieve user after registration: {result_1.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registered but failed to retrieve user data"
        )
    
    if len(result_1.get("output")) == 0:
        logger.error(f"User not found after registration: {email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registered but not found"
        )
    
    user_id = result_1.get("output")[0]["ID"]
    result_2 = cartdao.create_cart(user_id)
    
    if result_2.get("status") == "error":
        logger.error(f"Failed to create cart for user ID {user_id}: {result_2.get('reason')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registered but failed to create cart"
        )
    
    logger.info(f"Register user {email} successfully")
    return {"message": "User registered successfully"}

@router.get("/", status_code=status.HTTP_200_OK)
def get_user_data(request: Request, token: str = Depends(get_token_header)):
    """
    Retrieve user profile data and addresses.
    
    Request Headers:
        Authorization: Bearer <token>
    
    Response:
        200 OK: {
            "info": [{"ID": int, "EMAIL": str, "FIRST_NAME": str, "LAST_NAME": str, ...}],
            "addresses": [{"ID": int, "FULL_NAME": str, "LINE1": str, ...}, ...]
        }
        401 Unauthorized: Invalid or expired token
        500 Internal Server Error: Database error
    
    Authentication:
        Required - Bearer token in Authorization header
    
    Notes:
        Returns user info and all associated addresses
        Token is validated via get_token_header dependency
    """
    logger.info("Attempting to retrieve user data")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    
    if result.get("status") == "error":
        logger.error(f"Failed to get user ID from token: {result.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = result.get("output")[0]["USER_ID"]
    logger.info(f"Retrieving data for user ID {user_id}")
    address = userdao.get_user_addresses(user_id)
    
    if address.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve addresses"
        )
    
    info = userdao.get_user_info(user_id)
    
    if info.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user info"
        )
    
    logger.info(f"Successfully retrieved data for user ID {user_id}")
    return {
        "info": info.get("output"),
        "addresses": address.get("output")
    }

@router.put("/", status_code=status.HTTP_200_OK)
def update_user_data(request: Request, payload: UpdateUserRequest, token: str = Depends(get_token_header)):
    """
    Update user profile information.
    
    Request Headers:
        Authorization: Bearer <token>
    
    Request Body:
        email (str): New email address
        password (str): New password (will be hashed)
        fname (str): New first name
        lname (str): New last name
    
    Response:
        200 OK: {"message": "User data updated successfully"}
        400 Bad Request: Invalid data
        401 Unauthorized: Invalid or expired token
    
    Authentication:
        Required - Bearer token in Authorization header
    
    Side Effects:
        Updates user record in USERS table
        Password is hashed before storage
    """
    email = payload.email
    password = payload.password
    hashed_password = hash_password(password)
    fname = payload.fname
    lname = payload.lname
    logger.info(f"Attempting to update user data for email: {email}")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)

    if result.get("status") == "error":
        logger.error(f"Failed to get user ID from token: {result.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = result.get("output")[0]["USER_ID"]
    logger.info(f"User ID {user_id} found, updating user data")

    out = userdao.update_user_data(user_id, email, hashed_password, fname, lname)
    
    if out.get("status") == "error":
        logger.error(f"Failed to update user data for user ID {user_id}: {out.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user data"
        )
    
    logger.info(f"Successfully updated user data for user ID {user_id}")
    return {"message": "User data updated successfully"}

@router.post("/address", status_code=status.HTTP_201_CREATED)
def add_address(request: Request, payload: AddressRequest, token: str = Depends(get_token_header)):
    """
    Add a new address to user's address book.
    
    Request Headers:
        Authorization: Bearer <token>
    
    Request Body:
        full_name (str): Recipient's full name
        line1 (str): Address line 1
        line2 (str): Address line 2 (optional)
        city (str): City name
        region (str): State/province
        postal_code (str): ZIP/postal code
        country_code (str): ISO country code
        phone (str): Contact phone number
    
    Response:
        201 Created: {"message": "Address added successfully"}
        400 Bad Request: Invalid address data
        401 Unauthorized: Invalid or expired token
        404 Not Found: User not found
    
    Authentication:
        Required - Bearer token in Authorization header
    
    Side Effects:
        Inserts new address into ADDRESSES table associated with user
    """
    full_name = payload.full_name
    line1 = payload.line1
    line2 = payload.line2
    city = payload.city
    region = payload.region
    postal_code = payload.postal_code
    country_code = payload.country_code
    phone = payload.phone
    logger.info(f"Attempting to add address for user")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    
    if result.get("status") == "error":
        logger.error(f"Failed to get user ID from token: {result.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if len(result.get("output")) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_id = result.get("output")[0]["USER_ID"]
    logger.info(f"Adding address for user ID {user_id}")
    out = userdao.add_address(user_id, full_name, line1, line2, city, region, postal_code, country_code, phone)
    
    if out.get("status") == "error":
        logger.error(f"Failed to add address for user ID {user_id}: {out.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add address"
        )
    
    logger.info(f"Successfully added address for user ID {user_id}")
    return {"message": "Address added successfully"}

@router.delete("/address/{index}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(request: Request, index: int, token: str = Depends(get_token_header)):
    """
    Delete an address from user's address book.
    
    Request Headers:
        Authorization: Bearer <token>
    
    Path Parameters:
        index (int): Address ID to delete
    
    Response:
        204 No Content: Address deleted successfully (no body)
        401 Unauthorized: Invalid or expired token
        404 Not Found: Address not found or doesn't belong to user
    
    Authentication:
        Required - Bearer token in Authorization header
    
    Side Effects:
        Deletes address record from ADDRESSES table
    
    Notes:
        Verifies address belongs to authenticated user before deletion
        Returns no response body (204 No Content per HTTP spec)
    """
    logger.info(f"Attempting to delete address with index {index}")
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    
    if result.get("status") == "error":
        logger.error(f"Failed to get user ID from token: {result.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = result.get("output")[0]["USER_ID"]
    logger.info(f"Deleting address {index} for user ID {user_id}")
    out = userdao.delete_address(user_id, index)
    
    if out.get("status") == "error":
        logger.error(f"Failed to delete address {index} for user ID {user_id}: {out.get('reason', 'Unknown error')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    logger.info(f"Successfully deleted address {index} for user ID {user_id}")
    # Note: 204 NO_CONTENT should not return a body
    return None
