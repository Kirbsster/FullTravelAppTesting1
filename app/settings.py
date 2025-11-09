from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = Field(default="Bike Viz API", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")

    # Auth
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Mongo

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()