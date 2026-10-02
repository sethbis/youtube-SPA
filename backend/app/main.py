import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, videos, comments

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de plataforma de videos con FastAPI, AWS S3 y RDS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuracion de CORS para permitir peticiones desde S3 Frontend y desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta local para uploads en modo desarrollo/contingencia
upload_path = os.path.join(os.getcwd(), "uploads")
os.makedirs(upload_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

# Registrar routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(comments.router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs"
    }
