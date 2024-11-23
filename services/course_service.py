import json
from typing import Dict, Optional
from models.course import CourseBase, CourseCreate
from redis import asyncio as aioredis

class CourseService:
    redis = None

    @classmethod
    async def initialize(cls):
        if not cls.redis:
            cls.redis = await aioredis.from_url('redis://localhost')

    @classmethod
    async def get_all_courses(cls) -> Dict:
        if not cls.redis:
            await cls.initialize()
        
        # Get all course IDs
        course_keys = await cls.redis.keys('course:*')
        courses = {}
        
        # Get each course's data
        for key in course_keys:
            course_id = key.decode('utf-8').split(':')[1]
            course_data = await cls.redis.get(f'course:{course_id}')
            if course_data:
                courses[course_id] = json.loads(course_data)
        
        return courses

    @classmethod
    async def get_course(cls, course_id: str) -> Optional[Dict]:
        if not cls.redis:
            await cls.initialize()
        
        course_data = await cls.redis.get(f'course:{course_id}')
        return json.loads(course_data) if course_data else None

    @classmethod
    async def create_course(cls, course: CourseCreate) -> str:
        if not cls.redis:
            await cls.initialize()
        
        # Generate course ID if not provided
        course_id = course.id or course.title.lower().replace(' ', '-')
        
        # Prepare course data
        course_data = {
            "id": course_id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "duration": course.duration,
            "modules": course.modules,
            "outcomes": course.outcomes
        }
        
        # Store in Redis
        await cls.redis.set(
            f'course:{course_id}',
            json.dumps(course_data)
        )
        
        return course_id

    @classmethod
    async def update_course(cls, course_id: str, course: CourseBase) -> bool:
        if not cls.redis:
            await cls.initialize()
        
        # Check if course exists
        existing_course = await cls.get_course(course_id)
        if not existing_course:
            return False
        
        # Update course data
        course_data = {
            "id": course_id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "duration": course.duration,
            "modules": course.modules,
            "outcomes": course.outcomes
        }
        
        # Store updated data
        await cls.redis.set(
            f'course:{course_id}',
            json.dumps(course_data)
        )
        
        return True

    @classmethod
    async def delete_course(cls, course_id: str) -> bool:
        if not cls.redis:
            await cls.initialize()
        
        # Check if course exists
        if not await cls.get_course(course_id):
            return False
        
        # Delete course
        await cls.redis.delete(f'course:{course_id}')
        return True

    @classmethod
    async def cleanup(cls):
        if cls.redis:
            await cls.redis.close()
