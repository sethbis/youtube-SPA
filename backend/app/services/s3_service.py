import os
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from app.config import settings

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
    # Si no se proporcionan credenciales explícitas, boto3 usa el IAM Role asignado a EC2
    return boto3.client("s3", region_name=settings.AWS_REGION)

def upload_file_to_s3(
    file: UploadFile,
    bucket_name: str,
    allowed_extensions: list,
    max_size_mb: int = 100
) -> str:
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido: {ext}. Formatos permitidos: {', '.join(allowed_extensions)}"
        )

    file_bytes = file.file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    if file_size_mb > max_size_mb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamano maximo permitido de {max_size_mb} MB"
        )

    file.file.seek(0)
    unique_filename = f"{uuid.uuid4()}{ext}"

    content_type = file.content_type or "application/octet-stream"

    # Intentar subir a S3
    try:
        s3 = get_s3_client()
        s3.upload_fileobj(
            file.file,
            bucket_name,
            unique_filename,
            ExtraArgs={
                "ContentType": content_type
            }
        )
        url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        return url
    except Exception as e:
        print(f"Error al subir a S3 ({bucket_name}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de subida a Amazon S3 en {bucket_name}: {str(e)}"
        )

def delete_file_from_s3(file_url: str, bucket_name: str) -> bool:
    try:
        key = file_url.split("/")[-1]
        s3 = get_s3_client()
        s3.delete_object(Bucket=bucket_name, Key=key)
        return True
    except Exception:
        return False
