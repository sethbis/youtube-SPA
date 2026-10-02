import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Video Platform API"
    API_V1_STR: str = ""
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./video_platform.db"
    )
    
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_SESSION_TOKEN: str = os.getenv("AWS_SESSION_TOKEN", "")
    
    S3_BUCKET_VIDEOS: str = os.getenv("S3_BUCKET_VIDEOS", "video-platform-videos-nicolas")
    S3_BUCKET_THUMBNAILS: str = os.getenv("S3_BUCKET_THUMBNAILS", "video-platform-thumbnails-nicolas")
    S3_BUCKET_FRONTEND: str = os.getenv("S3_BUCKET_FRONTEND", "video-platform-frontend-nicolas")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
