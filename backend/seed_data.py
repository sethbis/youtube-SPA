import os
import io
import uuid
import zlib
import struct
import urllib.request
import boto3
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import User, Video, Comment
from app.services.auth_service import get_password_hash

# 15 combinaciones de colores para generar miniaturas PNG validas sin depender de servidores externos
COLORS = [
    (31, 78, 121),   # Azul cobalto
    (112, 48, 160),  # Purpura
    (0, 128, 128),   # Verde azulado (Teal)
    (192, 0, 0),     # Rojo carmesi
    (237, 125, 49),  # Naranja
    (46, 117, 89),   # Verde esmeralda
    (84, 130, 53),   # Verde oliva
    (68, 84, 106),   # Gris pizarra
    (153, 51, 102),  # Magenta
    (0, 112, 192),   # Azul electrico
    (128, 96, 0),    # Dorado
    (70, 70, 70),    # Gris grafito
    (180, 50, 80),   # Rosa frambuesa
    (20, 90, 140),   # Azul oceano
    (90, 40, 130)    # Violeta oscuro
]

SAMPLE_VIDEOS = [
    {
        "title": "Introduccion a la Arquitectura Cloud en AWS",
        "description": "Conceptos fundamentales de computo, almacenamiento y bases de datos en la nube con Amazon Web Services.",
        "views": 420
    },
    {
        "title": "Despliegue de Single Page Applications en Amazon S3",
        "description": "Como compilar una SPA en React con Vite y alojarla como sitio web estatico en un bucket S3 de alta disponibilidad.",
        "views": 850
    },
    {
        "title": "Configuracion de FastAPI en Amazon EC2 con Nginx",
        "description": "Paso a paso para levantar un servidor RESTful con Python, Uvicorn, Nginx como proxy inverso y gestion de procesos.",
        "views": 1240
    },
    {
        "title": "Conexion Segura a Amazon RDS PostgreSQL",
        "description": "Mejores practicas de redes: configuracion de Security Groups dentro de la VPC para aislar el acceso a la base de datos.",
        "views": 615
    },
    {
        "title": "Gestion de Roles IAM y Politicas de Acceso",
        "description": "Como otorgar permisos a instancias EC2 para acceder a buckets de S3 sin almacenar credenciales en el codigo fuente.",
        "views": 980
    },
    {
        "title": "Desarrollo Frontend Moderno con React y Vite",
        "description": "Estructuracion de componentes modulares, consumo de APIs con Axios y manejo de estado de autenticacion global.",
        "views": 1420
    },
    {
        "title": "Autenticacion con JWT y Bcrypt en FastAPI",
        "description": "Implementacion completa de registro, hashing de contrasenas y generacion de tokens de acceso Bearer.",
        "views": 2100
    },
    {
        "title": "Almacenamiento de Multimedia en S3: Videos y Miniaturas",
        "description": "Optimizacion de subida de archivos multipart, validacion de formatos MP4 y control de extensiones de imagen.",
        "views": 730
    },
    {
        "title": "Diseno de Bases de Datos Relacionales con SQLAlchemy",
        "description": "Modelado de entidades Usuario, Video y Comentario con relaciones foraneas y eliminacion en cascada.",
        "views": 510
    },
    {
        "title": "Optimizacion de Consultas y Relaciones en PostgreSQL",
        "description": "Tecnicas de joinedload y consultas optimizadas para evitar problemas N+1 al listar videos y usuarios.",
        "views": 890
    },
    {
        "title": "Manejo de Errores y Validaciones con Pydantic",
        "description": "Creacion de esquemas robustos para validacion de correos, contrasenas y respuestas serializadas.",
        "views": 1670
    },
    {
        "title": "Alta Disponibilidad y Monitoreo con PM2",
        "description": "Como configurar reinicio automatico de servicios, monitoreo de uso de memoria y persistencia de procesos en Linux.",
        "views": 1130
    },
    {
        "title": "Seguridad en la Nube: Principio de Menor Privilegio",
        "description": "Configuracion estricta de politicas de bucket y reglas de firewall sin exposicion de puertos innecesarios.",
        "views": 940
    },
    {
        "title": "Implementacion de Comentarios y Sistema de Recomendaciones",
        "description": "Consultas dinamicas para listar videos similares y gestion de comentarios en tiempo real.",
        "views": 1820
    },
    {
        "title": "Resumen Integral: Arquitectura Completa de la Plataforma",
        "description": "Demostracion del flujo integral desde la SPA en S3, pasando por FastAPI en EC2 hasta RDS y S3 Media.",
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

def generate_png_bytes(width: int = 640, height: int = 360, color: tuple = (31, 78, 121)) -> bytes:
    r, g, b = color
    png = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data))
    png += struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + ihdr_crc
    
    line = b'\x00' + bytes([r, g, b]) * width
    raw_data = line * height
    compressed = zlib.compress(raw_data)
    idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed))
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
    
    iend_crc = struct.pack('>I', zlib.crc32(b'IEND'))
    png += struct.pack('>I', 0) + b'IEND' + iend_crc
    return png

