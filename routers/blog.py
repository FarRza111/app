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
        "categories": categories,
        "current_time": datetime.now()
    })

@router.get("/create-blog", response_class=HTMLResponse)
async def new_blog_post(request: Request):
    """Display form to create new blog post"""
    return templates.TemplateResponse("blog/create.html", {
        "request": request,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.post("/create-blog")
async def create_blog_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new blog post"""
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
        featured_image=image_url,
        published=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return RedirectResponse(url=f"/blog/{new_post.slug}", status_code=303)

@router.get("/admin/blog/{blog_id}/edit", response_class=HTMLResponse)
async def edit_blog_post(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Display form to edit blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse("admin/blog/form.html", {
        "request": request,
        "blog_post": blog_post,
        "is_edit": True,
        "categories": categories,
        "current_time": datetime.now()
    })

@router.post("/admin/blog/{blog_id}/edit")
async def update_blog_post(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update an existing blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Handle image upload
    if image and image.filename:
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
    
    db.commit()
    db.refresh(blog_post)
    
    return RedirectResponse(url=f"/blog/{blog_post.slug}", status_code=303)

@router.delete("/admin/blog/{blog_id}")
async def delete_blog_post(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Delete a blog post"""
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Remove image if it exists
    if blog_post.featured_image:
        image_path = f"static{blog_post.featured_image}"
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(blog_post)
    db.commit()
    
    return {"success": True}

@router.post("/admin/blog/upload-image")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image for TinyMCE"""
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
