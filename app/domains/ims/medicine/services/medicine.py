# application/services/medicine.py
from uuid import UUID
from typing import List, Optional
from domains.ims.medicine.entities.medicine import MedicineEntity as Medicine
from domains.ims.medicine.repositories.medicine import MedicineRepository
from domains.ims.medicine.repositories.category import CategoryRepository
from core.exceptions import NotFoundException, ValidationException

class MedicineService:
    def __init__(
        self,
        medicine_repo: MedicineRepository,
        category_repo: CategoryRepository
    ):
        self.medicine_repo = medicine_repo
        self.category_repo = category_repo

    async def create_medicine(self, medicine_data: dict) -> Medicine:
        # Validate categories exist
        if medicine_data.get('category_ids'):
            existing = await self.category_repo.get_by_ids(medicine_data['category_ids'])
            if len(existing) != len(medicine_data['category_ids']):
                raise ValidationException("One or more categories not found")
        
        return await self.medicine_repo.create(medicine_data)

    async def get_medicine(self, medicine_id: UUID) -> Medicine:
        medicine = await self.medicine_repo.get_by_id(medicine_id)
        if not medicine:
            raise NotFoundException(entity_name="Medicine", entity_id=medicine_id)
        return medicine

    # Implement update, delete, list methods...