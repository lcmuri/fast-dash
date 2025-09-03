# interfaces/api/v1/routers/crm/customer_router.py
from fastapi import APIRouter, Depends, HTTPException
from application.schemas.crm.customer_schemas import (
    CustomerCreate, CustomerResponse, CustomerUpdate
)
from application.use_cases.crm.customer_use_cases import CustomerUseCases
from infrastructure.database.session import get_db

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    use_cases: CustomerUseCases = Depends(),
    db = Depends(get_db)
):
    """Create a new customer"""
    return await use_cases.create_customer(customer_data)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    use_cases: CustomerUseCases = Depends(),
    db = Depends(get_db)
):
    """Get customer by ID"""
    customer = await use_cases.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/phone/{phone}", response_model=CustomerResponse)
async def get_customer_by_phone(
    phone: str,
    use_cases: CustomerUseCases = Depends(),
    db = Depends(get_db)
):
    """Get customer by phone number"""
    customer = await use_cases.get_customer_by_phone(phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/{customer_id}/visit")
async def record_customer_visit(
    customer_id: int,
    visit_data: dict,
    use_cases: CustomerUseCases = Depends(),
    db = Depends(get_db)
):
    """Record a customer visit (walk-in or telesales)"""
    return await use_cases.record_visit(customer_id, visit_data)