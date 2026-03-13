from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from Backend.RestAPI.Routes import inventory, user, products, cart
from Backend.DatabaseAccess.connection_pool import IBMDBConnectionPool
import configparser
from Backend.Utilities.logger import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    config = configparser.ConfigParser()
    config.read('Backend/DatabaseAccess/config.ini')
    username = config['database']['username']
    password = config['database']['password']
    conn_str = (
        "DATABASE=HL02HL2D;"
        "HOSTNAME=192.168.54.250;"
        "PORT=3600;"
        "PROTOCOL=TCPIP;"
        f"UID={username};"
        f"PWD={password};"
    )
    app.state.db_pool = IBMDBConnectionPool(conn_str, pool_size=5)
    yield
    # Shutdown logic
    app.state.db_pool.close_all()

app = FastAPI(lifespan=lifespan)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "reason": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "reason": "Internal server error"}
    )

path = "/spectre/api"
app.include_router(user.router, prefix = path + "/user")
app.include_router(inventory.router, prefix = path + "/inventory")
app.include_router(products.router, prefix = path + "/products")
#app.include_router(cart.router, prefix = path + "/cart")