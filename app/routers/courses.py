from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.models.course import CourseBase, CourseCreate
from app.services.course_service import CourseService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def course_list(request: Request):
    courses = CourseService.get_all_courses()
    return templates.TemplateResponse(
        "course_list.html",
        {"request": request, "courses": courses}
    )

@router.get("/{course_id}", response_class=HTMLResponse)
async def course_detail(request: Request, course_id: str):
    course = CourseService.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse(
        "course_detail.html",
        {"request": request, "course": course}
    )

@router.post("/create")
async def create_course(course: CourseCreate, current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return CourseService.create_course(course)

@router.put("/{course_id}")
async def update_course(
    course_id: str,
    course: CourseBase,
    current_user = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated_course = CourseService.update_course(course_id, course)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course

@router.delete("/{course_id}")
async def delete_course(course_id: str, current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not CourseService.delete_course(course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}
