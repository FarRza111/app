from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class TeacherBase(BaseModel):
    full_name: str
    title: str
    bio: str
    linkedin_url: HttpUrl
    profile_image_url: Optional[HttpUrl] = None
    specializations: List[str]
    years_of_experience: int
    education: List[str]
    achievements: Optional[List[str]] = None
    teaching_philosophy: Optional[str] = None

    class Config:
        orm_mode = True

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    title: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    profile_image_url: Optional[HttpUrl] = None
    specializations: Optional[List[str]] = None
    years_of_experience: Optional[int] = None
    education: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    teaching_philosophy: Optional[str] = None

class TeacherInDB(TeacherBase):
    id: int

    class Config:
        orm_mode = True
