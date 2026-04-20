from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select


from app.db.session import get_session
from app.schemas.user import CreateUser, LoginUser
from app.model.user import User
from app.core.security import password_hash, verify_password, DUMMY_HASH, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user_data: CreateUser, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_data.username or User.email == user_data.email))
    if user:
        raise HTTPException(status_code=409, detail="Пользователь существует")
    hash = password_hash(user_data.password)
    new_user = User(username=user_data.username, password = hash, email=user_data.email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_data: LoginUser, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_data.username or User.email == user_data.email))
    if not user:
        verify_password( user_data.password, DUMMY_HASH)
        return HTTPException()
    if not verify_password(user_data.password, user.hashed_password):
        return HTTPException(status_code=401)
    
    access_token = create_token({"sub": str (user.id)})
    return access_token({"token": access_token, "token_type": "bearer"})