from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.auth import router as auth_router
from app.config import settings

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/dashboard")
async def dashboard(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        return {"message": f"Welcome {user_email} to you dashboard!"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
app.include_router(auth_router)