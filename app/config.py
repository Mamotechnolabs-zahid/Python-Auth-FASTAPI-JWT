from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongourl: str  # <-- Add this line
    accesstokenexpireminutes: int = 30
    jwtsecret: str = "Zahid5104"
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
