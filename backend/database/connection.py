from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from database.config import DATABASE_URL

# ================= BASE =================

class Base(DeclarativeBase):
    pass

# ================= ENGINE =================

engine = create_engine(
    DATABASE_URL,
    pool_size=100,
    max_overflow=400,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)

# ================= SESSION =================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ================= DEPENDENCY =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
