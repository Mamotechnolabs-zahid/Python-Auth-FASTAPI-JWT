from fastapi import APIRouter, HTTPException, Depends
from app.schemas import User, Token
from app.database import user_collection
from app.models import user_helper
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data:dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.accesstokenexpireminutes)
    data.update({"exp": expire})
    return jwt.encode(data, settings.jwtsecret, algorithm=settings.algorithm)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/register", response_model=dict)
async def register(user: User):
    existing = await user_collection.find_one({"email":user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = get_password_hash(user.password)
    await user_collection.insert_one({"email": user.email, "password": hashed_pwd})
    return {"msg": "User registered Successfully"}

@router.post("/login", response_model=Token)
async def login(user: User):
    db_user = await user_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

