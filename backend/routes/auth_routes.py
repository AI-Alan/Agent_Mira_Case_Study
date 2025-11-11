from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.user_model import UserCreate, UserInDB, UserResponse, Token
from services.auth_service import AuthService, get_current_active_user
from core.db import db

router = APIRouter()

def get_auth_service() -> AuthService:
    return AuthService(db)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user_in_db = await auth_service.create_user(user)
        # Return user without password
        return UserResponse(
            id=user_in_db.id,
            email=user_in_db.email,
            name=user_in_db.name,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is
        raise http_exc
    except ValueError as ve:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        # For other exceptions, provide a more helpful error message
        import traceback
        error_detail = str(e)
        print(f"Registration error: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail if error_detail else "Failed to create user. Please check your input."
        )

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return access token"""
    try:
        user = await auth_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = await auth_service.create_access_token_for_user(user)
        return token
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Login error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
