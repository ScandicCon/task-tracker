from datetime import timedelta, timezone, datetime
import jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlmodel import select, Session
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE, ALGORITHM 
from app.db.session import get_session
from app.model.user import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

password_hasher = PasswordHash.recommended()

def password_hash(password: str):
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hasher.verify(plain_password, hashed_password)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token:str = Depends(oauth2_schema), session : Session = Depends(get_session)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    user = session.exec(select(User).where(user_id == User.id)).first
    if not User:
        return HTTPException(status_code=401)
    return user