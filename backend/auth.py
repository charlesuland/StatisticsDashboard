# auth.py
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "f3b9d2c4e7a1486b9d4f1c2e8a7b5d1f9e0c3a6b7d4e2f1c8b9a0d6e3f7c2a1b5"  # Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------------------
# Hash & verify passwords
# ---------------------------

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    # bcrypt requires bytes, outputs bytes; decode to get string
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# ---------------------------
# JWT token creation
# ---------------------------

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------------
# JWT token verification
# ---------------------------

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
