from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from core.security import create_access_token, verify_token
from datetime import timedelta
from db.session import get_session
from models.user import UserDB, UserCreate, UserLogin, hash_password
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
from fastapi.responses import JSONResponse

router = APIRouter()

# Security scheme for Swagger UI
security_scheme = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return db.query(UserDB).filter(UserDB.email == email).first()

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_session)):
    """
    Authenticate user and return JWT token.
    """
    try:
        # Find user by email
        user = get_user_by_email(db, login_request.email)

        # Use the utility function to verify the password with 72-byte limit handling
        from utils.password_utils import verify_bcrypt_password
        if not user or not verify_bcrypt_password(login_request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )

@router.post("/signup", response_model=TokenResponse)
def signup(signup_request: SignupRequest, db: Session = Depends(get_session)):
    """
    Register a new user and return JWT token.
    """
    try:
        print(f"Signup attempt for email: {signup_request.email}")  # Debug print

        # Check if user already exists
        existing_user = get_user_by_email(db, signup_request.email)
        if existing_user:
            print(f"User already exists: {signup_request.email}")  # Debug print
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        print("About to hash password...")  # Debug print
        # Use the utility function to hash the password with 72-byte limit handling
        from utils.password_utils import hash_bcrypt_password
        hashed_password = hash_bcrypt_password(signup_request.password)
        print(f"Password hashed successfully")  # Debug print

        print("About to create user object...")  # Debug print
        # Create new user
        db_user = UserDB(
            email=signup_request.email,
            name=signup_request.name,
            hashed_password=hashed_password
        )
        print(f"User object created: {db_user.email}")  # Debug print

        print("About to add user to session...")  # Debug print
        db.add(db_user)
        
        # Handle potential integrity errors during commit
        try:
            print("About to commit transaction...")  # Debug print
            db.commit()
            print(f"Transaction committed")  # Debug print

            print("About to refresh user...")  # Debug print
            db.refresh(db_user)
            print(f"User refreshed from DB: ID {db_user.id}")  # Debug print
        except IntegrityError as e:
            db.rollback()
            print(f"IntegrityError during commit: {str(e)}")  # Debug print
            # Check if the error is specifically about the email being duplicated
            if "email" in str(e).lower() or "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                # Some other integrity constraint was violated
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A database constraint was violated: {str(e)}"
                )

        print("About to create access token...")  # Debug print
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email},
            expires_delta=access_token_expires
        )
        print(f"Access token created")  # Debug print

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except IntegrityError as e:
        print(f"IntegrityError during signup: {str(e)}")  # Debug print
        db.rollback()
        # Check if the error is specifically about the email being duplicated
        if "email" in str(e).lower() or "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            # Some other integrity constraint was violated
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A database constraint was violated: {str(e)}"
            )
    except Exception as e:
        print(f"General error during signup: {str(e)}")  # Debug print
        import traceback
        traceback.print_exc()  # Print full traceback
        db.rollback()
        # Provide more specific error information
        error_detail = str(e)
        if "connection" in error_detail.lower() or "database" in error_detail.lower():
            error_detail = f"Database connection error: {error_detail}"
        elif "table" in error_detail.lower():
            error_detail = f"Database table error: {error_detail}"
        elif "column" in error_detail.lower():
            error_detail = f"Database column error: {error_detail}"
        elif "duplicate" in error_detail.lower() or "unique constraint" in error_detail.lower():
            error_detail = "Email already registered"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {error_detail}"
        )

