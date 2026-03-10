from fastapi import FastAPI, Body
from Backend.RestAPI.Routes import login, inventory

app = FastAPI()
app.include_router(login.router)
app.include_router(inventory.router)

