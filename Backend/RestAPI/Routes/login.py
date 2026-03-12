from fastapi import APIRouter, Body, Request, Depends
from Backend.Utilities.logger import logger
from Backend.DatabaseAccess.user_dao import UserDAO
from Backend.Utilities.utilities import hash_password, get_token_header

from pydantic import BaseModel
router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: Request, payload:LoginRequest):
    email=payload.email
    password=payload.password
    password_hash= hash_password(password)
    logger.info("Attempted login by "+ email)
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result=userdao.get_user(email)
    # Check if valid login
    if result.get("status") == "error":
        logger.info(f"Failed to login : {result.get('reason')}")
        return {"status": "error", "reason": result.get("reason")}
    if result.get("output")==[]:
        logger.info(f"Invalid logon attempt from {email}")
        return {"Invalid email"}
    elif result.get("output")[0]["HASHED_PASSWORD"] == password_hash:
        logger.info(f"Valid login from {email}")
        userdao.add_token(result.get("output")[0]["ID"])
        result_token=userdao.get_token(email)
        
        return {"Token": result_token.get("output")[-1]['ID'], "First-Name": result.get("output")[-1]['FIRST_NAME']}
    elif result.get("output")[0]["HASHED_PASSWORD"] != password_hash:
        logger.info(f"Invalid Password attempt from {email}")
        return {"Invalid Password"}
    else:
        logger.info(f'Error encountered when logging in from {email}')
        return {"Error Encountered"}
    
class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

@router.post("/register")
def register(request: Request, payload: RegisterRequest):
    # retrieve information 
    email=payload.email
    password=payload.password
    password_hash=hash_password(password)
    first_name=payload.first_name
    last_name=payload.last_name
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result=userdao.add_user(email,password_hash,first_name,last_name)
    if result.get("status") == "error":
        logger.info(f"Failed to register email: {result.get('reason')}")
        return {"status": "error", "reason": result.get("reason")}
    logger.info(f"Register user {email} successfully")
    return {"status": "success"}

@router.get("/user")
def get_user_data(request:Request, token: str = Depends(get_token_header)):
    pool=request.app.state.db_pool
    userdao=UserDAO(pool)
    result = userdao.get_user_id(token)
    address=userdao.get_user_addresses(result.get("output")[0]["USER_ID"])
    info=userdao.get_user_info(result.get("output")[0]["USER_ID"])
    return {"info": info.get("output"), "address": address.get("output")}

class UpdateUserRequest(BaseModel):
    email: str
    password: str
    fname: str
    lname: str

@router.put("/user")
def update_user_data(request: Request, payload: UpdateUserRequest, token: str = Depends(get_token_header)):
    email = payload.email
    password = payload.password
    hashed_password = hash_password(password)
    fname = payload.fname
    lname = payload.lname
    pool=request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    userdao.update_user_data(result.get("output")[0]["USER_ID"],email, hashed_password, fname, lname)
    return {"status": "success"}

class AddressRequest(BaseModel):
    full_name: str
    line1: str
    line2: str
    city: str
    region: str
    postal_code: str
    country_code: str
    phone: str

@router.post("/user/address")
def add_address(request: Request, payload: AddressRequest, token: str = Depends(get_token_header)):
    full_name = payload.full_name
    line1 = payload.line1
    line2 = payload.line2
    city = payload.city
    region = payload.region
    postal_code = payload.postal_code
    country_code = payload.country_code
    phone = payload.phone
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    out=userdao.add_address(result.get("output")[0]["USER_ID"], full_name, line1, line2, city, region, postal_code, country_code, phone)
    return out

@router.delete("/user/address/{index}")
def delete_address(request: Request, index: int, token: str = Depends(get_token_header)):
    pool = request.app.state.db_pool
    userdao = UserDAO(pool)
    result = userdao.get_user_id(token)
    out = userdao.delete_address(result.get("output")[0]["USER_ID"], index)
    return out