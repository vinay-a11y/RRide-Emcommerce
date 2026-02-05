from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import aiomysql
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Union
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MySQL connection pool
db_pool = None

async def init_db():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host="localhost",          # ❗ MUST be this
        user="rride_app",          # ❗ NOT root
        password="AppPassword@123",# the password you set
        db="bike_shop",   # <-- change only this
        port=3306,
        autocommit=True,
        minsize=1,
        maxsize=10
    )
async def get_db():
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.0.237:3000"],
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
    email: Optional[EmailStr] = None
    addresses: Union[str, List[dict]] = []
    created_at: datetime

class UserRegister(BaseModel):
    mobile: str
    password: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    mobile: str
    password: str

class BikeCompatibility(BaseModel):
    model_config = ConfigDict(extra="ignore")
    brand: str  # KTM, BMW, Royal Enfield, Yamaha
    model: str  # Duke 390, Duke 250, etc.
    variant: str  # 2023, 2024, BS6, etc.

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # Performance, Safety Gear, Pro Spares, Accessories
    brand: str
    price: float
    original_price: Optional[float] = None
    description: str
    specifications: dict = {}
    image_url: str
    images: List[str] = []
    stock: int = 0
    compatibility: List[BikeCompatibility] = []  # Compatible bikes
    installation_difficulty: str = "Medium"  # Easy, Medium, Hard
    warranty: str = "1 Year"
    rating: float = 4.5
    reviews_count: int = 0
    is_best_seller: bool = False
    is_new_arrival: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_id: str
    quantity: int = 1
    selected_compatibility: Optional[BikeCompatibility] = None

