from fastapi import APIRouter, HTTPException, Depends
from app.schemas import User, Token, UpdateUser
from fastapi.security import OAuth2PasswordBearer
from app.database import database
from app.models import users
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    query = users.select().where(users.c.email == user.email)
    existing = await database.fetch_one(query)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = get_password_hash(user.password)
    query = users.insert().values(email=user.email, password=hashed_pwd)
    await database.execute(query)
    #user_collection.insert_one({"email": user.email, "password": hashed_pwd})
    return {"msg": "User registered Successfully"}

@router.post("/login", response_model=Token)
async def login(user: User):
    query = users.select().where(users.c.email == user.email)
    db_user = await database.fetch_one(query)
    # db_user = await user_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.put("/update-user", response_model=dict)
async def update_user(update: UpdateUser, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        query = users.select().where(users.c.email == user_email)
        db_user = await database.fetch_one(query)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data={}
        if update.email:
            update_data["email"] = update.email
        if update.password:
            update_data["password"] = get_password_hash(update.password)

        update_query = users.update().where(users.c.email == user_email).values(**update_data)
        await database.execute(update_query)

        return {"msg": "User updated successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

@router.delete("/delete-user", response_model=dict)
async def delete_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        query = users.select().where(users.c.email == user_email)
        db_user = database.fetch_one(query)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        delete_query = users.delete().where(users.c.email == user_email)
        await database.execute(delete_query)

        return {"msg": "User deleted Successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.get("/users", response_model=list[dict])
async def get_all_users(token: str= Depends(oauth2_scheme)):
    try:
        jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        query = users.select()
        all_users = await database.fetch_all(query)
        return [{"email": u["email"]} for u in all_users]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

@router.get("/me", response_model=dict)
async def get_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        query = users.select().where(users.c.email == user_email)
        db_user = await database.fetch_one(query)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"email": db_user["email"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

    