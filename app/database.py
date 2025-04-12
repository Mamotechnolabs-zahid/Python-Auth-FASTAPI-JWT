from databases import Database
from sqlalchemy import MetaData
from app.config import settings

database = Database(settings.postgreSQLurl)
metadata = MetaData()


#import motor.motor_asyncio
#from app.config import settings

#client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongourl)
#db = client["auth_db"]
#user_collection = db["users"]
