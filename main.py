# main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.database.session import create_all_tables
from app.interfaces.api.v1.routers.ims.medicine_router import router as medicine_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing database...")
    create_all_tables()
    print("Database initialization complete.")
    yield
    # Optionally, add shutdown logic here


# Initialize the FastAPI application
app = FastAPI(
    title="IMS API",
    description="Inventory Management System API built with FastAPI and SQLAlchemy.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",  # Your React app's origin
    "http://localhost",
    "http://127.0.0.1:5173",  # Another common local development address
    # Add any other origins where your frontend might be hosted (e.g., your production domain)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers for different domains/features
app.include_router(medicine_router)
# You would include other routers here for HRM, Warehouse, etc.
# app.include_router(hrm_router)
# app.include_router(warehouse_router)

# Event handler for application startup
# @app.on_event("startup")
# async def startup_event():
#     """
#     Event handler that runs when the application starts up.
#     Used to create database tables if they don't exist.
#     In a production environment, you would typically use Alembic for migrations.
#     """
#     print("Application startup: Initializing database...")
#     create_all_tables()
#     print("Database initialization complete.")

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the IMS API!"}

# To run this application:
# 1. Ensure you have all the files created as per the structure.
# 2. Install necessary packages:
#    pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
# 3. Run from your terminal in the parent directory of 'app':
#    uvicorn main:app --reload
# 4. Open your browser to `http://127.0.0.1:8000/docs` to see the interactive API documentation.