def get_sample_mp4_bytes() -> bytes:
    urls = [
        "https://www.w3schools.com/html/mov_bbb.mp4",
        "https://vjs.zencdn.net/v/oceans.mp4"
    ]
    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                if len(data) > 1000:
                    return data
        except Exception:
            continue
    # Respaldo de contingencia
    return b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42\x00\x00\x00\x08free\x00\x00\x00\x08mdat'

def get_s3_client():
    return boto3.client("s3", region_name=settings.AWS_REGION)

def seed():
    print("Iniciando poblado seguro de base de datos RDS y buckets S3...")
    db: Session = SessionLocal()
    s3 = get_s3_client()

    # 1. Crear o verificar usuarios
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

    # 2. Obtener archivo MP4 base para cargar
    print("Descargando video MP4 de referencia...")
    mp4_bytes = get_sample_mp4_bytes()
    print(f"Video preparado ({len(mp4_bytes) / 1024:.1f} KB).")

    # 3. Subir los 15 videos y miniaturas a S3 e insertar registros en RDS
    for i, item in enumerate(SAMPLE_VIDEOS):
        video_num = i + 1
        print(f"[{video_num}/15] Subiendo a S3 y RDS: '{item['title']}'...")

        # Subir video MP4 unico a S3
        video_key = f"{uuid.uuid4().hex}.mp4"
        s3.upload_fileobj(
            io.BytesIO(mp4_bytes),
            settings.S3_BUCKET_VIDEOS,
            video_key,
            ExtraArgs={"ContentType": "video/mp4"}
        )
        video_url = f"https://{settings.S3_BUCKET_VIDEOS}.s3.{settings.AWS_REGION}.amazonaws.com/{video_key}"

        # Generar y subir miniatura PNG valida a S3
        color = COLORS[i % len(COLORS)]
        png_bytes = generate_png_bytes(640, 360, color)
        thumb_key = f"{uuid.uuid4().hex}.png"
        s3.upload_fileobj(
            io.BytesIO(png_bytes),
            settings.S3_BUCKET_THUMBNAILS,
            thumb_key,
            ExtraArgs={"ContentType": "image/png"}
        )
        thumb_url = f"https://{settings.S3_BUCKET_THUMBNAILS}.s3.{settings.AWS_REGION}.amazonaws.com/{thumb_key}"

        # Guardar registro en RDS
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
        comment = Comment(
            content=SAMPLE_COMMENTS[i % len(SAMPLE_COMMENTS)],
            user_id=users[(i + 1) % len(users)].id,
            video_id=video.id
        )
        db.add(comment)
        db.commit()

        print(f"   Completado: Video ID {video.id} publicado por {author.name}.")

    db.close()
    print("Poblado completado con exito. Los 15 videos estan listos en S3 y RDS.")

if __name__ == "__main__":
    seed()
