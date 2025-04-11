import motor.motor_asyncio
from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongourl)
db = client["auth_db"]
user_collection = db["users"]
