from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from app.config.redis_config import get_redis_client
from app.models.user import UserCreate, UserInDB, UserResponse

class UserService:
    @classmethod
    async def get_redis(cls):
        return await get_redis_client()

    @classmethod
    async def get_all_users(cls) -> List[UserResponse]:
        redis = await cls.get_redis()
        users = await redis.hgetall("users")
        return [UserResponse(**json.loads(user)) for user in users.values()]

    @classmethod
    async def get_user_by_username(cls, username: str) -> Optional[UserInDB]:
        redis = await cls.get_redis()
        user_data = await redis.hget("users", username)
        if not user_data:
            return None
        return UserInDB(**json.loads(user_data))

    @classmethod
    async def create_user(cls, user_data: UserCreate) -> UserResponse:
        redis = await cls.get_redis()
        user_dict = {
            **user_data.model_dump(),
            "created_at": datetime.now(),
            "last_login": None,
            "learning_streak": 0,
            "courses_enrolled": [],
            "courses_completed": []
        }
        await redis.hset("users", user_data.username, json.dumps(user_dict))
        return UserResponse(**user_dict)

    @classmethod
    async def update_user(cls, username: str, user_data: dict) -> Optional[UserResponse]:
        redis = await cls.get_redis()
        existing_user = await cls.get_user_by_username(username)
        if not existing_user:
            return None
        
        updated_user = existing_user.model_dump()
        updated_user.update(user_data)
        
        await redis.hset("users", username, json.dumps(updated_user))
        return UserResponse(**updated_user)

    @classmethod
    async def delete_user(cls, username: str) -> bool:
        redis = await cls.get_redis()
        if await redis.hexists("users", username):
            await redis.hdel("users", username)
            return True
        return False

    @classmethod
    async def get_user_courses(cls, username: str) -> List[str]:
        user = await cls.get_user_by_username(username)
        if not user:
            return []
        return user.courses_enrolled

    @classmethod
    async def calculate_user_stats(cls, username: str) -> Dict:
        user = await cls.get_user_by_username(username)
        if not user:
            return {}
        
        return {
            "total_courses": len(user.courses_enrolled),
            "completed_courses": len(user.courses_completed),
            "learning_streak": user.learning_streak
        }

    @classmethod
    async def get_user_certificates(cls, username: str) -> List[Dict]:
        redis = await cls.get_redis()
        certificates = await redis.hgetall(f"certificates:{username}")
        return [json.loads(cert) for cert in certificates.values()] if certificates else []

    @classmethod
    async def get_streak_data(cls, username: str) -> Dict:
        user = await cls.get_user_by_username(username)
        if not user:
            return {"current_streak": 0, "best_streak": 0}
        
        redis = await cls.get_redis()
        streak_key = f"streak:{username}"
        current_streak = await redis.get(streak_key)
        best_streak_key = f"best_streak:{username}"
        best_streak = await redis.get(best_streak_key)
        
        return {
            "current_streak": int(current_streak) if current_streak else 0,
            "best_streak": int(best_streak) if best_streak else 0
        }

    @classmethod
    async def process_course_purchase(cls, username: str, course_id: str) -> bool:
        user = await cls.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        
        if course_id in user.courses_enrolled:
            raise ValueError("Course already purchased")
        
        user_dict = user.model_dump()
        user_dict["courses_enrolled"].append(course_id)
        
        redis = await cls.get_redis()
        await redis.hset("users", username, json.dumps(user_dict))
        return True

    @classmethod
    async def update_course_progress(cls, username: str, course_id: str, module_id: int) -> bool:
        user = await cls.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        
        if course_id not in user.courses_enrolled:
            raise ValueError("Course not enrolled")
        
        progress_key = f"progress:{username}:{course_id}"
        redis = await cls.get_redis()
        
        # Update progress
        await redis.hset(progress_key, str(module_id), "completed")
        
        # Check if course is completed
        total_modules = await redis.hlen(progress_key)
        completed_modules = len([1 for status in await redis.hvals(progress_key) if status == "completed"])
        
        if total_modules == completed_modules:
            user_dict = user.model_dump()
            if course_id not in user_dict["courses_completed"]:
                user_dict["courses_completed"].append(course_id)
                await redis.hset("users", username, json.dumps(user_dict))
                
                # Generate certificate
                certificate_id = f"cert_{course_id}_{username}"
                certificate = {
                    "id": certificate_id,
                    "course_id": course_id,
                    "username": username,
                    "completion_date": datetime.now().isoformat()
                }
                await redis.hset(f"certificates:{username}", certificate_id, json.dumps(certificate))
        
        return True

    @classmethod
    async def get_certificate(cls, username: str, certificate_id: str) -> Optional[Dict]:
        redis = await cls.get_redis()
        certificate = await redis.hget(f"certificates:{username}", certificate_id)
        return json.loads(certificate) if certificate else None