class Cart(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    compatibility: Optional[BikeCompatibility] = None

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_address: dict
    payment_method: str  # razorpay, cod
    payment_status: str = "pending"  # pending, completed, failed
    order_status: str = "placed"  # placed, processing, shipped, delivered, cancelled
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RazorpayOrderRequest(BaseModel):
    amount: float

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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

        # ✅ SAFE pydantic validation
        return User.model_validate(user)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE mobile = %s", (user_data.mobile,))
            existing = await cursor.fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    user = User(
        mobile=user_data.mobile,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        email=user_data.email
    )
    
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (id, mobile, password_hash, name, email, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (user.id, user.mobile, user.password_hash, user.name, user.email, user.created_at)
            )
            await conn.commit()
    
    token = create_access_token({"sub": user.id})
    return {"token": token, "user": {"id": user.id, "mobile": user.mobile, "name": user.name}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE mobile = %s", (credentials.mobile,))
            user = await cursor.fetchone()
    
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid mobile or password")
    
    token = create_access_token({"sub": user['id']})
    return {"token": token, "user": {"id": user['id'], "mobile": user['mobile'], "name": user.get('name')}}

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "mobile": current_user.mobile,
        "name": current_user.name,
        "email": current_user.email
    }

def normalize_product(product: dict) -> dict:
    """
    Convert JSON string fields from MySQL into proper Python objects
    so frontend always receives correct data types.
    """
    if not product:
        return product

    try:
        product["compatibility"] = (
            json.loads(product["compatibility"])
            if product.get("compatibility")
            else []
        )
    except Exception:
        product["compatibility"] = []

    try:
        product["images"] = (
            json.loads(product["images"])
            if product.get("images")
            else []
        )
    except Exception:
        product["images"] = []

    try:
        product["specifications"] = (
            json.loads(product["specifications"])
            if product.get("specifications")
            else {}
        )
    except Exception:
        product["specifications"] = {}

    return product

# ============ PRODUCTS ROUTES ============
@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    brand_id: Optional[str] = None,
    product_type: Optional[str] = None,  # 'spare' or 'accessory'
    product_name: Optional[str] = None,  # for filtering by specific product names like "Clutch Plate"
    
    # 🔥 BIKE FILTERS (for spares only)
    bike_brand: Optional[str] = None,
    bike_model: Optional[str] = None,
    bike_variant: Optional[str] = None,

    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    best_sellers: Optional[bool] = None,
    new_arrivals: Optional[bool] = None,
    
    # 🔥 PAGINATION
    page: int = 1,
    limit: int = 20
):
    query_parts = []
    params = []

    # ---------- BASIC FILTERS ----------
    if category:
        query_parts.append("spare_category_id = %s")
        params.append(category)
    
    if brand_id:
        query_parts.append("brand_id = %s")
        params.append(brand_id)
    
    if product_type:
        query_parts.append("product_type = %s")
        params.append(product_type)
    
    if product_name:
        query_parts.append("name LIKE %s")
        params.append(f"%{product_name}%")

    if best_sellers:
        query_parts.append("is_best_seller = 1")

    if new_arrivals:
        query_parts.append("is_new_arrival = 1")

    if min_price is not None:
        query_parts.append("price >= %s")
        params.append(min_price)

    if max_price is not None:
        query_parts.append("price <= %s")
        params.append(max_price)

    # ---------- BIKE COMPATIBILITY FILTER ----------
    if bike_brand and bike_model and bike_variant:
        # For spares: filter by bike compatibility
        # For accessories: show all (they're universal)
        query_parts.append(
            """(
                product_type = 'accessory' 
                OR id IN (
                    SELECT DISTINCT pbc.product_id 
                    FROM product_bike_compatibility pbc
                    JOIN bikes b ON pbc.bike_id = b.id
                    WHERE b.brand = %s AND b.model = %s AND b.variant = %s
                )
            )"""
        )
        params.extend([bike_brand, bike_model, bike_variant])

    where_clause = " AND ".join(query_parts) if query_parts else "1=1"

    # ---------- SORT ----------
    order_by = "created_at DESC"
    if sort_by == "price_low":
        order_by = "price ASC"
    elif sort_by == "price_high":
        order_by = "price DESC"
    elif sort_by == "popularity":
        order_by = "reviews_count DESC"
    elif sort_by == "rating":
        order_by = "rating DESC"

    # ---------- PAGINATION ----------
    offset = (page - 1) * limit

    # ---------- FETCH TOTAL COUNT ----------
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f"SELECT COUNT(*) as total FROM products WHERE {where_clause}",
                params
            )
            result = await cursor.fetchone()
            total_count = result[0] if result else 0

    # ---------- FETCH PRODUCTS ----------
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                f"""
                SELECT * FROM products
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset]
            )
            products = await cursor.fetchall()

    # ---------- NORMALIZE ----------
    normalized_products = [normalize_product(p) for p in products]

    return {
        "products": normalized_products,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,),
            )
            product = await cursor.fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get compatible bikes for this product
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT b.* FROM bikes b
                JOIN product_bike_compatibility pbc ON b.id = pbc.bike_id
                WHERE pbc.product_id = %s
                """,
                (product_id,)
            )
            compatible_bikes = await cursor.fetchall()

    # ✅ NORMALIZE PRODUCT
    normalized = normalize_product(product)
    normalized['compatible_bikes'] = compatible_bikes
    return normalized


# ============ NEW: GET PRODUCT SUBCATEGORIES (for filter chips) ============
@api_router.get("/products/subcategories/list")
async def get_product_subcategories(product_type: str):
    """
    Get unique product names grouped by type for filter chips
    e.g., Spares: Clutch Plate, Handle Bar, Chain Kit
          Accessories: Mobile Holder, Helmet, Gloves
    """
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT DISTINCT 
                    TRIM(SUBSTRING_INDEX(name, ' ', 2)) as subcategory,
                    COUNT(*) as count
                FROM products
                WHERE product_type = %s
                GROUP BY subcategory
                ORDER BY count DESC
                """,
                (product_type,)
            )
            subcategories = await cursor.fetchall()
    
    return subcategories


# ============ BRANDS ============
@api_router.get("/brands")
async def get_brands():
    """Get all product brands"""
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT pb.*, COUNT(p.id) as product_count
                FROM product_brands pb
                LEFT JOIN products p ON pb.id = p.brand_id
                GROUP BY pb.id
                ORDER BY pb.name
                """
            )
            brands = await cursor.fetchall()
    return brands


