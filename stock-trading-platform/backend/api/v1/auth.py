from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserLogin
from core.security import create_access_token, get_password_hash, verify_password
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    db_user = repo.get_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_username = repo.get_by_username(user.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    db_user = repo.create(username=user.username, email=user.email, hashed_password=hashed_password)
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = UserRepository(db).get_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}
