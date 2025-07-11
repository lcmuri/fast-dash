# domains/medicine/repositories.py
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from infrastructure.database.models.ims.medicine import Medicine
from domains.ims.medicine import MedicineEntity

class MedicineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, medicine_data: dict) -> MedicineEntity:
        medicine = Medicine(**medicine_data)
        self.db.add(medicine)
        await self.db.commit()
        await self.db.refresh(medicine)
        return MedicineEntity.from_orm(medicine)
    
    async def get_by_id(self, medicine_id: UUID) -> Optional[MedicineEntity]:
        result = await self.db.execute(
            select(Medicine).where(Medicine.id == medicine_id)
        )
        medicine = result.scalars().first()
        return MedicineEntity.from_orm(medicine) if medicine else None
    
    # Implement other CRUD operations...