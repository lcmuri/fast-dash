# app/interfaces/api/v1/routers/ims/medicine_router.py

from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session

# Import Pydantic schemas for request/response bodies
from app.application.schemas.ims.medicine_schemas import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    CategoryCreate,
    CategoryUpdate, # Added for update
    CategoryResponse,
    DoseFormCreate,
    DoseFormResponse,
    StrengthCreate,
    StrengthResponse,
    ATCCodeCreate,
    ATCCodeResponse
)
# Import the Use Case layer
from app.application.use_cases.ims.medicine_use_cases import MedicineUseCases
# Import the Domain Service layer
from app.domains.ims.medicine.services.medicine_service import MedicineService
# Import the Infrastructure Repository implementation
from app.infrastructure.repositories.ims.medicine_sqlalchemy_repository import MedicineSQLAlchemyRepository
# Import the database session dependency
from app.infrastructure.database.session import get_db

# Create an API router for IMS Medicine
router = APIRouter(
    prefix="/medicines",
    tags=["IMS - Medicines"]
)

# Dependency to get MedicineUseCases instance
# This function sets up the dependency chain:
# get_db -> MedicineSQLAlchemyRepository -> MedicineService -> MedicineUseCases
def get_medicine_use_cases(db: Session = Depends(get_db)) -> MedicineUseCases:
    """
    Provides a MedicineUseCases instance with a SQLAlchemy repository.
    This function acts as a FastAPI dependency injector.
    """
    repository = MedicineSQLAlchemyRepository(db)
    service = MedicineService(repository)
    return MedicineUseCases(service)

# --- Medicine Endpoints ---
@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine_create: MedicineCreate, # Pydantic schema for input validation
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases) # Dependency injection
):
    """
    Create a new medicine record.
    Allows associating categories and ATC codes during creation.
    """
    return await use_cases.create_medicine(medicine_create)

@router.get("/", response_model=List[MedicineResponse])
async def list_medicines(
    skip: int = 0,
    limit: int = 100,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve a list of all medicines with pagination.
    """
    return await use_cases.list_medicines(skip, limit)

@router.get("/{medicine_id}", response_model=MedicineResponse)
async def get_medicine_by_id(
    medicine_id: int,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve a single medicine by its ID.
    """
    return await use_cases.get_medicine_by_id(medicine_id)

@router.put("/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: int,
    medicine_update: MedicineUpdate, # Pydantic schema for partial updates
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Update an existing medicine record.
    Supports partial updates and adding/removing categories/ATC codes.
    """
    return await use_cases.update_medicine(medicine_id, medicine_update)

@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
    medicine_id: int,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Delete a medicine record by its ID.
    """
    await use_cases.delete_medicine(medicine_id)
    # FastAPI automatically handles 204 No Content for successful deletion
    return {"message": "Medicine deleted successfully"}

# --- Category Endpoints ---
@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, tags=["IMS - Categories"])
async def create_category(
    category_create: CategoryCreate,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Create a new category.
    Optionally specify `parent_id` to create a nested category.
    """
    return await use_cases.create_category(category_create)

@router.get("/categories/", response_model=List[CategoryResponse], tags=["IMS - Categories"])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve a list of all categories with pagination (flat list).
    """
    return await use_cases.list_categories(skip, limit)

@router.get("/categories/tree", response_model=List[CategoryResponse], tags=["IMS - Categories"])
async def get_category_tree(
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve all categories in a hierarchical tree structure.
    """
    return await use_cases.get_category_tree()

@router.get("/categories/{category_id}", response_model=CategoryResponse, tags=["IMS - Categories"])
async def get_category_by_id(
    category_id: int,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases),
    include_children: bool = True # Optional query parameter to include children
):
    """
    Retrieve a single category by its ID.
    """
    return await use_cases.get_category_by_id(category_id, include_children)

@router.put("/categories/{category_id}", response_model=CategoryResponse, tags=["IMS - Categories"])
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Update an existing category record.
    """
    return await use_cases.update_category(category_id, category_update)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["IMS - Categories"])
async def delete_category(
    category_id: int,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Delete a category record by its ID.
    Note: Deleting a parent category will also delete its descendants by default with MPTT.
    """
    await use_cases.delete_category(category_id)
    return {"message": "Category deleted successfully"}

# --- DoseForm Endpoints ---
@router.post("/dose-forms/", response_model=DoseFormResponse, status_code=status.HTTP_201_CREATED, tags=["IMS - Dose Forms"])
async def create_dose_form(
    dose_form_create: DoseFormCreate,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Create a new dose form.
    """
    return await use_cases.create_dose_form(dose_form_create)

@router.get("/dose-forms/", response_model=List[DoseFormResponse], tags=["IMS - Dose Forms"])
async def list_dose_forms(
    skip: int = 0,
    limit: int = 100,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve a list of all dose forms with pagination.
    """
    return await use_cases.list_dose_forms(skip, limit)

# --- Strength Endpoints ---
@router.post("/strengths/", response_model=StrengthResponse, status_code=status.HTTP_201_CREATED, tags=["IMS - Strengths"])
async def create_strength(
    strength_create: StrengthCreate,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Create a new strength for a medicine.
    """
    return await use_cases.create_strength(strength_create)

@router.get("/medicines/{medicine_id}/strengths/", response_model=List[StrengthResponse], tags=["IMS - Strengths"])
async def list_strengths_for_medicine(
    medicine_id: int,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve all strengths associated with a specific medicine.
    """
    return await use_cases.list_strengths_for_medicine(medicine_id)

# --- ATC Code Endpoints ---
@router.post("/atc-codes/", response_model=ATCCodeResponse, status_code=status.HTTP_201_CREATED, tags=["IMS - ATC Codes"])
async def create_atc_code(
    atc_code_create: ATCCodeCreate,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Create a new ATC code.
    """
    return await use_cases.create_atc_code(atc_code_create)

@router.get("/atc-codes/", response_model=List[ATCCodeResponse], tags=["IMS - ATC Codes"])
async def list_atc_codes(
    skip: int = 0,
    limit: int = 100,
    use_cases: MedicineUseCases = Depends(get_medicine_use_cases)
):
    """
    Retrieve a list of all ATC codes with pagination.
    """
    return await use_cases.list_atc_codes(skip, limit)
