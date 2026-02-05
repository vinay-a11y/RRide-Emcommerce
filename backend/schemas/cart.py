from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from schemas.product import BikeCompatibilitySchema

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1
    selected_compatibility: Optional[BikeCompatibilitySchema] = None

class CartItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    selected_compatibility: Optional[BikeCompatibilitySchema] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
