from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os
import shutil
from slugify import slugify

from database.database import get_db
from models.database_models import BlogPost, User
# from auth.auth import get_current_user

from starlette.authentication import requires

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Course categories
categories = {
    "programming": "Proqramlaşdırma",
    "data_science": "Data Elmi",
    "cybersecurity": "Kiber Təhlükəsizlik",
    "web_development": "Veb Proqramlaşdırma",
    "mobile_development": "Mobil Proqramlaşdırma",
    "cloud_computing": "Bulud Texnologiyaları",
    "devops": "DevOps",
    "artificial_intelligence": "Süni İntellekt",
    "machine_learning": "Maşın Öyrənməsi",
    "blockchain": "Blokçeyn"
}

@router.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request, db: Session = Depends(get_db)):
    """Display list of all blog posts"""
    blog_posts = db.query(BlogPost).filter(BlogPost.published == True).order_by(BlogPost.created_at.desc()).all()
    
    return templates.TemplateResponse("blog/list.html", {
        "request": request,
        "blog_posts": blog_posts,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    """Display a single blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse("blog/detail.html", {
        "request": request,
        "blog_post": blog_post,
        "author": blog_post.author,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.get("/admin/blog/new", response_class=HTMLResponse)
@requires("authenticated")
async def new_blog_post(request: Request):
    """Display form to create new blog post"""
    return templates.TemplateResponse("admin/blog/form.html", {
        "request": request,
        "is_edit": False,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.post("/admin/blog/new")
@requires("authenticated")
async def create_blog_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    summary: str = Form(...),
    published: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new blog post"""
    current_user = await get_current_user(request)
    
    # Handle image upload
    image_url = None
    if image:
        # Create uploads directory if it doesn't exist
        os.makedirs("static/uploads/blog", exist_ok=True)
        
        # Save the file
        file_location = f"static/uploads/blog/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        image_url = f"/static/uploads/blog/{image.filename}"
    
    # Create slug from title
    slug = slugify(title)
    
    # Create blog post
    blog_post = BlogPost(
        title=title,
        content=content,
        summary=summary,
        slug=slug,
        published=published,
        featured_image=image_url,
        author_id=current_user.id
    )
    
    db.add(blog_post)
    db.commit()
    db.refresh(blog_post)
    
    return RedirectResponse(url=f"/blog/{blog_post.slug}", status_code=303)

@router.get("/admin/blog/{blog_id}/edit", response_class=HTMLResponse)
@requires("authenticated")
async def edit_blog_post(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Display form to edit blog post"""
    # Get current user from session
    current_user = await get_current_user(request)
    
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    if blog_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own blog posts")
    
    return templates.TemplateResponse("admin/blog/form.html", {
        "request": request,
        "blog_post": blog_post,
        "is_edit": True,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.post("/admin/blog/{blog_id}/edit")
@requires("authenticated")
async def update_blog_post(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    summary: str = Form(...),
    published: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update an existing blog post"""
    # Get current user from session
    current_user = await get_current_user(request)
    
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    if blog_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own blog posts")
    
    # Handle image upload
    if image:
        # Remove old image if it exists
        if blog_post.featured_image:
            old_image_path = f"static{blog_post.featured_image}"
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Save new image
        os.makedirs("static/uploads/blog", exist_ok=True)
        file_location = f"static/uploads/blog/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        blog_post.featured_image = f"/static/uploads/blog/{image.filename}"
    
    # Update blog post
    blog_post.title = title
    blog_post.content = content
    blog_post.summary = summary
    blog_post.published = published
    
    db.commit()
    db.refresh(blog_post)
    
    return RedirectResponse(url=f"/blog/{blog_post.slug}", status_code=303)

@router.delete("/admin/blog/{blog_id}")
@requires("authenticated")
async def delete_blog_post(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Delete a blog post"""
    # Get current user from session
    current_user = await get_current_user(request)
    
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    if blog_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own blog posts")
    
    # Remove image if it exists
    if blog_post.featured_image:
        image_path = f"static{blog_post.featured_image}"
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(blog_post)
    db.commit()
    
    return {"success": True}

@router.post("/admin/blog/upload-image")
@requires("authenticated")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image for TinyMCE"""
    # Get current user from session
    current_user = await get_current_user(request)
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("static/uploads/blog/content", exist_ok=True)
        
        # Save the uploaded file
        file_location = f"static/uploads/blog/content/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        # Return the URL in the format expected by TinyMCE
        return {"location": f"/static/uploads/blog/content/{image.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
