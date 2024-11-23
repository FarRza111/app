from pydantic import BaseModel, EmailStr

class EmailSchema(BaseModel):
    email: EmailStr
    name: str
    message: str

class PurchaseSchema(BaseModel):
    email: EmailStr
    name: str
    course_id: str
