# api/v1/endpoints/medicine.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_db
from application.schemas.ims import MedicineCreate, MedicineResponse
from domains.ims.medicine.entities.medicine import MedicineEntity as Medicine
from domains.ims.medicine.services.medicine import MedicineService, get_medicine_service
from domains.ims.medicine import MedicineRepository

router = APIRouter(prefix="/medicines", tags=["medicines"])

@router.post("/", response_model=MedicineResponse)
async def create_medicine(
    medicine_data: MedicineCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = MedicineRepository(db)
    try:
        medicine = await repo.create(medicine_data.dict())
        return MedicineResponse.from_orm(medicine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Medicine)
async def get_medicine(
    id: UUID,
    service: MedicineService = Depends(get_medicine_service)
):
    medicine = await service.get_by_id(id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return medicine

# Similar endpoints for categories, ATC codes, and dose forms
@router.post("/{medicine_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_medicine_category(
    medicine_id: UUID,
    category_id: UUID,
    service: MedicineService = Depends(get_medicine_service)
):
    success = await service.add_category(medicine_id, category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine or category not found")

@router.delete("/{medicine_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_medicine_category(
    medicine_id: UUID,
    category_id: UUID,
    service: MedicineService = Depends(get_medicine_service)
):
    success = await service.remove_category(medicine_id, category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")