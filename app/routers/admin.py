from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.auth_service import get_current_user
from app.services.course_service import CourseService
from app.services.user_service import UserService
from typing import Annotated

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

async def verify_admin(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: Annotated[dict, Depends(verify_admin)]
):
    courses = await CourseService.get_all_courses()
    users = await UserService.get_all_users()
    stats = {
        "total_courses": len(courses),
        "total_users": len(users),
        "active_users": sum(1 for user in users if user.get("is_active", False))
    }
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "stats": stats, "courses": courses, "users": users}
    )

@router.get("/users", response_class=HTMLResponse)
async def user_management(
    request: Request,
    current_user: Annotated[dict, Depends(verify_admin)]
):
    users = await UserService.get_all_users()
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "users": users}
    )

@router.get("/courses", response_class=HTMLResponse)
async def course_management(
    request: Request,
    current_user: Annotated[dict, Depends(verify_admin)]
):
    courses = await CourseService.get_all_courses()
    return templates.TemplateResponse(
        "admin/courses.html",
        {"request": request, "courses": courses}
    )
