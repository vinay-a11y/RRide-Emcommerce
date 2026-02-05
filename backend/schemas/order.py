# backend/schemas/order.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: float
    compatibility: Optional[dict] = None

class OrderCreate(BaseModel):
    items: list
    total_amount: float
    shipping_address: dict
    payment_method: str
    
class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    price: float
    compatibility: Optional[dict] = None

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemResponse]
    total_amount: float
    shipping_address: dict
    payment_method: str
    payment_status: str
    order_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
