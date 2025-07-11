# # infrastructure/database/session.py
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
# from core.config import settings
# from .base import Base

# # Configure database URL from settings
# DATABASE_URL = (
#     f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
#     f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
# )

# # Create async engine
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=settings.DB_ECHO,  # Log SQL queries in development
#     poolclass=NullPool,  # Disable connection pooling for async
#     future=True  # Enable SQLAlchemy 2.0 features
# )

# # Create session factory
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autoflush=False
# )

# from typing import AsyncGenerator

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     """Dependency that provides a database session"""
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()

# async def init_db():
#     """Initialize database tables"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# app/infrastructure/database/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# Import the Base from your ORM models
# Make sure all your ORM models inherit from this Base
from app.infrastructure.database.models.ims.medicine import Base as IMSBase
# If you have other domains, you would import their Bases too
# from app.infrastructure.database.models.hrm.employee import Base as HRMBase
# from app.infrastructure.database.models.warehouse.location import Base as WarehouseBase

# Configuration (ideally from app/core/config)
# For now, hardcode for demonstration
DATABASE_URL = "sqlite:///./ims_database.db" # SQLite for simplicity

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed for SQLite with FastAPI
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get a database session
def get_db() -> Generator:
    """
    Dependency to provide a database session.
    This will be used in FastAPI path operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables defined in the Base metadata
def create_all_tables():
    """
    Creates all database tables defined by the SQLAlchemy Base metadata.
    Call this function once when your application starts (e.g., in main.py)
    or during migrations.
    """
    print("Creating database tables...")
    IMSBase.metadata.create_all(bind=engine)
    # If you have other Bases, you'd create them here too
    # HRMBase.metadata.create_all(bind=engine)
    # WarehouseBase.metadata.create_all(bind=engine)
    print("Database tables created.")

# Example of how to use it (for initial setup or testing)
if __name__ == "__main__":
    create_all_tables()
    # You can add some initial data here if needed
    # with SessionLocal() as db:
    #     new_medicine = Medicine(name="Paracetamol", slug="paracetamol")
    #     db.add(new_medicine)
    #     db.commit()
    #     print(f"Added: {new_medicine}")
