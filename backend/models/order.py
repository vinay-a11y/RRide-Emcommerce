from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from database.connection import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    items = Column(Text, nullable=False)  # JSON array stored as string
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=False)  # JSON stored as string
    payment_method = Column(String(50), nullable=False)  # razorpay, cod
    payment_status = Column(String(50), default="pending", index=True)  # pending, completed, failed
    order_status = Column(String(50), default="placed", index=True)  # placed, processing, shipped, delivered, cancelled
    razorpay_order_id = Column(String(100), nullable=True, unique=True)
    razorpay_payment_id = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Order {self.id}>"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    compatibility = Column(Text, nullable=True)  # JSON stored as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<OrderItem {self.product_name}>"
