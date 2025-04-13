from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgreSQLurl: str 
    accesstokenexpireminutes: int = 30
    jwtsecret: str
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()

print(settings.postgreSQLurl) 
