"""
================================================================================
File: server.py
Description: FastAPI application server and main entry point
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module configures and runs the FastAPI web server for the Spectre
e-commerce platform. It handles:
- Database connection pool initialization
- CORS middleware configuration
- Route registration for all API endpoints
- Global exception handling
- Application lifecycle management
================================================================================
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from Backend.RestAPI.Routes import inventory, user, products, cart, orders
from Backend.DatabaseAccess.connection_pool import IBMDBConnectionPool
import configparser
from Backend.Utilities.logger import logger
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle (startup and shutdown).
    
    Inputs:
        app (FastAPI): FastAPI application instance
    
    Outputs:
        None (async context manager)
    
    Side Effects:
        - Startup: Creates database connection pool
        - Shutdown: Closes all database connections
    
    Notes:
        This replaces deprecated @app.on_event decorators
    """
    # Startup logic
    config = configparser.ConfigParser()
    config.read('DatabaseAccess/config.ini')
    username = config['database']['username']
    password = config['database']['password']
    database = config['database']['database']
    hostname = config['database']['hostname']
    port = config['database']['port']
    
    # Build IBM Db2 connection string
    conn_str = (
        f"DATABASE={database};"
        f"HOSTNAME={hostname};"
        f"PORT={port};"
        "PROTOCOL=TCPIP;"
        f"UID={username};"
        f"PWD={password};"
    )
    
    # Initialize connection pool and attach to application state
    app.state.db_pool = IBMDBConnectionPool(conn_str, pool_size=5)
    logger.info("Database connection pool initialized")
    
    yield
    
    # Shutdown logic
    app.state.db_pool.close_all()
    logger.info("Database connections closed")


# Initialize FastAPI application with lifecycle management
app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions raised by route handlers.
    
    Inputs:
        request (Request): Incoming HTTP request
        exc (HTTPException): HTTP exception that was raised
    
    Outputs:
        JSONResponse: Standardized error response
    
    Notes:
        Logs error and returns consistent JSON error format
    """
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "reason": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions not caught by route handlers.
    
    Inputs:
        request (Request): Incoming HTTP request
        exc (Exception): Unhandled exception that was raised
    
    Outputs:
        JSONResponse: Generic 500 error response
    
    Notes:
        Logs full exception traceback and returns safe generic message
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "reason": "Internal server error"}
    )


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# API base path
path = "/spectre/api"

# Register all route modules with their prefixes
app.include_router(user.router, prefix=path + "/user")
app.include_router(inventory.router, prefix=path + "/inventory")
app.include_router(products.router, prefix=path + "/products")
app.include_router(cart.router, prefix=path + "/cart")
app.include_router(orders.router, prefix=path + "/orders")


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@app.get("/hello_world")
def hello_world():
    """
    Simple test endpoint to verify server is running.
    
    Inputs:
        None
    
    Outputs:
        str: Greeting message
    """
    return "Hi All"


@app.get("/hola_mundo")
def hola_mundo():
    """
    Simple test endpoint (Spanish greeting).
    
    Inputs:
        None
    
    Outputs:
        str: Spanish greeting message
    """
    return "Hola a todos"
