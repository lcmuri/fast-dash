# app/infrastructure/database/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
# Import mptt_sessionmaker
from sqlalchemy_mptt import mptt_sessionmaker

# Import the Base from your ORM models
from app.infrastructure.database.models.ims.medicine import Base as IMSBase

# Configuration (ideally from app/core/config)
DATABASE_URL = "sqlite:///./ims_database.db" # SQLite for simplicity

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed for SQLite with FastAPI
)

# Create a configured "Session" class using mptt_sessionmaker
SessionLocal = mptt_sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    print("Database tables created.")

# Example of how to use it (for initial setup or testing)
if __name__ == "__main__":
    create_all_tables()
