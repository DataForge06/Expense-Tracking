import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ CRITICAL ERROR: DATABASE_URL not found in .env")
else:
    # Ensure it uses asyncpg for async operations
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False, # Set to True if you want to see raw SQL queries in terminal
    pool_pre_ping=True
)

# Create Session Local for ACID transactions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # ATOMICITY: Saves only if no errors occurred
        except Exception:
            await session.rollback() # ROLLBACK: Reverts everything on error
            raise