from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings


# Password hashing context with proper handling for bcrypt 72-byte limit
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__min_rounds=12
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    Note: bcrypt has a 72-byte password length limit, so we use the utility function.
    """
    from utils.password_utils import verify_bcrypt_password
    return verify_bcrypt_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password.
    Note: bcrypt has a 72-byte password length limit, so we use the utility function.
    """
    from utils.password_utils import hash_bcrypt_password
    return hash_bcrypt_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the given data and expiration time.
    """
    # Defensive copy to avoid None issues
    if not data or not isinstance(data, dict):
        data = {}
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid.
    """
    try:
        if not token:
            return None
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Ensure payload is a dictionary before returning
        if isinstance(payload, dict):
            return payload
        else:
            return None
    except JWTError:
        return None
    except Exception:
        # Catch any other exceptions that might occur during token verification
        return None