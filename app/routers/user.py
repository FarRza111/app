from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.auth_service import get_current_user
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.models.email import PurchaseSchema
from app.models.user import UserResponse, UserInDB

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    current_user: UserInDB = Depends(get_current_user)
):
    user_courses = await UserService.get_user_courses(current_user.username)
    user_stats = await UserService.calculate_user_stats(current_user.username)
    certificates = await UserService.get_user_certificates(current_user.username)
    streak_data = await UserService.get_streak_data(current_user.username)
    
    return templates.TemplateResponse(
        "user/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "courses": user_courses,
            "stats": user_stats,
            "certificates": certificates,
            "streak_data": streak_data
        }
    )

@router.post("/purchase")
async def purchase_course(
    purchase_data: PurchaseSchema,
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        result = await UserService.process_course_purchase(
            current_user.username,
            purchase_data.course_id
        )
        return JSONResponse(content={"message": "Purchase successful"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/progress/{course_id}")
async def update_progress(
    course_id: str,
    module_id: int,
    completed: bool = True,
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        await UserService.update_course_progress(
            current_user.username,
            course_id,
            module_id,
            completed
        )
        return JSONResponse(content={"message": "Progress updated successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/certificates/{certificate_id}")
async def download_certificate(
    certificate_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        certificate = await UserService.get_certificate(current_user.username, certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        return certificate
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
