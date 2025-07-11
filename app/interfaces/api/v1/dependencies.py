# api/dependencies.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_db
from domains.ims.medicine.repositories.medicine import MedicineRepository
from domains.ims.medicine.repositories.category import CategoryRepository
from domains.ims.medicine.services.medicine import MedicineService

def get_medicine_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return MedicineService(
        medicine_repo=MedicineRepository(db),
        category_repo=CategoryRepository(db)
    )

# Add other service providers...