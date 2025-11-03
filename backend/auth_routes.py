# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, UserCreate, UserOut, Token
from crud import get_user_by_username, create_user
from auth import verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Register
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("Password:", user.password)
    print("Password type:", type(user.password))
    print("Password length:", len(user.password))
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return create_user(db, user.username, user.email, user.password)

# Login
@router.post("/token", response_model=Token)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user helper
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Protected route example
@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
