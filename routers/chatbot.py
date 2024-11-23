from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    sender: str  # 'user' or 'bot'

class ChatResponse(BaseModel):
    response: str

# Detailed course information
courses_info = {
    "python": {
        "name": "Python Programming",
        "duration": "8 weeks",
        "price": "$99",
        "description": "Learn Python from basics to advanced concepts, including web development with Django and Flask."
    },
    "javascript": {
        "name": "JavaScript Development",
        "duration": "10 weeks",
        "price": "$129",
        "description": "Master JavaScript, React, and Node.js for full-stack web development."
    },
    "data_science": {
        "name": "Data Science Fundamentals",
        "duration": "12 weeks",
        "price": "$199",
        "description": "Learn data analysis, machine learning, and visualization with Python."
    },
    "web_dev": {
        "name": "Web Development Bootcamp",
        "duration": "16 weeks",
        "price": "$299",
        "description": "Comprehensive web development course covering HTML, CSS, JavaScript, and modern frameworks."
    }
}

# Enhanced responses dictionary
responses = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! Welcome to Tech Learning Hub. What would you like to know about our courses?",
        "Welcome! I'm here to help you find the perfect course. What are you interested in learning?"
    ],
    
    "courses_general": """We offer several popular courses:
1. Python Programming (8 weeks) - Perfect for beginners
2. JavaScript Development (10 weeks) - For aspiring web developers
3. Data Science Fundamentals (12 weeks) - Learn data analysis and ML
4. Web Development Bootcamp (16 weeks) - Comprehensive web dev course

Which course would you like to know more about?""",
    
    "pricing_general": """Our course pricing is structured to provide maximum value:
• Entry-level courses: $99-$129
• Intermediate courses: $149-$199
• Advanced bootcamps: $249-$299

All courses include:
✓ Lifetime access to course materials
✓ Project-based learning
✓ Personal mentor support
✓ Course completion certificate

Would you like pricing details for a specific course?""",
    
    "duration_general": """Course durations are designed to fit your schedule:
• Short courses: 4-6 weeks
• Standard courses: 8-12 weeks
• Comprehensive bootcamps: 12-16 weeks

All courses offer:
✓ Flexible learning pace
✓ Part-time friendly schedule
✓ Weekly live sessions
✓ Self-paced modules

Which course duration interests you?""",
    
    "help_general": """I can help you with:
1. Course Information
   • Available courses
   • Course content
   • Prerequisites
   
2. Pricing & Payment
   • Course fees
   • Payment plans
   • Refund policy
   
3. Learning Experience
   • Course duration
   • Learning format
   • Support available
   
4. Technical Support
   • Access issues
   • Platform navigation
   • Resource downloads

What specific information would you like to know?""",
    
    "fallback": "I'm not sure about that. Would you like to know about our courses, pricing, or duration? You can also type 'help' to see what I can assist you with."
}

def get_course_info(course_name: str) -> str:
    course = courses_info.get(course_name.lower().replace(" ", "_"))
    if course:
        return f""" {course['name']}
• Duration: {course['duration']}
• Price: {course['price']}
• Description: {course['description']}

Would you like to know more about the course content or enroll?"""
    return None

def get_bot_response(message: str) -> str:
    message = message.lower()
    
    # Greeting responses
    if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
        return responses["greeting"][0]
    
    # Course specific information
    for course in courses_info.keys():
        if course.replace("_", " ") in message:
            course_info = get_course_info(course)
            if course_info:
                return course_info
    
    # General course information
    if "course" in message:
        return responses["courses_general"]
    
    # Pricing information
    if any(word in message for word in ["price", "cost", "fee", "payment"]):
        return responses["pricing_general"]
    
    # Duration information
    if any(word in message for word in ["duration", "long", "time", "weeks"]):
        return responses["duration_general"]
    
    # Help information
    if any(word in message for word in ["help", "support", "assist", "guide"]):
        return responses["help_general"]
    
    # Fallback response
    return responses["fallback"]

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    bot_response = get_bot_response(message.message)
    return ChatResponse(response=bot_response)