# Add register endpoint for compatibility with frontend expectations
@router.post("/register", response_model=TokenResponse)
def register(signup_request: SignupRequest, db: Session = Depends(get_session)):
    """
    Register a new user and return JWT token (alias for signup).
    """
    # Call the signup function to reuse the same logic
    return signup(signup_request, db)

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Logout endpoint - in a real app, this might blacklist the token.
    """
    # In a real application, you might add the token to a blacklist
    # For now, we just acknowledge the logout
    return {"message": "Successfully logged out"}



# Better Auth Compatible Endpoints
@router.post("/sign-up",
             summary="Sign up a new user",
             description="Register a new user account with email, password, and optional name.")
async def better_auth_signup(request: Request):
    """
    Better Auth compatible signup endpoint
    """
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        name = body.get('name')

        # Validate input
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )

        # Get database session using the dependency
        from db.session import SessionLocal
        db = SessionLocal()

        try:
            # Check if user already exists
            existing_user = get_user_by_email(db, email)
            if existing_user:
                print(f"User already exists in DB: {email}")  # Debug print
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Use the utility function to hash the password with 72-byte limit handling
            from utils.password_utils import hash_bcrypt_password
            hashed_password = hash_bcrypt_password(password)

            # Create new user
            db_user = UserDB(
                email=email,
                name=name,
                hashed_password=hashed_password
            )

            db.add(db_user)
            
            # Commit and handle potential integrity errors
            try:
                db.commit()
                db.refresh(db_user)
            except IntegrityError as e:
                db.rollback()
                # Check if the error is specifically about the email being duplicated
                if "email" in str(e).lower() or "duplicate" in str(e).lower() or "unique" in str(e).lower():
                    print(f"IntegrityError: Email already exists: {email}")  # Debug print
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    # Some other integrity constraint was violated
                    print(f"Other IntegrityError: {str(e)}")  # Debug print
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"A database constraint was violated: {str(e)}"
                    )

            # Create access token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": str(db_user.id), "email": db_user.email},
                expires_delta=access_token_expires
            )

            # Return Better Auth compatible response
            # Ensure createdAt and updatedAt are properly formatted
            created_at_iso = db_user.created_at.isoformat() if db_user.created_at else None
            updated_at_iso = db_user.updated_at.isoformat() if db_user.updated_at else None
            # Calculate expiration time from current time, not from creation time
            from datetime import datetime
            expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()

            return {
                "user": {
                    "id": str(db_user.id),
                    "email": db_user.email,
                    "name": db_user.name or "",
                    "emailVerified": False,
                    "createdAt": created_at_iso,
                    "updatedAt": updated_at_iso,
                },
                "session": {
                    "id": access_token,  # Using JWT as session ID
                    "expiresAt": expires_at,
                    "userId": str(db_user.id)
                },
                "token": access_token
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.post("/sign-in/email",
             summary="Sign in a user",
             description="Authenticate a user with email and password.")
async def better_auth_signin(request: Request):
    """
    Better Auth compatible signin endpoint
    """
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')

        # Validate input
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )

        # Get database session using the dependency
        from db.session import SessionLocal
        db = SessionLocal()

        try:
            # Find user by email
            user = get_user_by_email(db, email)
            
            # Use the utility function to verify the password with 72-byte limit handling
            from utils.password_utils import verify_bcrypt_password
            if not user or not verify_bcrypt_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Inactive user",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Create access token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )

            # Return Better Auth compatible response
            # Ensure createdAt and updatedAt are properly formatted
            created_at_iso = user.created_at.isoformat() if user.created_at else None
            updated_at_iso = user.updated_at.isoformat() if user.updated_at else None
            # Calculate expiration time from current time, not from creation time
            from datetime import datetime
            expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()

            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name or "",
                    "emailVerified": False,
                    "createdAt": created_at_iso,
                    "updatedAt": updated_at_iso,
                },
                "session": {
                    "id": access_token,  # Using JWT as session ID
                    "expiresAt": expires_at,
                    "userId": str(user.id)
                },
                "token": access_token
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.get("/session")
def better_auth_session(request: Request):
    """
    Better Auth compatible session endpoint
    Manually extract token from Authorization header to avoid dependency issues
    """
    try:
        # Manually extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid authorization header"
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Verify the token with maximum error protection
        payload = None
        try:
            payload = verify_token(token)
        except Exception as e:
            print(f"Exception in verify_token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )

        # Ensure payload is a valid dictionary before accessing
        if payload is None or not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Safely extract values from payload
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get database session using the dependency
        from db.session import SessionLocal
        db = SessionLocal()

        try:
            # Get user from database
            user = db.query(UserDB).filter(UserDB.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # Create access token with defensive checks
            access_token_expires = timedelta(minutes=30)
            token_data = {
                "sub": str(user.id) if user and user.id else "",
                "email": user.email if user and user.email else ""
            }
            access_token = create_access_token(
                data=token_data,
                expires_delta=access_token_expires
            )

            # Return Better Auth compatible response
            # Calculate expiration time from current time, not from creation time
            from datetime import datetime
            expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
            
            return JSONResponse(
                status_code=200,
                content={
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "name": user.name,
                        "emailVerified": False,
                        "createdAt": user.created_at.isoformat() if user.created_at else None,
                        "updatedAt": user.updated_at.isoformat() if user.updated_at else None,
                    },
                    "session": {
                        "id": access_token,  # Using JWT as session ID
                        "expiresAt": expires_at,
                        "userId": str(user.id)
                    },
                    "token": access_token
                }
            )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred getting session: {str(e)}"
        )


# Mount Better Auth compatible endpoints at the root level
# This creates the endpoints that Better Auth client expects
from fastapi import APIRouter

# Create a separate router for Better Auth compatible endpoints
better_auth_router = APIRouter()

@better_auth_router.post("/sign-up")
async def root_better_auth_signup(request: Request):
    """
    Root level Better Auth compatible signup endpoint
    """
    # Forward to the actual implementation
    return await better_auth_signup(request)

@better_auth_router.post("/sign-in/email")
async def root_better_auth_signin(request: Request):
    """
    Root level Better Auth compatible signin endpoint
    """
    # Forward to the actual implementation
    return await better_auth_signin(request)

@better_auth_router.get("/session")
def root_better_auth_session(request: Request):
    """
    Root level Better Auth compatible session endpoint
    """
    # Forward to the actual implementation
    return better_auth_session(request)

@better_auth_router.post("/sign-out")
def root_better_auth_signout(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Root level Better Auth compatible signout endpoint
    """
    # In a real implementation, you might add the token to a blacklist
    # For now, we just acknowledge the logout
    return {"message": "Successfully logged out"}

# Export the router so it can be imported in main.py