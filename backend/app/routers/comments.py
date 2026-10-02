from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Comment, Video, User
from app.schemas import CommentCreate, CommentOut
from app.services.auth_service import get_current_user

router = APIRouter(tags=["Comentarios"])

@router.post("/videos/{id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )
    
    comment = Comment(
        content=comment_in.content,
        user_id=current_user.id,
        video_id=id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return db.query(Comment).options(joinedload(Comment.author)).filter(Comment.id == comment.id).first()

@router.get("/videos/{id}/comments", response_model=List[CommentOut])
def get_video_comments(id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )
    
    comments = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.video_id == id
    ).order_by(Comment.created_at.asc()).all()

    return comments
