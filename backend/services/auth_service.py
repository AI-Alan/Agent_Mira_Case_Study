from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user_model import (
    UserInDB, UserCreate, Token, TokenData,
    verify_password, get_password_hash, create_access_token
)
from core.config import settings
from core.db import db

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]

    async def create_user(self, user: UserCreate) -> UserInDB:
        try:
            # Check if user already exists
            existing_user = await self.users.find_one({"email": user.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user - use model_dump() for Pydantic v2
            user_dict = user.model_dump()
            hashed_password = get_password_hash(user_dict.pop("password"))
            user_dict["hashed_password"] = hashed_password
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            
            # Insert user into database
            result = await self.users.insert_one(user_dict)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user in database"
                )
            
            user_dict["id"] = str(result.inserted_id)
            
            return UserInDB(**user_dict)
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Error in create_user: {error_msg}")
            print(traceback.format_exc())
            
            # Provide user-friendly error messages
            if "authentication failed" in error_msg.lower() or "bad auth" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database authentication failed. Please check your MONGO_URI in .env file. Make sure username and password are correct."
                )
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to connect to database. Please check your MongoDB URI and network connection."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {error_msg[:200]}"  # Limit error message length
                )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        try:
            user = await self.users.find_one({"email": email})
            if not user:
                print(f"User not found for email: {email}")
                return None
            
            user_dict = dict(user, id=str(user["_id"]))
            try:
                user_in_db = UserInDB(**user_dict)
            except Exception as e:
                print(f"Error creating UserInDB: {e}")
                return None
            
            if not verify_password(password, user_in_db.hashed_password):
                print(f"Password verification failed for email: {email}")
                return None
                
            print(f"User authenticated successfully: {email}")
            return user_in_db
        except Exception as e:
            print(f"Error in authenticate_user: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserInDB:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
            
        user = await self.users.find_one({"email": token_data.email})
        if user is None:
            raise credentials_exception
            
        user_dict = dict(user, id=str(user["_id"]))
        return UserInDB(**user_dict)

    async def create_access_token_for_user(self, user: UserInDB) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

# Dependency to get the current active user
async def get_current_active_user(
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)
