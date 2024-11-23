from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
import os

templates = Jinja2Templates(directory="templates")

def create_app():
    app = FastAPI(
        title="Tech Learning Hub",
        description="A platform for tech courses"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SECRET_KEY", "your-secret-key")
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app
