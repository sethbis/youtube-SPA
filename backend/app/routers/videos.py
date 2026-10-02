from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload
from app.config import settings
from app.database import get_db
from app.models import Video, User
from app.schemas import VideoOut, VideoUpdate
from app.services.auth_service import get_current_user
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(tags=["Videos"])

@router.post("/videos", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
def create_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validar y subir video a S3 Bucket 2 (Videos)
    video_url = upload_file_to_s3(
        file=video_file,
        bucket_name=settings.S3_BUCKET_VIDEOS,
        allowed_extensions=[".mp4"],
        max_size_mb=100
    )

    # Validar y subir miniatura a S3 Bucket 3 (Miniaturas)
    thumbnail_url = upload_file_to_s3(
        file=thumbnail_file,
        bucket_name=settings.S3_BUCKET_THUMBNAILS,
        allowed_extensions=[".jpg", ".jpeg", ".png"],
        max_size_mb=10
    )

    video = Video(
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        views=0,
        user_id=current_user.id
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    # Cargar relacion de owner
    return db.query(Video).options(joinedload(Video.owner)).filter(Video.id == video.id).first()

@router.get("/videos", response_model=List[VideoOut])
def list_videos(
    user_id: Optional[int] = None,
    exclude_id: Optional[int] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Video).options(joinedload(Video.owner))
    if user_id is not None:
        query = query.filter(Video.user_id == user_id)
    if exclude_id is not None:
        query = query.filter(Video.id != exclude_id)
    
    query = query.order_by(Video.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    return query.all()

@router.get("/videos/{id}", response_model=VideoOut)
def get_video(id: int, db: Session = Depends(get_db)):
    video = db.query(Video).options(joinedload(Video.owner)).filter(Video.id == id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )
    
    # Incrementar vistas
    video.views += 1
    db.commit()
    db.refresh(video)
    return video

@router.put("/videos/{id}", response_model=VideoOut)
def update_video(
    id: int,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).options(joinedload(Video.owner)).filter(Video.id == id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )
    
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar este video"
        )
    
    if video_update.title is not None:
        video.title = video_update.title
    if video_update.description is not None:
        video.description = video_update.description

    db.commit()
    db.refresh(video)
    return video

@router.delete("/videos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )
    
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este video"
        )

    # Intentar eliminar archivos asociados de S3
    delete_file_from_s3(video.video_url, settings.S3_BUCKET_VIDEOS)
    delete_file_from_s3(video.thumbnail_url, settings.S3_BUCKET_THUMBNAILS)

    db.delete(video)
    db.commit()
    return None
