from fastapi import FastAPI, Request, HTTPException, Depends, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
import json
from pathlib import Path
import shutil
import os
import logging
import traceback
from datetime import datetime, timedelta

from database.database import engine, Base, get_db

from routers import chatbot, testimonials, blog
from services import CourseService
from models.database_models import Course, BlogPost, User, Testimonial
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Tech Learning Hub",
    description="A platform for tech courses",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Initialize database
Base.metadata.create_all(bind=engine)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Utility functions
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def to_snake(string: str) -> str:
    """Convert camelCase to snake_case."""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', string).lower()

def convert_dict_case(d: dict, converter: callable) -> dict:
    """Convert all dictionary keys using the provided case converter."""
    new_dict = {}
    for k, v in d.items():
        new_key = converter(k)
        if isinstance(v, dict):
            new_dict[new_key] = convert_dict_case(v, converter)
        elif isinstance(v, list):
            new_dict[new_key] = [
                convert_dict_case(x, converter) if isinstance(x, dict) else x 
                for x in v
            ]
        else:
            new_dict[new_key] = v
    return new_dict

class CamelModel(BaseModel):
    """Base model that converts snake_case to camelCase in JSON."""
    
    def dict(self, *args, **kwargs):
        """Override dict() to convert keys to camelCase."""
        d = super().dict(*args, **kwargs)
        return convert_dict_case(d, to_camel)

    @classmethod
    def parse_obj(cls, obj):
        """Override parse_obj() to convert keys from camelCase to snake_case."""
        if isinstance(obj, dict):
            converted = convert_dict_case(obj, to_snake)
            return super().parse_obj(converted)
        return super().parse_obj(obj)

# Email Models
class EmailSchema(BaseModel):
    email: EmailStr
    name: str
    message: str

    class Config:
        alias_generator = to_camel

class PurchaseSchema(BaseModel):
    email: EmailStr
    name: str
    course_id: str

    class Config:
        alias_generator = to_camel

class MessageSchema(BaseModel):
    subject: str
    recipients: List[str]
    body: str
    subtype: Optional[str] = "html"

# Course Models
class CourseBase(BaseModel):
    title: str
    description: str
    price: float
    duration: str
    modules: list
    outcomes: list
    difficulty: str
    alias_generator = to_camel

class CourseCreate(CourseBase):
    id: Optional[str] = None
    alias_generator = to_camel

class MeetingRequest(BaseModel):
    name: str
    email: str
    phone: str
    message: str

# Include routers
app.include_router(chatbot.router, prefix="/api", tags=["chat"])
app.include_router(testimonials.router, prefix="/api", tags=["testimonials"])
app.include_router(blog.router, tags=["blog"])

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

# Convert courses list to dictionary
courses_list = [
    {
        "id": "python-programming",
        "category": "programming",
        "name": "Python Proqramlaşdırma",
        "subtitle": "Sıfırdan Professional Python Developer",
        "description": "Python proqramlaşdırma dilini əsaslarından başlayaraq professional səviyyəyə qədər öyrənin. Web development, data science və süni intellekt sahələrində istifadə üçün lazım olan bütün bacarıqları əldə edin.",
        "image": "/static/images/courses/python-course.jpg",
        "instructor": {
            "name": "Rustam Kisi",
            "title": "Senior Software Engineer",
            "image": "/static/images/instructors/ali-mammadov.jpg",
            "bio": "10+ illik proqramlaşdırma təcrübəsi"
        },
        "stats": {
            "students": 3278,
            "reviews": 458,
            "rating": 4.9
        },
        "features": {
            "level": "Ileri",
            "duration": "16 həftə",
            "lectures": 124,
            "hours": 42,
            "projects": 8
        },
        "price": {
            "original": 599,
            "discounted": 299
        },
        "curriculum": [
            {
                "title": "Python Təməlləri",
                "lessons": [
                    "Python-a Giriş və Quraşdırma",
                    "Dəyişənlər və Data Tipləri",
                    "Nəzarət Strukturları",
                    "Funksiyalar və Modullar"
                ]
            },
            {
                "title": "Object Oriented Programming",
                "lessons": [
                    "OOP Konsepsiyaları",
                    "Klaslar və Obyektlər",
                    "İnheritance və Polymorphism",
                    "Encapsulation və Abstraction"
                ]
            }
        ]
    },
    {
        "id": "data-analytics",
        "category": "data_science",
        "name": "Data Analitikasi",
        "subtitle": "Data ilə İşləmə və Vizuallaşdırma",
        "description": "Məlumatların toplanması, təmizlənməsi, analizi və vizuallaşdırılması üçün lazım olan bütün metodları öyrənin. SQL və Power BI ilə işləməyi mənimsəyin.",
        "image": "/static/images/courses/powerbi-course.jpg",
        "instructor": {
            "name": "Fariz Rzayev",
            "title": "Senior Data Scientist",
            "image": "/static/images/instructors/leyla-hasanova.jpg",
            "bio": "8+ illik data analitika təcrübəsi"
        },
        "stats": {
            "students": 2145,
            "reviews": 312,
            "rating": 4.8
        },
        "features": {
            "level": "Orta",
            "duration": "14 həftə",
            "lectures": 98,
            "hours": 38,
            "projects": 6
        },
        "price": {
            "original": 699,
            "discounted": 349
        },
        "curriculum": [
            {
                "title": "Data Analitika Təməlləri",
                "lessons": [
                    "Data Analitikaya Giriş",
                    "SQL ilə Data Manipulyasiyası",
                    "Python ilə Data Analizi",
                    "Statistik Analiz Metodları"
                ]
            },
            {
                "title": "Vizuallaşdırma",
                "lessons": [
                    "Power BI Əsasları",
                    "Tableau ilə Dashboard Yaratma",
                    "İnteraktiv Vizuallar",
                    "Data Storytelling"
                ]
            }
        ]
    }
]

