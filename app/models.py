from sqlalchemy import Table, Column, Integer, String
from app.database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True),
    Column("password", String)
)


#def user_helper(user) -> dict:
#    return {
#        "id": str(user["_id"]),
#        "email": user["email"]
#    }