@api_router.get("/categories")
async def get_categories():
    return [
        {"name": "Performance", "slug": "performance", "image": "https://images.unsplash.com/photo-1761583780521-7723c3569361?crop=entropy&cs=srgb&fm=jpg&q=85"},
        {"name": "Safety Gear", "slug": "safety_gear", "image": "https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"},
        {"name": "Pro Spares", "slug": "pro_spares", "image": "https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85"},
        {"name": "Accessories", "slug": "accessories", "image": "https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"}
    ]

# ============ BIKES ROUTES ============

@api_router.get("/bikes/brands")
async def get_bike_brands():
    return [
        {"name": "KTM", "logo": "https://m.media-amazon.com/images/I/510Te9GgpVL._AC_UF1000,1000_QL80_.jpg"},
        {"name": "BMW", "logo": "https://thumbs.dreamstime.com/b/web-136350854.jpg"},
        {"name": "Royal Enfield", "logo": "https://i.pinimg.com/736x/ae/85/23/ae852311b4d932a981d129dce36c5aba.jpg"},
        {"name": "Yamaha", "logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTU3BcHSQmww0zWysg9-SCGRHPDIvWTNzL02A&s"}
    ]

@api_router.get("/bikes/models/{brand}")
async def get_bike_models(brand: str):
    models_map = {
        "KTM": ["Duke 390", "Duke 250", "RC 390", "Adventure 390"],
        "BMW": ["G 310 R", "G 310 GS", "S 1000 RR", "R 1250 GS"],
        "Royal Enfield": ["Classic 350", "Meteor 350", "Himalayan", "Interceptor 650"],
        "Yamaha": ["MT-15", "R15 V4", "FZ-S", "YZF R1"]
    }
    return models_map.get(brand, [])

@api_router.get("/bikes/variants/{brand}/{model}")
async def get_bike_variants(brand: str, model: str):
    return ["2024", "2023", "2022", "BS6"]

# ============ CART ROUTES ============

