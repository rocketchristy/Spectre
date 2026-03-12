from fastapi import FastAPI
from Backend.RestAPI.Routes import login, inventory
from Backend.DatabaseAccess.connection_pool import IBMDBConnectionPool
import configparser
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
app.include_router(login.router)
app.include_router(inventory.router)