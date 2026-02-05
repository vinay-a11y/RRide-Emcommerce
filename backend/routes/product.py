from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from database.connection import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    bike_brand: Optional[str] = Query(None),
    bike_model: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(None),
    best_sellers: Optional[bool] = Query(None),
    new_arrivals: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get products with filters and sorting"""
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if best_sellers:
        query = query.filter(Product.is_best_seller == True)
    if new_arrivals:
        query = query.filter(Product.is_new_arrival == True)
    
    # Apply sorting
    if sort_by == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "popularity":
        query = query.order_by(Product.reviews_count.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.limit(100).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get single product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new product (admin only)"""
    # TODO: Add admin check here
    
    new_product = Product(
        name=product_data.name,
        category=product_data.category,
        brand=product_data.brand,
        price=product_data.price,
        original_price=product_data.original_price,
        description=product_data.description,
        specifications=json.dumps(product_data.specifications) if product_data.specifications else "{}",
        image_url=product_data.image_url,
        images=json.dumps(product_data.images) if product_data.images else "[]",
        stock=product_data.stock,
        compatibility=json.dumps([c.dict() for c in product_data.compatibility]) if product_data.compatibility else "[]",
        installation_difficulty=product_data.installation_difficulty,
        warranty=product_data.warranty,
        is_best_seller=product_data.is_best_seller,
        is_new_arrival=product_data.is_new_arrival
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/categories/all", tags=["categories"])
async def get_categories():
    """Get all product categories"""
    return [
        {
            "name": "Performance",
            "slug": "performance",
            "image": "https://images.unsplash.com/photo-1761583780521-7723c3569361?crop=entropy&cs=srgb&fm=jpg&q=85"
        },
        {
            "name": "Safety Gear",
            "slug": "safety_gear",
            "image": "https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"
        },
        {
            "name": "Pro Spares",
            "slug": "pro_spares",
            "image": "https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85"
        },
        {
            "name": "Accessories",
            "slug": "accessories",
            "image": "https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"
        }
    ]
@router.post("/seed", tags=["seed"])
def seed_products(db: Session = Depends(get_db)):
    """Seed initial products (run once)"""

    existing = db.query(Product).first()
    if existing:
        return {"message": "Products already seeded"}

    products = [
        Product(
            name="Performance Exhaust System",
            category="Performance",
            brand="Akrapovic",
            price=25999,
            original_price=32999,
            description="Premium titanium exhaust system for enhanced performance and sound",
            specifications=json.dumps({
                "material": "Titanium",
                "weight": "2.5kg",
                "power_gain": "+5HP"
            }),
            image_url="https://images.unsplash.com/photo-1620937843955-a177ceba979e",
            images=json.dumps([]),
            stock=15,
            compatibility=json.dumps([
                {"brand": "KTM", "model": "Duke 390", "variant": "2024"},
                {"brand": "KTM", "model": "Duke 390", "variant": "2023"}
            ]),
            installation_difficulty="Hard",
            warranty="2 Years",
            is_best_seller=True,
            is_new_arrival=False
        ),
        Product(
            name="Premium Full Face Helmet",
            category="Safety Gear",
            brand="AGV",
            price=18999,
            original_price=24999,
            description="DOT certified full face helmet with aerodynamic design",
            specifications=json.dumps({
                "certification": "DOT, ECE",
                "weight": "1.3kg"
            }),
            image_url="https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2",
            images=json.dumps([]),
            stock=30,
            compatibility=json.dumps([
                {"brand": "KTM", "model": "Duke 390"},
                {"brand": "BMW", "model": "G 310 R"}
            ]),
            installation_difficulty="Easy",
            warranty="1 Year",
            is_best_seller=True,
            is_new_arrival=True
        ),
        Product(
            name="Chain & Sprocket Kit",
            category="Pro Spares",
            brand="DID",
            price=4599,
            original_price=5999,
            description="Heavy duty chain and sprocket kit for long lasting performance",
            specifications=json.dumps({
                "chain_type": "O-Ring",
                "links": "120"
            }),
            image_url="https://images.unsplash.com/photo-1633281256183-c0f106f70d76",
            images=json.dumps([]),
            stock=45,
            compatibility=json.dumps([
                {"brand": "KTM", "model": "Duke 250"},
                {"brand": "Yamaha", "model": "MT-15"}
            ]),
            installation_difficulty="Medium",
            warranty="6 Months",
            is_best_seller=False,
            is_new_arrival=False
        ),
        Product(
            name="LED Headlight Bulb",
            category="Accessories",
            brand="Philips",
            price=1299,
            original_price=1799,
            description="High intensity LED headlight bulb with white light",
            specifications=json.dumps({
                "brightness": "6000K",
                "power": "30W"
            }),
            image_url="https://images.unsplash.com/photo-1649027421785-6827863f0891",
            images=json.dumps([]),
            stock=100,
            compatibility=json.dumps([
                {"brand": "Royal Enfield", "model": "Classic 350"}
            ]),
            installation_difficulty="Easy",
            warranty="1 Year",
            is_best_seller=False,
            is_new_arrival=True
        ),
    ]

    db.add_all(products)
    db.commit()

    return {
        "message": "Products seeded successfully",
        "count": len(products)
    }