@api_router.get("/cart")
async def get_cart(current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
            cart = await cursor.fetchone()
    
    if not cart:
        return {"items": []}
    
    # Parse items JSON
    items = json.loads(cart.get('items', '[]'))
    
    # Populate product details
    enriched_items = []
    for item in items:
        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM products WHERE id = %s", (item['product_id'],))
                product = await cursor.fetchone()
        
        if product:
            enriched_items.append({
                **item,
                "product": product
            })
    
    return {**cart, "items": enriched_items}
@api_router.get("/products/search")
async def search_products(
    q: str,
    limit: int = 20
):
    """
    Search products by name, brand, or category
    """
    q = q.strip()

    if len(q) < 2:
        return []

    search_term = f"%{q}%"

    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT DISTINCT p.* 
                FROM products p
                LEFT JOIN product_brands pb ON p.brand_id = pb.id
                LEFT JOIN spare_categories sc ON p.spare_category_id = sc.id
                WHERE
                    p.name LIKE %s
                    OR pb.name LIKE %s
                    OR sc.name LIKE %s
                    OR p.description LIKE %s
                ORDER BY
                    CASE
                        WHEN p.name LIKE %s THEN 1
                        WHEN pb.name LIKE %s THEN 2
                        WHEN sc.name LIKE %s THEN 3
                        ELSE 4
                    END,
                    p.rating DESC
                LIMIT %s
                """,
                (
                    search_term,
                    search_term,
                    search_term,
                    search_term,
                    search_term,
                    search_term,
                    search_term,
                    limit
                )
            )

            products = await cursor.fetchall()

    return [normalize_product(p) for p in products]

@api_router.post("/cart/add")
async def add_to_cart(item: CartItem, current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
            cart = await cursor.fetchone()
    
    if not cart:
        cart_id = str(uuid.uuid4())
        items = [item.model_dump()]
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO carts (id, user_id, items, updated_at) VALUES (%s, %s, %s, %s)",
                    (cart_id, current_user.id, json.dumps(items), datetime.now(timezone.utc))
                )
                await conn.commit()
    else:
        # Parse existing items
        items = json.loads(cart.get('items', '[]'))
        
        # Check if product already in cart
        existing_item = None
        for i, cart_item in enumerate(items):
            if cart_item['product_id'] == item.product_id:
                existing_item = i
                break
        
        if existing_item is not None:
            items[existing_item]['quantity'] += item.quantity
        else:
            items.append(item.model_dump())
        
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE carts SET items = %s, updated_at = %s WHERE user_id = %s",
                    (json.dumps(items), datetime.now(timezone.utc), current_user.id)
                )
                await conn.commit()
    
    return {"message": "Item added to cart"}

@api_router.post("/cart/update")
async def update_cart_item(product_id: str, quantity: int, current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
            cart = await cursor.fetchone()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = json.loads(cart.get('items', '[]'))
    for item in items:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE carts SET items = %s, updated_at = %s WHERE user_id = %s",
                (json.dumps(items), datetime.now(timezone.utc), current_user.id)
            )
            await conn.commit()
    
    return {"message": "Cart updated"}

@api_router.delete("/cart/remove/{product_id}")
async def remove_from_cart(product_id: str, current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM carts WHERE user_id = %s", (current_user.id,))
            cart = await cursor.fetchone()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = json.loads(cart.get('items', '[]'))
    items = [item for item in items if item['product_id'] != product_id]
    
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE carts SET items = %s, updated_at = %s WHERE user_id = %s",
                (json.dumps(items), datetime.now(timezone.utc), current_user.id)
            )
            await conn.commit()
    
    return {"message": "Item removed"}

# ============ ORDERS ROUTES ============

@api_router.post("/orders/create")
async def create_order(order_data: dict, current_user: User = Depends(get_current_user)):
    order = Order(
        user_id=current_user.id,
        items=order_data['items'],
        total_amount=order_data['total_amount'],
        shipping_address=order_data['shipping_address'],
        payment_method=order_data['payment_method']
    )
    
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO orders (id, user_id, items, total_amount, shipping_address, payment_method, payment_status, order_status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (order.id, order.user_id, json.dumps([item if isinstance(item, dict) else item.model_dump() for item in order.items]), order.total_amount, json.dumps(order.shipping_address), order.payment_method, order.payment_status, order.order_status, order.created_at, order.updated_at)
            )
            await conn.commit()
    
    # Clear cart
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM carts WHERE user_id = %s", (current_user.id,))
            await conn.commit()
    
    return order.model_dump()

def normalize_order(order: dict) -> dict:
    if not order:
        return order

    # items
    try:
        order["items"] = (
            json.loads(order["items"])
            if isinstance(order.get("items"), str)
            else order.get("items", [])
        )
    except Exception:
        order["items"] = []

    # shipping_address
    try:
        order["shipping_address"] = (
            json.loads(order["shipping_address"])
            if isinstance(order.get("shipping_address"), str)
            else order.get("shipping_address", {})
        )
    except Exception:
        order["shipping_address"] = {}

    return order

@api_router.get("/orders")
async def get_orders(current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC LIMIT 100", (current_user.id,))
            orders = await cursor.fetchall()
    return [normalize_order(o) for o in orders]



@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, current_user.id))
            order = await cursor.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return normalize_order(order)


@api_router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Update order status
    Valid statuses: placed, confirmed, processing, pickup, delivery, delivered, cancelled
    """
    new_status = status_data.get('status')
    
    valid_statuses = ['placed', 'confirmed', 'processing', 'pickup', 'delivery', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Verify order belongs to user
            await cursor.execute(
                "SELECT * FROM orders WHERE id = %s AND user_id = %s",
                (order_id, current_user.id)
            )
            order = await cursor.fetchone()
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Update status
            await cursor.execute(
                "UPDATE orders SET order_status = %s, updated_at = %s WHERE id = %s",
                (new_status, datetime.now(timezone.utc), order_id)
            )
            await conn.commit()
    
    return {"message": "Order status updated", "status": new_status}


# ============ RAZORPAY ROUTES ============

@api_router.post("/payment/create-order")
async def create_razorpay_order(
    data: RazorpayOrderRequest,
    current_user: User = Depends(get_current_user)
):
    return {
        "key_id": os.environ.get('RAZORPAY_KEY_ID'),
        "amount": int(data.amount * 100),  # paise
        "currency": "INR"
    }


@api_router.post("/payment/verify")
async def verify_payment(payment_data: dict, current_user: User = Depends(get_current_user)):
    # In production, verify signature here
    return {"status": "success"}

# ============ SEED DATA ============

@api_router.post("/seed")
async def seed_database():
    # Check if already seeded
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) as count FROM products")
            result = await cursor.fetchone()
            if result[0] > 1:
                return {"message": "Database already seeded"}
    
    # Seed products
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Exhaust System",
            "category": "Performance",
            "brand": "Akrapovic",
            "price": 25999,
            "original_price": 32999,
            "description": "Premium titanium exhaust system for enhanced performance and sound",
            "specifications": {"material": "Titanium", "weight": "2.5kg", "power_gain": "+5HP"},
            "image_url": "https://images.unsplash.com/photo-1620937843955-a177ceba979e?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 15,
            "compatibility": [
                {"brand": "KTM", "model": "Duke 390", "variant": "2024"},
                {"brand": "KTM", "model": "Duke 390", "variant": "2023"}
            ],
            "installation_difficulty": "Hard",
            "warranty": "2 Years",
            "rating": 4.8,
            "reviews_count": 124,
            "is_best_seller": True,
            "is_new_arrival": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Full Face Helmet",
            "category": "Safety Gear",
            "brand": "AGV",
            "price": 18999,
            "original_price": 24999,
            "description": "DOT certified full face helmet with aerodynamic design",
            "specifications": {"shell": "Carbon Fiber", "weight": "1.3kg", "certification": "DOT, ECE"},
            "image_url": "https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 30,
            "compatibility": [
                {"brand": "KTM", "model": "Duke 390", "variant": "2024"},
                {"brand": "BMW", "model": "G 310 R", "variant": "2024"},
                {"brand": "Royal Enfield", "model": "Classic 350", "variant": "2024"},
                {"brand": "Yamaha", "model": "MT-15", "variant": "2024"}
            ],
            "installation_difficulty": "Easy",
            "warranty": "1 Year",
            "rating": 4.7,
            "reviews_count": 89,
            "is_best_seller": True,
            "is_new_arrival": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Chain & Sprocket Kit",
            "category": "Pro Spares",
            "brand": "DID",
            "price": 4599,
            "original_price": 5999,
            "description": "Heavy duty chain and sprocket kit for long lasting performance",
            "specifications": {"chain_type": "O-Ring", "links": "120", "material": "Steel"},
            "image_url": "https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 45,
            "compatibility": [
                {"brand": "KTM", "model": "Duke 250", "variant": "2024"},
                {"brand": "KTM", "model": "Duke 250", "variant": "2023"},
                {"brand": "Yamaha", "model": "MT-15", "variant": "2024"}
            ],
            "installation_difficulty": "Medium",
            "warranty": "6 Months",
            "rating": 4.6,
            "reviews_count": 67,
            "is_best_seller": False,
            "is_new_arrival": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "LED Headlight Bulb",
            "category": "Accessories",
            "brand": "Philips",
            "price": 1299,
            "original_price": 1799,
            "description": "High intensity LED headlight bulb with white light",
            "specifications": {"brightness": "6000K", "power": "30W", "type": "H4"},
            "image_url": "https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 100,
            "compatibility": [
                {"brand": "KTM", "model": "Duke 390", "variant": "2024"},
                {"brand": "Royal Enfield", "model": "Classic 350", "variant": "2024"},
                {"brand": "Royal Enfield", "model": "Meteor 350", "variant": "2024"}
            ],
            "installation_difficulty": "Easy",
            "warranty": "1 Year",
            "rating": 4.5,
            "reviews_count": 156,
            "is_best_seller": False,
            "is_new_arrival": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Racing Brake Pads",
            "category": "Performance",
            "brand": "Brembo",
            "price": 3499,
            "original_price": 4299,
            "description": "High performance brake pads for superior stopping power",
            "specifications": {"material": "Ceramic", "type": "Front", "temperature_range": "0-800°C"},
            "image_url": "https://images.unsplash.com/photo-1761583780521-7723c3569361?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 60,
            "compatibility": [
                {"brand": "BMW", "model": "G 310 R", "variant": "2024"},
                {"brand": "BMW", "model": "G 310 GS", "variant": "2024"}
            ],
            "installation_difficulty": "Medium",
            "warranty": "1 Year",
            "rating": 4.9,
            "reviews_count": 203,
            "is_best_seller": True,
            "is_new_arrival": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Engine Oil Filter",
            "category": "Pro Spares",
            "brand": "K&N",
            "price": 599,
            "original_price": 799,
            "description": "High flow engine oil filter for better lubrication",
            "specifications": {"type": "Cartridge", "filtration": "99%", "capacity": "Standard"},
            "image_url": "https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 200,
            "compatibility": [
                {"brand": "Royal Enfield", "model": "Interceptor 650", "variant": "2024"},
                {"brand": "Royal Enfield", "model": "Himalayan", "variant": "2024"}
            ],
            "installation_difficulty": "Easy",
            "warranty": "3 Months",
            "rating": 4.4,
            "reviews_count": 78,
            "is_best_seller": False,
            "is_new_arrival": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bar End Mirrors",
            "category": "Accessories",
            "brand": "Rizoma",
            "price": 2999,
            "original_price": 3999,
            "description": "CNC machined aluminum bar end mirrors with wide angle view",
            "specifications": {"material": "Aluminum", "adjustable": "Yes", "color": "Black"},
            "image_url": "https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
            "stock": 35,
            "compatibility": [
                {"brand": "Yamaha", "model": "R15 V4", "variant": "2024"},
                {"brand": "KTM", "model": "RC 390", "variant": "2024"}
            ],
            "installation_difficulty": "Easy",
            "warranty": "2 Years",
            "rating": 4.6,
            "reviews_count": 42,
            "is_best_seller": False,
            "is_new_arrival": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Riding Jacket",
            "category": "Safety Gear",
            "brand": "Alpinestars",
            "price": 12999,
            "original_price": 16999,
            "description": "All-weather riding jacket with CE certified armor",
            "specifications": {"material": "Textile", "armor": "CE Level 2", "waterproof": "Yes"},
            "image_url": "https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85",
            "images": [],
                "stock": 25,
                "compatibility": [
                    {"brand": "KTM", "model": "Duke 390", "variant": "2024"},
                    {"brand": "BMW", "model": "G 310 R", "variant": "2024"},
                    {"brand": "Royal Enfield", "model": "Classic 350", "variant": "2024"},
                    {"brand": "Yamaha", "model": "MT-15", "variant": "2024"}
                ],
                "installation_difficulty": "Easy",
            "warranty": "1 Year",
            "rating": 4.8,
            "reviews_count": 112,
            "is_best_seller": True,
            "is_new_arrival": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            for product in products:
                await cursor.execute(
                    "INSERT INTO products (id, name, category, brand, price, original_price, description, specifications, image_url, images, stock, compatibility, installation_difficulty, warranty, rating, reviews_count, is_best_seller, is_new_arrival, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (product['id'], product['name'], product['category'], product['brand'], product['price'], product['original_price'], product['description'], json.dumps(product['specifications']), product['image_url'], json.dumps(product['images']), product['stock'], json.dumps(product['compatibility']), product['installation_difficulty'], product['warranty'], product['rating'], product['reviews_count'], product['is_best_seller'], product['is_new_arrival'], product['created_at'])
                )
            await conn.commit()
    
    return {"message": "Database seeded successfully", "products_count": len(products)}

# ============ APP STARTUP/SHUTDOWN ============

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    global db_pool
    db_pool.close()
    await db_pool.wait_closed()

# Include router AFTER all routes are defined
app.include_router(api_router)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
