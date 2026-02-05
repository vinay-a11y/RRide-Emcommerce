from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user import User
from schemas.user import UserRegister, UserLogin, UserResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if mobile already exists
    existing_user = db.query(User).filter(User.mobile == user_data.mobile).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    new_user = User(
        mobile=user_data.mobile,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        email=user_data.email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    token = create_access_token({"sub": new_user.id})
    
    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "mobile": new_user.mobile,
            "name": new_user.name,
            "email": new_user.email
        }
    }

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.mobile == credentials.mobile).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile or password"
        )
    
    # Create access token
    token = create_access_token({"sub": user.id})
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "mobile": user.mobile,
            "name": user.name,
            "email": user.email
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}
