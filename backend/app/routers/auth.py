from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Video
from app.schemas import UserCreate, UserLogin, UserOut, Token
from app.services.auth_service import verify_password, get_password_hash, create_access_token

router = APIRouter(tags=["Usuarios"])

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electronico ya se encuentra registrado"
        )
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    video_count = db.query(Video).filter(Video.user_id == user.id).count()
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        video_count=video_count
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    video_count = db.query(Video).filter(Video.user_id == user.id).count()

    user_out = UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        video_count=video_count
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_out
    )

@router.get("/users/{id}", response_model=UserOut)
def get_user_profile(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    video_count = db.query(Video).filter(Video.user_id == user.id).count()
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        video_count=video_count
    )
