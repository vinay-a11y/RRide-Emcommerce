from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from database.connection import get_db
from models.order import Order, OrderItem
from models.cart import Cart, CartItem
from models.product import Product
from schemas.order import OrderCreate, OrderResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new order"""
    # Validate items exist and check stock
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        items=json.dumps([item.dict() for item in order_data.items]),
        total_amount=order_data.total_amount,
        shipping_address=json.dumps(order_data.shipping_address),
        payment_method=order_data.payment_method,
        payment_status="pending",
        order_status="placed"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Update product stock
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity
    
    # Clear user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    
    return new_order

@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for current user"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    # TODO: Add admin check here
    
    valid_statuses = ["placed", "processing", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.order_status = new_status
    order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": f"Order status updated to {new_status}", "order": order}

@router.put("/{order_id}/payment-status")
async def update_payment_status(
    order_id: str,
    payment_status: str,
    razorpay_payment_id: str = None,
    razorpay_order_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update payment status"""
    # TODO: Add Razorpay verification here
    
    valid_statuses = ["pending", "completed", "failed"]
    if payment_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    order.payment_status = payment_status
    if razorpay_payment_id:
        order.razorpay_payment_id = razorpay_payment_id
    if razorpay_order_id:
        order.razorpay_order_id = razorpay_order_id
    order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "Payment status updated", "order": order}

@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if order.order_status == "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel delivered order"
        )
    
    order.order_status = "cancelled"
    order.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "Order cancelled"}
