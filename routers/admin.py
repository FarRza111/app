from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os
import shutil
from slugify import slugify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get admin credentials from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

from database.database import get_db
from models.database_models import BlogPost, User
from dependencies import admin_required

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    """Root admin route - redirects to dashboard if logged in, login page if not"""
    admin_cookie = request.cookies.get("admin_logged_in")
    if admin_cookie and admin_cookie == "true":
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return RedirectResponse(url="/admin/login", status_code=303)

@router.get("/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "current_time": datetime.now()
    })

@router.post("/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle admin login"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_logged_in", value="true", httponly=True)
        return response
    return RedirectResponse(url="/admin/login?error=invalid_credentials", status_code=303)

@router.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard"""
    blog_posts = db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "blog_posts": blog_posts,
        "current_time": datetime.now()
    })

@router.get("/blog/new", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def new_blog_post(request: Request):
    """Display form to create new blog post"""
    return templates.TemplateResponse("admin/blog/create.html", {
        "request": request,
        "current_time": datetime.now()
    })

@router.post("/blog/new", dependencies=[Depends(admin_required)])
async def create_blog_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new blog post"""
    try:
        # Handle image upload
        image_url = None
        if image and image.filename:
            # Create uploads directory if it doesn't exist
            os.makedirs("static/uploads/blog", exist_ok=True)
            
            # Save the file
            file_location = f"static/uploads/blog/{image.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(image.file, file_object)
            
            image_url = f"/static/uploads/blog/{image.filename}"
        
        # Create slug from title
        slug = slugify(title)
        
        # Create new blog post
        new_post = BlogPost(
            title=title,
            content=content,
            slug=slug,
            image_url=image_url,
            published=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blog/{blog_id}/edit", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def edit_blog_post(request: Request, blog_id: int, db: Session = Depends(get_db)):
    """Display form to edit blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse("admin/blog/edit.html", {
        "request": request,
        "post": blog_post,
        "current_time": datetime.now()
    })

@router.post("/blog/{blog_id}/edit", dependencies=[Depends(admin_required)])
async def update_blog_post(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update a blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Handle image upload
    if image and image.filename:
        # Remove old image if it exists
        if blog_post.image_url:
            old_image_path = f"static{blog_post.image_url}"
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Create uploads directory if it doesn't exist
        os.makedirs("static/uploads/blog", exist_ok=True)
        
        # Save the new file
        file_location = f"static/uploads/blog/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        blog_post.image_url = f"/static/uploads/blog/{image.filename}"
    
    # Update blog post
    blog_post.title = title
    blog_post.content = content
    blog_post.slug = slugify(title)
    blog_post.updated_at = datetime.now()
    
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.post("/blog/{blog_id}/delete", dependencies=[Depends(admin_required)])
async def delete_blog_post(request: Request, blog_id: int, db: Session = Depends(get_db)):
    """Delete a blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Remove image if it exists
    if blog_post.image_url:
        image_path = f"static{blog_post.image_url}"
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(blog_post)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.get("/logout")
async def admin_logout(request: Request):
    """Handle admin logout"""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="admin_logged_in")
    return response
