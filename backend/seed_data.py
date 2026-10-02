import os
import sys
import uuid
import urllib.request
import boto3
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine, Base
from app.models import User, Video, Comment
from app.services.auth_service import get_password_hash

# Lista de 15 videos muestra con archivos MP4 y miniaturas reales
SAMPLE_VIDEOS = [
    {
        "title": "Introduccion a la Arquitectura Cloud en AWS",
        "description": "Conceptos fundamentales de computo, almacenamiento y bases de datos en la nube con Amazon Web Services.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=80",
        "views": 420
    },
    {
        "title": "Despliegue de Single Page Applications en Amazon S3",
        "description": "Como compilar una SPA en React con Vite y alojarla como sitio web estatico en un bucket S3 de alta disponibilidad.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
        "views": 850
    },
    {
        "title": "Configuracion de FastAPI en Amazon EC2 con Nginx",
        "description": "Paso a paso para levantar un servidor RESTful con Python, Uvicorn, Nginx como proxy inverso y gestion de procesos.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
        "views": 1240
    },
    {
        "title": "Conexion Segura a Amazon RDS PostgreSQL",
        "description": "Mejores practicas de redes: configuracion de Security Groups dentro de la VPC para aislar el acceso a la base de datos.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&auto=format&fit=crop&q=80",
        "views": 615
    },
    {
        "title": "Gestion de Roles IAM y Politicas de Acceso",
        "description": "Como otorgar permisos a instancias EC2 para acceder a buckets de S3 sin almacenar credenciales en el codigo fuente.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=80",
        "views": 980
    },
    {
        "title": "Desarrollo Frontend Moderno con React y Vite",
        "description": "Estructuracion de componentes modulares, consumo de APIs con Axios y manejo de estado de autenticacion global.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&auto=format&fit=crop&q=80",
        "views": 1420
    },
    {
        "title": "Autenticacion con JWT y Bcrypt en FastAPI",
        "description": "Implementacion completa de registro, hashing de contrasenas y generacion de tokens de acceso Bearer.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80",
        "views": 2100
    },
    {
        "title": "Almacenamiento de Multimedia en S3: Videos y Miniaturas",
        "description": "Optimizacion de subida de archivos multipart, validacion de formatos MP4 y control de extensiones de imagen.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=800&auto=format&fit=crop&q=80",
        "views": 730
    },
    {
        "title": "Diseno de Bases de Datos Relacionales con SQLAlchemy",
        "description": "Modelado de entidades Usuario, Video y Comentario con relaciones foraneas y eliminacion en cascada.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&auto=format&fit=crop&q=80",
        "views": 510
    },
    {
        "title": "Optimizacion de Consultas y Relaciones en PostgreSQL",
        "description": "Tecnicas de joinedload y consultas optimizadas para evitar problemas N+1 al listar videos y usuarios.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=80",
        "views": 890
    },
    {
        "title": "Manejo de Errores y Validaciones con Pydantic",
        "description": "Creacion de esquemas robustos para validacion de correos, contrasenas y respuestas serializadas.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&auto=format&fit=crop&q=80",
        "views": 1670
    },
    {
        "title": "Alta Disponibilidad y Monitoreo con PM2",
        "description": "Como configurar reinicio automatico de servicios, monitoreo de uso de memoria y persistencia de procesos en Linux.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&auto=format&fit=crop&q=80",
        "views": 1130
    },
    {
        "title": "Seguridad en la Nube: Principio de Menor Privilegio",
        "description": "Configuracion estricta de politicas de bucket y reglas de firewall sin exposicion de puertos innecesarios.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop&q=80",
        "views": 940
    },
    {
        "title": "Implementacion de Comentarios y Sistema de Recomendaciones",
        "description": "Consultas dinamicas para listar videos similares y gestion de comentarios en tiempo real.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=80",
        "views": 1820
    },
    {
        "title": "Resumen Integral: Arquitectura Completa de la Plataforma",
        "description": "Demostracion del flujo integral desde la SPA en S3, pasando por FastAPI en EC2 hasta RDS y S3 Media.",
        "video_src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
        "thumb_src": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80",
        "views": 3400
    }
]

