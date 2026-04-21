from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_session
from app.schemas.user import CreateUser, LoginUser
from app.model.user import User
from app.core.security import password_hash, verify_password, DUMMY_HASH, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user_data: CreateUser, session: Session = Depends(get_session)):
    user = session.exec(select(User).where((User.username == user_data.username) | (User.email == user_data.email))).first()
    if user:
        raise HTTPException(status_code=409, detail="Пользователь существует")
    hash_ps = password_hash(user_data.password)
    new_user = User(username=user_data.username,email=user_data.email, hashed_password = hash_ps )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.username)
        )
    ).first()

    if not user:
        verify_password(user_data.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}