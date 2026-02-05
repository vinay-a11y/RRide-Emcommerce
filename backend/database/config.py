import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# ================= MYSQL CONFIG =================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "143%40Vinay")
DB_NAME = os.getenv("DB_NAME", "bike_shop")
DB_PORT = int(os.getenv("DB_PORT", 3306))

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ================= JWT CONFIG =================

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
