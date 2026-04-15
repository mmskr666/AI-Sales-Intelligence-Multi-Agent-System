from fastapi import FastAPI
from api.app import app_router


app = FastAPI()

app.include_router(app_router)

