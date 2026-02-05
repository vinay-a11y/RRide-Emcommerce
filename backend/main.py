from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import aiomysql
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import json
from urllib.parse import urlparse

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MySQL connection pool
db_pool = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    global db_pool

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set")

    parsed = urlparse(db_url)

    db_pool = await aiomysql.create_pool(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        db=parsed.path.lstrip("/"),
        port=parsed.port or 3306,
        autocommit=True,
        minsize=1,
        maxsize=10
    )

    logger.info("Database pool initialized using DATABASE_URL")

async def get_db():
    """Get database cursor from pool"""
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)

# Create FastAPI app
app = FastAPI(title="Bike Shop API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ MODELS ============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    mobile: str
    password_hash: str
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

class UserRegister(BaseModel):
    mobile: str
    password: str
    name: Optional[str] = None
    email: Optional[str] = None

class UserLogin(BaseModel):
    mobile: str
    password: str

class BikeModel(BaseModel):
    id: str
    brand: str
    model: str
    variant: str

class ProductBrand(BaseModel):
    id: str
    name: str
    logo: Optional[str] = None

class SpareCategory(BaseModel):
    id: str
    name: str
    slug: str
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    brand_id: str
    spare_category_id: str
    product_type: str          # 👈 ADD THIS
    price: float
    original_price: Optional[float] = None
    description: str
    images: List[str] = []
    stock: int
    rating: float = 4.5
    reviews_count: int = 0
    is_best_seller: bool = False
    is_new_arrival: bool = False
    created_at: datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemResponse(CartItem):
    product: Optional[dict] = None

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM users WHERE id = %s",
                    (user_id.strip(),)
                )
                user = await cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User.model_validate(user)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user_data: UserRegister, cursor = Depends(get_db)):
    """Register new user"""
    await cursor.execute("SELECT id FROM users WHERE mobile = %s", (user_data.mobile,))
    existing = await cursor.fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    user_id = str(uuid.uuid4())
    password_hash = hash_password(user_data.password)
    
    await cursor.execute(
        """INSERT INTO users (id, mobile, password_hash, name, email, created_at) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, user_data.mobile, password_hash, user_data.name, user_data.email, datetime.now(timezone.utc))
    )
    
    token = create_access_token({"sub": user_id})
    return {"token": token, "user": {"id": user_id, "mobile": user_data.mobile, "name": user_data.name}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin, cursor = Depends(get_db)):
    """Login user"""
    await cursor.execute("SELECT * FROM users WHERE mobile = %s", (credentials.mobile,))
    user = await cursor.fetchone()
    
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid mobile or password")
    
    token = create_access_token({"sub": user['id']})
    return {"token": token, "user": {"id": user['id'], "mobile": user['mobile'], "name": user.get('name')}}

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "mobile": current_user.mobile,
        "name": current_user.name,
        "email": current_user.email
    }

# ============ BIKE ROUTES ============

@api_router.get("/bikes/brands")
async def get_bike_brands(cursor = Depends(get_db)):
    """Get all bike brands with models"""
    await cursor.execute("""
        SELECT DISTINCT brand FROM bikes ORDER BY brand
    """)
    brands = await cursor.fetchall()
    
    result = []
    for brand_row in brands:
        brand_name = brand_row['brand']
        await cursor.execute("""
            SELECT DISTINCT model FROM bikes WHERE brand = %s ORDER BY model
        """, (brand_name,))
        models = await cursor.fetchall()
        
        result.append({
            "name": brand_name,
            "logo": f"https://via.placeholder.com/150?text={brand_name}",
            "models": [m['model'] for m in models]
        })
    
    return result

@api_router.get("/bikes/models/{brand}")
async def get_bike_models(brand: str, cursor = Depends(get_db)):
    """Get models for a bike brand"""
    await cursor.execute("""
        SELECT DISTINCT model FROM bikes WHERE brand = %s ORDER BY model
    """, (brand,))
    models = await cursor.fetchall()
    return [m['model'] for m in models]

@api_router.get("/bikes/variants/{brand}/{model}")
async def get_bike_variants(brand: str, model: str, cursor = Depends(get_db)):
    """Get variants for a bike model"""
    await cursor.execute("""
        SELECT DISTINCT variant FROM bikes WHERE brand = %s AND model = %s ORDER BY variant
    """, (brand, model))
    variants = await cursor.fetchall()
    return [v['variant'] for v in variants]

# ============ PRODUCTS ROUTES ============
@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    product_type: Optional[str] = Query(None, regex="^(spare|accessory)$"),  # 👈 NEW
    bike_brand: Optional[str] = None,
    bike_model: Optional[str] = None,
    bike_variant: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    best_sellers: Optional[bool] = None,
    new_arrivals: Optional[bool] = None,
    cursor = Depends(get_db)
):

    """Get products with optional filters"""
    query = "SELECT DISTINCT p.* FROM products p"
    params = []
    where_clauses = []
    
    # Join with bikes if bike filter provided
    if bike_brand and bike_model and bike_variant:
        query += """
            JOIN product_bike_compatibility pbc ON p.id = pbc.product_id
            JOIN bikes b ON pbc.bike_id = b.id
        """
        where_clauses.append("b.brand = %s")
        where_clauses.append("b.model = %s")
        where_clauses.append("b.variant = %s")
        params.extend([bike_brand, bike_model, bike_variant])
    
    # Other filters
    if category:
        where_clauses.append("p.spare_category_id = %s")
        params.append(category)
    
    if brand:
        where_clauses.append("p.brand_id = %s")
        params.append(brand)
    
    if best_sellers:
        where_clauses.append("p.is_best_seller = 1")
    
    if new_arrivals:
        where_clauses.append("p.is_new_arrival = 1")
    
    if min_price is not None:
        where_clauses.append("p.price >= %s")
        params.append(min_price)
    
    if max_price is not None:
        where_clauses.append("p.price <= %s")
        params.append(max_price)

    if product_type:
        where_clauses.append("p.product_type = %s")
        params.append(product_type)

    # Build WHERE clause
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Sorting
    order_by = "p.created_at DESC"
    if sort_by == "price_low":
        order_by = "p.price ASC"
    elif sort_by == "price_high":
        order_by = "p.price DESC"
    elif sort_by == "popularity":
        order_by = "p.reviews_count DESC"
    
    query += f" ORDER BY {order_by} LIMIT 100"
    
    await cursor.execute(query, params)
    products = await cursor.fetchall()
    
    return [normalize_product(p) for p in products]

@api_router.get("/products/spares")
async def get_spares(cursor=Depends(get_db)):
    await cursor.execute(
        "SELECT * FROM products WHERE product_type = 'spare' ORDER BY created_at DESC"
    )
    return [normalize_product(p) for p in await cursor.fetchall()]


@api_router.get("/products/accessories")
async def get_accessories(cursor=Depends(get_db)):
    await cursor.execute(
        "SELECT * FROM products WHERE product_type = 'accessory' ORDER BY created_at DESC"
    )
    return [normalize_product(p) for p in await cursor.fetchall()]

# 🔍 SEARCH — MUST COME FIRST
@api_router.get("/products/search")
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    cursor = Depends(get_db)
):
    search_term = f"%{q.strip()}%"
    
    await cursor.execute("""
        SELECT DISTINCT p.* FROM products p
        LEFT JOIN product_brands pb ON p.brand_id = pb.id
        LEFT JOIN spare_categories sc ON p.spare_category_id = sc.id
        WHERE p.name LIKE %s
           OR pb.name LIKE %s
           OR sc.name LIKE %s
        ORDER BY p.rating DESC
        LIMIT %s
    """, (search_term, search_term, search_term, limit))
    
    products = await cursor.fetchall()
    return [normalize_product(p) for p in products]

@api_router.get("/products/{product_id}")
async def get_product(product_id: str, cursor = Depends(get_db)):
    """Get single product by ID"""
    await cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = await cursor.fetchone()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get compatible bikes
    await cursor.execute("""
        SELECT DISTINCT b.* FROM bikes b
        JOIN product_bike_compatibility pbc ON b.id = pbc.bike_id
        WHERE pbc.product_id = %s
    """, (product_id,))
    compatible_bikes = await cursor.fetchall()
    
    result = normalize_product(product)
    result['compatibility'] = compatible_bikes
    return result



# ============ CATEGORIES ROUTES ============

@api_router.get("/categories")
async def get_categories(cursor = Depends(get_db)):
    """Get all spare categories"""
    await cursor.execute("SELECT * FROM spare_categories ORDER BY name")
    categories = await cursor.fetchall()
    
    return [
        {
            "id": cat['id'],
            "name": cat['name'],
            "slug": cat['slug'],
            "image": f"https://via.placeholder.com/400?text={cat['name']}"
        }
        for cat in categories
    ]

@api_router.get("/brands")
async def get_brands(cursor = Depends(get_db)):
    """Get all product brands"""
    await cursor.execute("SELECT * FROM product_brands ORDER BY name")
    brands = await cursor.fetchall()
    return brands

# ============ CART ROUTES ============

@api_router.get("/cart")
async def get_cart(current_user: User = Depends(get_current_user), cursor = Depends(get_db)):
    """Get user's cart"""
    await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
    cart = await cursor.fetchone()
    
    if not cart:
        return {"items": []}
    
    items = json.loads(cart.get('items', '[]'))
    
    enriched_items = []
    for item in items:
        await cursor.execute("SELECT * FROM products WHERE id = %s", (item['product_id'],))
        product = await cursor.fetchone()
        
        if product:
            enriched_items.append({
                **item,
                "product": normalize_product(product)
            })
    
    return {"items": enriched_items}

@api_router.post("/cart/add")
async def add_to_cart(item: CartItem, current_user: User = Depends(get_current_user), cursor = Depends(get_db)):
    """Add item to cart"""
    await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
    cart = await cursor.fetchone()
    
    if not cart:
        cart_id = str(uuid.uuid4())
        items = [item.model_dump()]
        await cursor.execute(
            "INSERT INTO carts (id, user_id, items, updated_at) VALUES (%s, %s, %s, %s)",
            (cart_id, current_user.id, json.dumps(items), datetime.now(timezone.utc))
        )
    else:
        items = json.loads(cart.get('items', '[]'))
        
        existing_item = None
        for i, cart_item in enumerate(items):
            if cart_item['product_id'] == item.product_id:
                existing_item = i
                break
        
        if existing_item is not None:
            items[existing_item]['quantity'] += item.quantity
        else:
            items.append(item.model_dump())
        
        await cursor.execute(
            "UPDATE carts SET items = %s, updated_at = %s WHERE user_id = %s",
            (json.dumps(items), datetime.now(timezone.utc), current_user.id)
        )
    
    return {"message": "Item added to cart"}

@api_router.delete("/cart/remove/{product_id}")
async def remove_from_cart(product_id: str, current_user: User = Depends(get_current_user), cursor = Depends(get_db)):
    """Remove item from cart"""
    await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
    cart = await cursor.fetchone()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = json.loads(cart.get('items', '[]'))
    items = [item for item in items if item['product_id'] != product_id]
    
    await cursor.execute(
        "UPDATE carts SET items = %s, updated_at = %s WHERE user_id = %s",
        (json.dumps(items), datetime.now(timezone.utc), current_user.id)
    )
    
    return {"message": "Item removed from cart"}

# ============ HELPER FUNCTIONS ============

def normalize_product(product: dict) -> dict:
    """Normalize product data from database"""
    if not product:
        return product
    
    try:
        product["images"] = json.loads(product["images"]) if product.get("images") else []
    except:
        product["images"] = []
    
    return product

# ============ STARTUP & SHUTDOWN ============

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown"""
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()

# Include routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Bike Shop API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
