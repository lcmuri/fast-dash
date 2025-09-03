from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from sqlalchemy_mptt import mptt_sessionmaker

# Import the Base from your ORM models
from app.infrastructure.database.models.ims.medicine import Base as IMSBase

# Configuration
DATABASE_URL = "sqlite:///./ims_database.db"  # SQLite for simplicity

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite with FastAPI
)

# # First create a standard sessionmaker
# standard_sessionmaker = sessionmaker(
#     # autocommit=False,
#     # autoflush=False,
#     bind=engine
# )

# # Then wrap it with mptt_sessionmaker
# SessionLocal = mptt_sessionmaker(sessionmaker=standard_sessionmaker)

# FROM CHATGPT WHEN I AM QUERING FOR CRUD CRM 03/09/2025 SEPTEMBER
# TAKE A LOOK
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.core.config.base import settings


# engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# Base = declarative_base()


# async def get_db():
# async with AsyncSessionLocal() as session:
# yield session

SessionLocal = mptt_sessionmaker(
    sessionmaker(bind=engine, autocommit=False, autoflush=False)
)

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

def drop_all_tables():
    IMSBase.metadata.drop_all(bind=engine)

# Function to create all tables defined in the Base metadata
def create_all_tables():
    """
    Creates all database tables defined by the SQLAlchemy Base metadata.
    """
    print("Creating database tables...")
    IMSBase.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    create_all_tables()