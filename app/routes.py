from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from database import database

router = APIRouter()


@router.post("/blog_posts/", response_model=schemas.BlogPost)
def create_blog_post(blog_post: schemas.BlogPostCreate, db: Session = Depends(database.SessionLocal)):
    return crud.create_blog_post(db=db, blog_post=blog_post)

@router.get("/blog_posts/{blog_post_id}", response_model=schemas.BlogPost)
def read_blog_post(blog_post_id: int, db: Session = Depends(database.SessionLocal)):
    db_blog_post = crud.get_blog_post(db, blog_post_id=blog_post_id)
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_blog_post

@router.get("/blog_posts/", response_model=list[schemas.BlogPost])
def read_blog_posts(skip: int = 0, limit: int = 10, db: Session = Depends(database.SessionLocal)):
    return crud.get_blog_posts(db, skip=skip, limit=limit)