# Convert list to dictionary with course IDs as keys
courses = {course["id"]: course for course in courses_list}

# Add request processing middleware after session middleware
@app.middleware("http")
async def process_request(request: Request, call_next):
    """Process each request to add common context and handle errors."""
    try:
        response = await call_next(request)
        if isinstance(response, HTMLResponse):
            response.context.update({
                "categories": categories,
                "current_time": datetime.now()
            })
        return response
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        logging.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

# Sample testimonials data
testimonials = [
    {
        "id": 1,
        "name": "Əli Məmmədov",
        "role": "Data Scientist",
        "company": "Tech Corp",
        "image": "https://randomuser.me/api/portraits/men/1.jpg",
        "content": "Bu platformada Data Analytics kursunu bitirdikdən sonra karyeramda böyük irəliləyiş əldə etdim. Təlimçilər çox peşəkardır!",
        "rating": 5
    },
    {
        "id": 2,
        "name": "Ayşən Hüseynova",
        "role": "Full-stack Developer",
        "company": "StartUp Inc",
        "image": "https://randomuser.me/api/portraits/women/1.jpg",
        "content": "Web Development kursu mənim üçün çox faydalı oldu. Real layihələr üzərində işləmək təcrübəmi artırdı.",
        "rating": 5
    },
    {
        "id": 3,
        "name": "Murad Əliyev",
        "role": "ML Engineer",
        "company": "AI Solutions",
        "image": "https://randomuser.me/api/portraits/men/2.jpg",
        "content": "Machine Learning kursunun keyfiyyəti məni heyran etdi. İndi öz startupımı qururam!",
        "rating": 5
    }
]

