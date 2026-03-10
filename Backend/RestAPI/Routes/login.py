from fastapi import APIRouter, Body
from Backend.Utilities.logger import logger

router = APIRouter()

@router.post("/login")
def login(payload: dict = Body(...)):
    username=payload.get("username")
    password=payload.get("password")
    logger.info("Attempted login by "+ username)
    # convert password to hash value
	# call dao to get password where username =
    #return if no user exists
    # return incorrect password
    # return {"token": username-token-2026}
    return {"token:": username}

'''
@app.post("/register")
def login(payload: dict = Body(...)):
    # retrieve information 
'''