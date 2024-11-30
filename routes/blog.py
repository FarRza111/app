from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blog import Blog
from app.dependencies import templates
import shutil
import os
from pathlib import Path
import re

router = APIRouter()

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return its path"""
    upload_dir = Path("static/uploads/blog")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / upload_file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return f"/static/uploads/blog/{upload_file.filename}"

@router.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request, db: Session = Depends(get_db)):
    blog_posts = db.query(Blog).order_by(Blog.created_at.desc()).all()
    return templates.TemplateResponse("blog/list.html", {
        "request": request,
        "blog_posts": blog_posts,
        "current_time": datetime.now()
    })

@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    blog_post = db.query(Blog).filter(Blog.slug == slug).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse("blog/detail.html", {
        "request": request,
        "blog_post": blog_post,
        "current_time": datetime.now()
    })

@router.get("/create-blog", response_class=HTMLResponse)
async def new_blog_post(request: Request):
    return templates.TemplateResponse("blog/create.html", {
        "request": request
    })

@router.post("/create-blog")
async def create_blog_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Create slug from title
    slug = slugify(title)
    
    # Check if slug exists
    existing_post = db.query(Blog).filter(Blog.slug == slug).first()
    if existing_post:
        # Append timestamp to make slug unique
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    # Handle image upload
    thumbnail_url = None
    if image and image.filename:
        thumbnail_url = save_upload_file(image)
    
    # Create new blog post
    new_post = Blog(
        title=title,
        content=content,
        slug=slug,
        thumbnail_url=thumbnail_url,
        excerpt=content[:200] + "..." if len(content) > 200 else content
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return RedirectResponse(url=f"/blog/{new_post.slug}", status_code=303)

@router.get("/blog/{blog_id}/edit", response_class=HTMLResponse)
async def edit_blog_post(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    blog_post = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse("blog/edit.html", {
        "request": request,
        "blog_post": blog_post
    })

@router.post("/blog/{blog_id}/edit")
async def update_blog_post(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    blog_post = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Update blog post
    blog_post.title = title
    blog_post.content = content
    blog_post.updated_at = datetime.utcnow()
    blog_post.excerpt = content[:200] + "..." if len(content) > 200 else content
    
    db.commit()
    db.refresh(blog_post)
    
    return RedirectResponse(url=f"/blog/{blog_post.slug}", status_code=303)

@router.delete("/blog/{blog_id}")
async def delete_blog_post(
    blog_id: int,
    db: Session = Depends(get_db)
):
    blog_post = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    db.delete(blog_post)
    db.commit()
    
    return {"message": "Blog post deleted successfully"}

# Comment routes
@router.post("/blog/{blog_id}/comment")
async def create_comment(
    blog_id: int,
    content: str = Form(...),
    parent_id: int = Form(None),
    db: Session = Depends(get_db)
):
    blog_post = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    new_comment = Comment(
        content=content,
        blog_id=blog_id,
        parent_id=parent_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return RedirectResponse(url=f"/blog/{blog_post.slug}#comment-{new_comment.id}", status_code=303)

@router.delete("/blog/comment/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}