# Sample blog posts
blog_posts = [
    {
        "id": 1,
        "title": "Data Elminin Gələcəyi",
        "excerpt": "2024-cü ildə Data Science sahəsində gözlənilən yeni trendlər və texnologiyalar haqqında məlumat...",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3",
        "author": "Dr. Cavid Əhmədov",
        "date": "2024-01-15",
        "category": "Data Science"
    },
    {
        "id": 2,
        "title": "AI-nin İş Dünyasına Təsiri",
        "excerpt": "Süni intellektin müxtəlif sektorlarda tətbiqi və gətirdiyi yeniliklər haqqında ətraflı analiz...",
        "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?ixlib=rb-4.0.3",
        "author": "Leyla Məmmədova",
        "date": "2024-01-10",
        "category": "Artificial Intelligence"
    },
    {
        "id": 3,
        "title": "Modern Web Development",
        "excerpt": "Müasir web development texnologiyaları və framework-lər haqqında praktiki məsləhətlər...",
        "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3",
        "author": "Tural Həsənov",
        "date": "2024-01-05",
        "category": "Web Development"
    }
]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the home page."""
    try:
        # Get featured courses (latest 3 courses)
        featured_courses = courses_list[:3]  # Get first 3 courses
        
        # Get recent blog posts
        recent_blog_posts = []  # We can populate this later if needed
        
        # Organize courses by category
        categorized_courses = {}
        for course in courses_list:
            category = course["category"]
            if category not in categorized_courses:
                categorized_courses[category] = []
            categorized_courses[category].append(course)
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "featured_courses": featured_courses,
                "recent_blog_posts": recent_blog_posts,
                "categories": categories,
                "categorized_courses": categorized_courses,
                "current_time": datetime.now()
            }
        )
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def course_detail(request: Request, course_id: str):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get related courses from the same category
    related_courses = [
        c for c in courses.values() 
        if c["category"] == course["category"] and c["id"] != course_id
    ][:3]
    
    return templates.TemplateResponse(
        "course_detail.html",
        {
            "request": request,
            "course": course,
            "related_courses": related_courses,
            "current_time": datetime.now()
        }
    )

@app.get("/category/{category_id}", response_class=HTMLResponse)
async def category_courses(request: Request, category_id: str):
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category_courses = [c for c in courses.values() if c["category"] == category_id]
    
    return templates.TemplateResponse(
        "category.html",
        {
            "request": request,
            "category_name": categories[category_id],
            "courses": category_courses,
            "current_time": datetime.now()
        }
    )

@app.get("/courses", response_class=HTMLResponse)
async def course_list(request: Request):
    try:
        courses = await CourseService.get_all_courses()
        return templates.TemplateResponse("courses.html", {
            "request": request,
            "courses": courses,
            "enumerate": enumerate,  # Pass enumerate function to template
            "current_time": datetime.now()
        })
    except Exception as e:
        logger.error(f"Error in course_list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def course_detail(request: Request, course_id: str):
    try:
        course = await CourseService.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Get user progress if available
        user_id = request.session.get("user_id")
        progress = None
        progress_percentage = 0

        if user_id:
            progress = user_progress.get(f"{user_id}_{course_id}", set())
            if progress and course["modules"]:
                progress_percentage = (len(progress) / len(course["modules"])) * 100

        return templates.TemplateResponse("course_detail.html", {
            "request": request,
            "course": course,
            "user_progress": progress,
            "progress_percentage": progress_percentage,
            "enumerate": enumerate,  # Pass enumerate function to template
            "current_time": datetime.now()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in course_detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/admin/api/courses")
async def create_course(course: CourseCreate, request: Request):
    try:
        course_id = await CourseService.create_course(course)
        return {"id": course_id}
    except Exception as e:
        logger.error(f"Error in create_course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create course")

@app.put("/admin/api/courses/{course_id}")
async def update_course(course_id: str, course: CourseBase, request: Request):
    try:
        success = await CourseService.update_course(course_id, course)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update course")

@app.delete("/admin/api/courses/{course_id}")
async def delete_course(course_id: str, request: Request):
    try:
        success = await CourseService.delete_course(course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete course")

@app.on_event("startup")
async def startup_event():
    # Initialize Redis connection for CourseService
    await CourseService.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up Redis connection
    await CourseService.cleanup()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "courses": courses, "current_time": datetime.now()}
    )

@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def course_detail(request: Request, course_id: str):
    course = courses.get(course_id)
    if course is None:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )
    return templates.TemplateResponse(
        "course_detail.html",
        {"request": request, "course": course, "current_time": datetime.now()}
    )

@app.get("/courses", response_class=HTMLResponse)
async def course_list(request: Request):
    try:
        courses = await CourseService.get_all_courses()
        return templates.TemplateResponse("courses.html", {
            "request": request,
            "courses": courses,
            "enumerate": enumerate,  # Pass enumerate function to template
            "current_time": datetime.now()
        })
    except Exception as e:
        logger.error(f"Error in course_list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def course_detail(request: Request, course_id: str):
    try:
        course = await CourseService.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Get user progress if available
        user_id = request.session.get("user_id")
        progress = None
        progress_percentage = 0

        if user_id:
            progress = user_progress.get(f"{user_id}_{course_id}", set())
            if progress and course["modules"]:
                progress_percentage = (len(progress) / len(course["modules"])) * 100

        return templates.TemplateResponse("course_detail.html", {
            "request": request,
            "course": course,
            "user_progress": progress,
            "progress_percentage": progress_percentage,
            "enumerate": enumerate,  # Pass enumerate function to template
            "current_time": datetime.now()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in course_detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/admin/courses")
async def create_course(request: Request):
    try:
        form = await request.form()
        course_id = slugify(form.get("name"))
        
        # Create the course data structure
        course_data = {
            "id": course_id,
            "name": form.get("name"),
            "category": form.get("category"),
            "subtitle": form.get("subtitle"),
            "description": form.get("description"),
            "image": form.get("image"),
            "instructor": {
                "name": form.get("instructor_name"),
                "title": form.get("instructor_title"),
                "image": form.get("instructor_image"),
                "bio": form.get("instructor_bio")
            },
            "stats": {
                "students": 0,
                "reviews": 0,
                "rating": 0
            },
            "features": {
                "level": form.get("level"),
                "duration": form.get("duration"),
                "lectures": int(form.get("lectures")),
                "hours": int(form.get("hours")),
                "projects": int(form.get("projects"))
            },
            "price": {
                "original": float(form.get("original_price")),
                "discounted": float(form.get("discounted_price"))
            }
        }

        # Parse curriculum JSON
        try:
            curriculum = json.loads(form.get("curriculum"))
            course_data["curriculum"] = curriculum
        except json.JSONDecodeError:
            course_data["curriculum"] = []

        # Add the course to our courses dictionary
        courses[course_id] = course_data
        
        return JSONResponse({
            "success": True,
            "redirect": "/admin/dashboard"
        })
    except Exception as e:
        logging.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/admin/courses/{course_id}")
async def update_course(request: Request, course_id: str):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    try:
        form = await request.form()
        course_data = {
            "id": course_id,
            "name": form.get("name"),
            "category": form.get("category"),
            "subtitle": form.get("subtitle"),
            "description": form.get("description"),
            "image": form.get("image"),
            "instructor": {
                "name": form.get("instructor_name"),
                "title": form.get("instructor_title"),
                "image": form.get("instructor_image"),
                "bio": form.get("instructor_bio")
            },
            "stats": courses[course_id]["stats"],
            "features": {
                "level": form.get("level"),
                "duration": form.get("duration"),
                "lectures": int(form.get("lectures")),
                "hours": int(form.get("hours")),
                "projects": int(form.get("projects"))
            },
            "price": {
                "original": float(form.get("original_price")),
                "discounted": float(form.get("discounted_price"))
            }
        }

        # Parse curriculum JSON
        try:
            curriculum = json.loads(form.get("curriculum"))
            course_data["curriculum"] = curriculum
        except json.JSONDecodeError:
            course_data["curriculum"] = []

        # Update existing course
        courses[course_id] = course_data
        
        return JSONResponse({
            "success": True,
            "redirect": "/admin/dashboard"
        })
    except Exception as e:
        logging.error(f"Error updating course: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/admin/courses/{course_id}", response_class=JSONResponse)
async def delete_course(request: Request, course_id: str):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    del courses[course_id]
    return JSONResponse({"success": True})

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

@app.get("/admin/courses/new", response_class=HTMLResponse)
async def new_course_form(request: Request):
    return templates.TemplateResponse(
        "admin/course_form.html",
        {"request": request, "categories": categories, "course": None, "current_time": datetime.now()}
    )

@app.get("/admin/courses/{course_id}/edit", response_class=HTMLResponse)
async def edit_course_form(request: Request, course_id: str):
    course = courses.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse(
        "admin/course_form.html",
        {"request": request, "categories": categories, "course": course, "current_time": datetime.now()}
    )

# Email configuration
EMAIL_HOST = os.getenv("MAIL_SERVER", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("MAIL_USERNAME", "farrza111@gmail.com")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "zcnu rshv xlih yacf")
EMAIL_FROM = os.getenv("MAIL_FROM", "farrza111@gmail.com")
EMAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Tech Learning Hub")

# Email route
@app.post("/send-email")
async def send_email(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    try:
        # Create message
        email_message = MIMEText(
            f"""
            New Contact Form Submission
            
            Name: {name}
            Email: {email}
            
            Message:
            {message}
            """
        )
        email_message["Subject"] = f"{EMAIL_FROM_NAME} - Contact Form: {subject}"
        email_message["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        email_message["To"] = EMAIL_FROM
        email_message["Reply-To"] = f"{name} <{email}>"

        # Connect to SMTP server
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(email_message)

        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )

@app.post("/api/book-meeting")
async def book_meeting(request: MeetingRequest, background_tasks: BackgroundTasks):
    """Handle meeting booking requests."""
    try:
        # Add email sending to background tasks using the email_utils function
        form_data = {
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "message": request.message
        }
        
        background_tasks.add_task(send_email_from_utils, form_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Müraciətiniz qəbul edildi! Tezliklə sizinlə əlaqə saxlanılacaq."}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Müraciətiniz göndərilmədi. Zəhmət olmasa bir az sonra yenidən cəhd edin."
        )

async def send_email_from_utils(form_data: dict):
    """Helper function to send email using email_utils."""
    from utils.email_utils import send_email
    await send_email(form_data)

# Course Enrollment Routes
@app.post("/api/courses/{course_id}/enroll")
async def enroll_course(
    request: Request,
    course_id: str
):
    try:
        if course_id not in courses:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Here you would typically:
        # 1. Check if user is authenticated
        # 2. Process payment
        # 3. Add course to user's enrolled courses
        # 4. Update course statistics
        
        # For now, we'll just return success
        return {
            "status": "success",
            "message": "Successfully enrolled in course",
            "course": courses[course_id]
        }
    except Exception as e:
        logger.error(f"Error enrolling in course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