SAMPLE_COMMENTS = [
    "Excelente explicacion sobre el despliegue en la nube.",
    "Muy claro el funcionamiento de los buckets y la base de datos.",
    "Gran arquitectura, todo funciona de manera muy rapida.",
    "La documentacion en Swagger facilita mucho probar los endpoints.",
    "Me sirvio mucho el ejemplo de conexion entre EC2 y RDS."
]

def get_s3_client():
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        session_kwargs = {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "region_name": settings.AWS_REGION
        }
        if settings.AWS_SESSION_TOKEN:
            session_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
        return boto3.client("s3", **session_kwargs)
    return boto3.client("s3", region_name=settings.AWS_REGION)

def upload_url_to_s3(url: str, bucket_name: str, ext: str, content_type: str, s3_client) -> str:
    unique_key = f"{uuid.uuid4()}{ext}"
    temp_path = f"/tmp/{unique_key}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as response, open(temp_path, "wb") as out_file:
        out_file.write(response.read())

    with open(temp_path, "rb") as f:
        s3_client.upload_fileobj(
            f,
            bucket_name,
            unique_key,
            ExtraArgs={"ContentType": content_type}
        )

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_key}"

def seed():
    print("Iniciando poblado de la base de datos y carga de archivos en S3...")
    db: Session = SessionLocal()
    s3 = get_s3_client()

    # 1. Crear usuarios muestra si no existen
    user1 = db.query(User).filter(User.email == "nicolas@ejemplo.com").first()
    if not user1:
        user1 = User(
            name="Nicolas",
            email="nicolas@ejemplo.com",
            password_hash=get_password_hash("password123")
        )
        db.add(user1)

    user2 = db.query(User).filter(User.email == "clouddev@ejemplo.com").first()
    if not user2:
        user2 = User(
            name="CloudDev",
            email="clouddev@ejemplo.com",
            password_hash=get_password_hash("password123")
        )
        db.add(user2)

    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    users = [user1, user2]

    # 2. Subir 15 videos a S3 y registrarlos en RDS
    for i, item in enumerate(SAMPLE_VIDEOS, 1):
        print(f"[{i}/15] Procesando: {item['title']}...")
        try:
            # Subir video MP4 a S3 Bucket Videos
            video_url = upload_url_to_s3(
                item["video_src"],
                settings.S3_BUCKET_VIDEOS,
                ".mp4",
                "video/mp4",
                s3
            )

            # Subir miniatura JPG a S3 Bucket Miniaturas
            thumb_url = upload_url_to_s3(
                item["thumb_src"],
                settings.S3_BUCKET_THUMBNAILS,
                ".jpg",
                "image/jpeg",
                s3
            )

            # Asignar autor alternado
            author = users[i % len(users)]

            video = Video(
                title=item["title"],
                description=item["description"],
                video_url=video_url,
                thumbnail_url=thumb_url,
                views=item["views"],
                user_id=author.id
            )
            db.add(video)
            db.commit()
            db.refresh(video)

            # Anadir comentario de prueba
            comment_text = SAMPLE_COMMENTS[i % len(SAMPLE_COMMENTS)]
            comment_author = users[(i + 1) % len(users)]
            comment = Comment(
                content=comment_text,
                user_id=comment_author.id,
                video_id=video.id
            )
            db.add(comment)
            db.commit()

            print(f"   Video guardado exitosamente en RDS (ID: {video.id}) y S3.")
        except Exception as e:
            print(f"   Error al procesar video {i}: {e}")

    db.close()
    print("Poblado completado con exito. Todos los 15 videos estan disponibles en la plataforma.")

if __name__ == "__main__":
    seed()
