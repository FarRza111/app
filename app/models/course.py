from typing import List, Optional
from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str
    price: float
    duration: str
    modules: List[dict]
    outcomes: List[str]

class CourseCreate(CourseBase):
    id: Optional[str] = None

class CourseResponse(CourseBase):
    id: str
