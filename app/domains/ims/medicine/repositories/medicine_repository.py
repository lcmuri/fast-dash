# app/domains/ims/medicine/repositories/medicine_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.ims.medicine.entities.medicine import (
    MedicineEntity,
    CategoryEntity,
    DoseFormEntity,
    StrengthEntity,
    ATCCodeEntity
)

class IMedicineRepository(ABC):
    """
    Abstract Base Class for Medicine Repository.
    Defines the contract for interacting with medicine data storage.
    """

    @abstractmethod
    async def get_medicine_by_id(self, medicine_id: int) -> Optional[MedicineEntity]:
        """Retrieves a medicine by its ID."""
        pass

    @abstractmethod
    async def get_medicine_by_slug(self, slug: str) -> Optional[MedicineEntity]:
        """Retrieves a medicine by its slug."""
        pass

    @abstractmethod
    async def get_all_medicines(self, skip: int = 0, limit: int = 100) -> List[MedicineEntity]:
        """Retrieves all medicines with pagination."""
        pass

    @abstractmethod
    async def create_medicine(self, medicine: MedicineEntity) -> MedicineEntity:
        """Creates a new medicine record."""
        pass

    @abstractmethod
    async def update_medicine(self, medicine_id: int, medicine: MedicineEntity) -> Optional[MedicineEntity]:
        """Updates an existing medicine record."""
        pass

    @abstractmethod
    async def delete_medicine(self, medicine_id: int) -> bool:
        """Deletes a medicine record by its ID."""
        pass

    @abstractmethod
    async def add_categories_to_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        """Adds categories to a medicine."""
        pass

    @abstractmethod
    async def remove_categories_from_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        """Removes categories from a medicine."""
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        """Retrieves a category by its ID."""
        pass

    @abstractmethod
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryEntity]:
        """Retrieves a category by its slug."""
        pass

    @abstractmethod
    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryEntity]:
        """Retrieves all categories with pagination."""
        pass

    @abstractmethod
    async def create_category(self, category: CategoryEntity) -> CategoryEntity:
        """Creates a new category record."""
        pass

    @abstractmethod
    async def get_dose_form_by_id(self, dose_form_id: int) -> Optional[DoseFormEntity]:
        """Retrieves a dose form by its ID."""
        pass

    @abstractmethod
    async def get_all_dose_forms(self, skip: int = 0, limit: int = 100) -> List[DoseFormEntity]:
        """Retrieves all dose forms with pagination."""
        pass

    @abstractmethod
    async def create_dose_form(self, dose_form: DoseFormEntity) -> DoseFormEntity:
        """Creates a new dose form record."""
        pass

    @abstractmethod
    async def get_strength_by_id(self, strength_id: int) -> Optional[StrengthEntity]:
        """Retrieves a strength by its ID."""
        pass

    @abstractmethod
    async def get_strengths_for_medicine(self, medicine_id: int) -> List[StrengthEntity]:
        """Retrieves all strengths for a specific medicine."""
        pass

    @abstractmethod
    async def create_strength(self, strength: StrengthEntity) -> StrengthEntity:
        """Creates a new strength record."""
        pass

    @abstractmethod
    async def get_atc_code_by_id(self, atc_code_id: int) -> Optional[ATCCodeEntity]:
        """Retrieves an ATC code by its ID."""
        pass

    @abstractmethod
    async def get_atc_code_by_code(self, code: str) -> Optional[ATCCodeEntity]:
        """Retrieves an ATC code by its unique code string."""
        pass

    @abstractmethod
    async def get_atc_code_by_slug(self, slug: str) -> Optional[ATCCodeEntity]:
        """Retrieves an ATC code by its slug."""
        pass

    @abstractmethod
    async def get_all_atc_codes(self, skip: int = 0, limit: int = 100) -> List[ATCCodeEntity]:
        """Retrieves all ATC codes with pagination."""
        pass

    @abstractmethod
    async def create_atc_code(self, atc_code: ATCCodeEntity) -> ATCCodeEntity:
        """Creates a new ATC code record."""
        pass

    @abstractmethod
    async def add_atc_codes_to_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        """Adds ATC codes to a medicine."""
        pass

    @abstractmethod
    async def remove_atc_codes_from_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        """Removes ATC codes from a medicine."""
        pass