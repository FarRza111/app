from fastapi import Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path

# Initialize templates
templates = Jinja2Templates(directory=str(Path("templates")))

async def get_current_user(request: Request):
    """
    Simple user dependency that always returns a guest user.
    In a real application, this would check session/token/etc.
    """
    return {
        "id": 1,  # Guest user ID
        "username": "guest",
        "is_authenticated": True
    }

def admin_required(request: Request):
    """
    Middleware to check if user is logged in as admin.
    Redirects to login page if not authenticated.
    """
    admin_cookie = request.cookies.get("admin_logged_in")
    if not admin_cookie or admin_cookie != "true":
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return True
