from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    mobile: str
    password: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    mobile: str
    password: str

class UserResponse(BaseModel):
    id: str
    mobile: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    addresses: Optional[List[dict]] = []
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    addresses: Optional[List[dict]] = None
