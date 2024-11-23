import uuid
import json
from typing import List, Optional, Dict
from app.models.course import CourseBase, CourseCreate
from redis import Redis
from app.config.redis_config import get_redis_client

class CourseService:
    @classmethod
    async def get_redis(cls) -> Redis:
        return await get_redis_client()

    @classmethod
    async def get_all_courses(cls) -> List[dict]:
        redis = await cls.get_redis()
        courses = await redis.hgetall("courses")
        return [json.loads(course) for course in courses.values()]

    @classmethod
    async def get_course_by_id(cls, course_id: str) -> Optional[dict]:
        redis = await cls.get_redis()
        course = await redis.hget("courses", course_id)
        return json.loads(course) if course else None

    @classmethod
    async def create_course(cls, course: CourseCreate) -> dict:
        course_id = course.id or str(uuid.uuid4())
        course_dict = {
            "id": course_id,
            **course.model_dump()
        }
        redis = await cls.get_redis()
        await redis.hset("courses", course_id, json.dumps(course_dict))
        return course_dict

    @classmethod
    async def update_course(cls, course_id: str, course: CourseBase) -> Optional[dict]:
        redis = await cls.get_redis()
        existing_course = await cls.get_course_by_id(course_id)
        if not existing_course:
            return None
        
        updated_course = {
            **existing_course,
            **course.model_dump(exclude_unset=True)
        }
        await redis.hset("courses", course_id, json.dumps(updated_course))
        return updated_course

    @classmethod
    async def delete_course(cls, course_id: str) -> bool:
        redis = await cls.get_redis()
        deleted = await redis.hdel("courses", course_id)
        return bool(deleted)

    @classmethod
    async def get_course_recommendations(cls, user_id: str) -> List[dict]:
        # In a real application, this would use a recommendation algorithm
        # For now, just return all courses
        redis = await cls.get_redis()
        courses = await redis.hgetall("courses")
        return [json.loads(course) for course in courses.values()]

    @classmethod
    async def initialize_demo_courses(cls):
        demo_courses = [
            {
                "id": "power-bi",
                "title": "Power BI Mastery",
                "description": "Master data visualization and business intelligence with Power BI",
                "price": 99.0,
                "duration": "6 weeks",
                "modules": [
                    {"title": "Introduction to Power BI", "content": "Learn the basics of Power BI"},
                    {"title": "Data Modeling", "content": "Master data modeling techniques"},
                    {"title": "DAX Formulas", "content": "Learn advanced DAX formulas"},
                    {"title": "Visualizations", "content": "Create stunning visualizations"}
                ],
                "outcomes": [
                    "Create professional dashboards",
                    "Master data modeling",
                    "Write complex DAX formulas",
                    "Design effective visualizations"
                ]
            },
            {
                "id": "python",
                "title": "Python Programming",
                "description": "Learn Python programming from basics to advanced concepts",
                "price": 149.0,
                "duration": "8 weeks",
                "modules": [
                    {"title": "Python Basics", "content": "Learn Python fundamentals"},
                    {"title": "Data Structures", "content": "Master Python data structures"},
                    {"title": "OOP in Python", "content": "Learn object-oriented programming"},
                    {"title": "Advanced Topics", "content": "Explore advanced Python concepts"}
                ],
                "outcomes": [
                    "Write Python programs",
                    "Use Python data structures",
                    "Create object-oriented applications",
                    "Build real-world projects"
                ]
            },
            {
                "id": "sql",
                "title": "SQL for Data Analysis",
                "description": "Master SQL for data analysis and database management",
                "price": 129.0,
                "duration": "6 weeks",
                "modules": [
                    {"title": "SQL Basics", "content": "Learn SQL fundamentals"},
                    {"title": "Advanced Queries", "content": "Master complex SQL queries"},
                    {"title": "Database Design", "content": "Learn database design principles"},
                    {"title": "Performance Tuning", "content": "Optimize SQL queries"}
                ],
                "outcomes": [
                    "Write complex SQL queries",
                    "Design efficient databases",
                    "Analyze large datasets",
                    "Optimize query performance"
                ]
            }
        ]
        
        redis = await cls.get_redis()
        for course in demo_courses:
            await redis.hset("courses", course["id"], json.dumps(course))
