import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.app import app_router
import os

app = FastAPI()

app.include_router(app_router)

