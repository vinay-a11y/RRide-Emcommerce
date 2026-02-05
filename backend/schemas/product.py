from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class BikeCompatibilitySchema(BaseModel):
    brand: str
    model: str
    variant: str
    
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    category: str
    brand: str
    price: float
    original_price: Optional[float] = None
    description: str
    specifications: Optional[Dict] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    stock: int = 0
    compatibility: Optional[List[BikeCompatibilitySchema]] = None
    installation_difficulty: Optional[str] = "Medium"
    warranty: Optional[str] = "1 Year"
    is_best_seller: Optional[bool] = False
    is_new_arrival: Optional[bool] = False

class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    brand: str
    price: float
    original_price: Optional[float] = None
    description: str
    specifications: Optional[Dict] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    stock: int
    compatibility: Optional[List[BikeCompatibilitySchema]] = None
    installation_difficulty: str
    warranty: str
    rating: float
    reviews_count: int
    is_best_seller: bool
    is_new_arrival: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
