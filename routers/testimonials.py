from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database.database import get_db
from models.database_models import User, Testimonial


router = APIRouter()

class TestimonialBase(BaseModel):
    author_name: str
    content: str
    rating: int

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialResponse(TestimonialBase):
    id: int
    teacher_id: int
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/testimonials", response_model=TestimonialResponse)
async def create_testimonial(
    testimonial: TestimonialCreate,
    teacher_id: int,
    db: Session = Depends(get_db)
):
    """Create a new testimonial for a teacher"""
    # Verify teacher exists
    teacher = db.query(User).filter(User.id == teacher_id, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Create testimonial
    db_testimonial = Testimonial(
        teacher_id=teacher_id,
        author_name=testimonial.author_name,
        content=testimonial.content,
        rating=testimonial.rating
    )
    db.add(db_testimonial)
    db.commit()
    db.refresh(db_testimonial)
    return db_testimonial

@router.get("/testimonials/{teacher_id}", response_model=List[TestimonialResponse])
async def get_teacher_testimonials(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    """Get all testimonials for a specific teacher"""
    teacher = db.query(User).filter(User.id == teacher_id, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return db.query(Testimonial).filter(Testimonial.teacher_id == teacher_id).all()

@router.get("/testimonials/latest/{limit}", response_model=List[TestimonialResponse])
async def get_latest_testimonials(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get the latest testimonials across all teachers"""
    return db.query(Testimonial).order_by(Testimonial.created_at.desc()).limit(limit).all()
#
# @router.delete("/testimonials/{testimonial_id}")
# async def delete_testimonial(
#     testimonial_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Delete a testimonial (only by the teacher who received it)"""
#     testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
#     if not testimonial:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Testimonial not found"
#         )
#
#     # Verify the current user is the teacher who received the testimonial
#     if testimonial.teacher_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete this testimonial"
#         )
#
#     db.delete(testimonial)
#     db.commit()
#     return {"message": "Testimonial deleted successfully"}
