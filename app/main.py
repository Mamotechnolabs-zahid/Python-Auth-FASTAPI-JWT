from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from jose import JWTError, jwt
from app.auth import router as auth_router
from app.config import settings
from app.database import database, metadata
from sqlalchemy import create_engine

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

engine = create_engine(settings.postgreSQLurl.replace("+asyncpg", ""))
metadata.create_all(engine)

@app.on_event("startup")
async def connect_db():
    await database.connect()

@app.on_event("shutdown")
async def disconnect_db():
    await database.disconnect()

@app.get("/dashboard")
async def dashboard(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.jwtsecret, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        return {"message": f"Welcome {user_email} to you dashboard!"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My JWT Auth API",
        version="1.0.0",
        description="Secure endpoints using JWT with Swagger",
        routes=app.routes,
    )

    # Add BearerAuth to security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Add BearerAuth globally to all paths
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.include_router(auth_router)
app.openapi = custom_openapi   

