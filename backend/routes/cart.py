from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import json
from database.connection import get_db
from models.cart import Cart, CartItem
from models.product import Product
from schemas.cart import CartItemCreate, CartResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        # Create new cart if doesn't exist
        new_cart = Cart(user_id=current_user.id)
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart
    
    return cart
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from database.connection import get_db
from models.cart import Cart, CartItem
from schemas.cart import CartItemCreate
from routes.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add")
async def add_to_cart(
    item: CartItemCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Cart).where(Cart.user_id == user.id)
    )
    cart = result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.flush()  # get cart.id

    cart_item = CartItem(
        cart_id=cart.id,
        product_id=item.product_id,
        quantity=item.quantity,
        selected_compatibility=json.dumps(
            item.selected_compatibility.model_dump()
        ) if item.selected_compatibility else None
    )

    db.add(cart_item)
    await db.commit()

    return {"message": "Item added to cart"}

@router.put("/update-item/{cart_item_id}")
async def update_cart_item(
    cart_item_id: str,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    cart = db.query(Cart).filter(Cart.id == cart_item.cart_id).first()
    if cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.commit()
    
    return {"message": "Cart item updated"}

@router.delete("/remove-item/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    cart = db.query(Cart).filter(Cart.id == cart_item.cart_id).first()
    if cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart"}

@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
    
    return {"message": "Cart cleared"}
