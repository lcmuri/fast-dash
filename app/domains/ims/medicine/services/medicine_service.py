# app/domains/ims/medicine/services/medicine_service.py

from typing import List, Optional
from slugify import slugify # Import the slugify function

from app.domains.ims.medicine.entities.medicine import (
    MedicineEntity,
    CategoryEntity,
    DoseFormEntity,
    StrengthEntity,
    ATCCodeEntity
)
from app.domains.ims.medicine.repositories.medicine_repository import IMedicineRepository

class MedicineService:
    """
    Domain Service for Medicine.
    Contains business logic related to medicines and their related entities.
    It orchestrates interactions with the repository.
    """
    def __init__(self, repository: IMedicineRepository):
        self._repository = repository

    # Medicine related methods
    async def get_medicine_details(self, medicine_id: int) -> Optional[MedicineEntity]:
        """
        Retrieves full details of a medicine, including its categories, strengths, and ATC codes.
        """
        medicine = await self._repository.get_medicine_by_id(medicine_id)
        if medicine:
            # In a real scenario, you might fetch related entities here
            # or the repository might return them pre-loaded.
            # For this example, assuming the repository returns a complete entity.
            pass # MedicineEntity already includes lists for relationships
        return medicine

    async def create_new_medicine(self, medicine_data: MedicineEntity) -> MedicineEntity:
        """
        Creates a new medicine and handles any associated logic (e.g., slug generation).
        """
        # Business logic: Generate slug if not provided or ensure it's valid
        if not medicine_data.slug:
            medicine_data.slug = slugify(medicine_data.name)
        # Ensure slug uniqueness (this check would ideally be in the repository or a dedicated domain validation)
        existing_medicine = await self._repository.get_medicine_by_slug(medicine_data.slug)
        if existing_medicine:
            raise ValueError(f"Medicine with slug '{medicine_data.slug}' already exists.")

        return await self._repository.create_medicine(medicine_data)

    async def update_medicine_details(self, medicine_id: int, medicine_data: MedicineEntity) -> Optional[MedicineEntity]:
        """
        Updates an existing medicine.
        """
        existing_medicine = await self._repository.get_medicine_by_id(medicine_id)
        if not existing_medicine:
            return None

        # Apply updates from medicine_data to existing_medicine
        # This is simplified; in a real app, you'd carefully merge fields
        existing_medicine.name = medicine_data.name
        existing_medicine.generic_name = medicine_data.generic_name
        existing_medicine.description = medicine_data.description
        existing_medicine.status = medicine_data.status
        # Note: slug might be updated or kept based on business rules
        # If the name changes and slug is not explicitly provided, regenerate
        if existing_medicine.name != medicine_data.name and not medicine_data.slug:
             existing_medicine.slug = slugify(medicine_data.name)
        elif medicine_data.slug: # If a new slug is provided, use it
            existing_medicine.slug = medicine_data.slug

        # Ensure updated slug uniqueness
        if existing_medicine.slug:
            check_existing = await self._repository.get_medicine_by_slug(existing_medicine.slug)
            if check_existing and check_existing.id != medicine_id:
                raise ValueError(f"Medicine with slug '{existing_medicine.slug}' already exists.")


        return await self._repository.update_medicine(medicine_id, existing_medicine)

    async def delete_medicine_record(self, medicine_id: int) -> bool:
        """
        Deletes a medicine record.
        """
        return await self._repository.delete_medicine(medicine_id)

    async def list_all_medicines(self, skip: int = 0, limit: int = 100) -> List[MedicineEntity]:
        """
        Lists all medicines with pagination.
        """
        return await self._repository.get_all_medicines(skip, limit)

    async def add_categories_to_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        """
        Adds categories to a medicine, ensuring categories exist.
        """
        # Business logic: Verify category_ids exist before adding
        for cat_id in category_ids:
            if not await self._repository.get_category_by_id(cat_id):
                raise ValueError(f"Category with ID {cat_id} not found.")
        await self._repository.add_categories_to_medicine(medicine_id, category_ids)

    async def remove_categories_from_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        """
        Removes categories from a medicine.
        """
        await self._repository.remove_categories_from_medicine(medicine_id, category_ids)

    # Category related methods
    async def create_new_category(self, category_data: CategoryEntity, parent_id: Optional[int] = None) -> CategoryEntity:
        """
        Creates a new category, optionally as a child of another.
        """
        if not category_data.slug:
            category_data.slug = slugify(category_data.name)
        
        # Ensure slug uniqueness for categories
        existing_category = await self._repository.get_category_by_slug(category_data.slug)
        if existing_category:
            raise ValueError(f"Category with slug '{category_data.slug}' already exists.")

        return await self._repository.create_category(category_data, parent_id)

    async def get_category_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        """
        Retrieves a single category by its ID.
        """
        return await self._repository.get_category_by_id(category_id)

    async def update_category_details(self, category_id: int, category_data: CategoryEntity) -> Optional[CategoryEntity]:
        """
        Updates an existing category.
        """
        existing_category = await self._repository.get_category_by_id(category_id)
        if not existing_category:
            return None

        # Apply updates
        existing_category.name = category_data.name
        existing_category.description = category_data.description
        existing_category.status = category_data.status
        if category_data.slug: # Only update slug if explicitly provided
            existing_category.slug = category_data.slug
        else: # If name changed and slug not provided, regenerate
            existing_category.slug = slugify(category_data.name)

        # Ensure updated slug uniqueness (excluding itself)
        if existing_category.slug:
            check_existing = await self._repository.get_category_by_slug(existing_category.slug)
            if check_existing and check_existing.id != category_id:
                raise ValueError(f"Category with slug '{existing_category.slug}' already exists.")

        return await self._repository.update_category(category_id, existing_category)

    async def delete_category_record(self, category_id: int) -> bool:
        """
        Deletes a category record.
        """
        return await self._repository.delete_category(category_id)


    async def list_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryEntity]:
        """
        Lists all categories with pagination (flat list).
        """
        return await self._repository.get_all_categories(skip, limit)

    async def get_category_tree(self) -> List[CategoryEntity]:
        """
        Retrieves all categories in a hierarchical tree structure.
        """
        return await self._repository.get_category_tree()

    # DoseForm related methods
    async def create_new_dose_form(self, dose_form_data: DoseFormEntity) -> DoseFormEntity:
        """
        Creates a new dose form.
        """
        return await self._repository.create_dose_form(dose_form_data)

    async def list_all_dose_forms(self, skip: int = 0, limit: int = 100) -> List[DoseFormEntity]:
        """
        Lists all dose forms.
        """
        return await self._repository.get_all_dose_forms(skip, limit)
 
#  Strength related methods
    async def create_new_strength(self, strength_data: StrengthEntity) -> StrengthEntity:
        """
        Creates a new strength for a medicine.
        Business logic: Ensure medicine_id and dose_form_id exist.
        """
        if not await self._repository.get_medicine_by_id(strength_data.medicine_id):
            raise ValueError(f"Medicine with ID {strength_data.medicine_id} not found.")
        if not await self._repository.get_dose_form_by_id(strength_data.dose_form_id):
            raise ValueError(f"Dose Form with ID {strength_data.dose_form_id} not found.")
        return await self._repository.create_strength(strength_data)

    async def list_strengths_for_medicine(self, medicine_id: int) -> List[StrengthEntity]:
        """
        Lists strengths for a specific medicine.
        """
        return await self._repository.get_strengths_for_medicine(medicine_id)

# ATC Code related methods
    async def create_new_atc_code(self, atc_code_data: ATCCodeEntity) -> ATCCodeEntity:
        """
        Creates a new ATC code.
        Business logic: Ensure code and slug are unique.
        """
        if await self._repository.get_atc_code_by_code(atc_code_data.code):
            raise ValueError(f"ATC Code '{atc_code_data.code}' already exists.")
        if not atc_code_data.slug: # Generate slug for ATC code if not provided
            atc_code_data.slug = slugify(atc_code_data.name)
        # Additional slug uniqueness check if slug is also unique and not derived directly from code
        return await self._repository.create_atc_code(atc_code_data)

    async def list_all_atc_codes(self, skip: int = 0, limit: int = 100) -> List[ATCCodeEntity]:
        """
        Lists all ATC codes.
        """
        return await self._repository.get_all_atc_codes(skip, limit)

    async def add_atc_codes_to_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        """
        Adds ATC codes to a medicine, ensuring ATC codes exist.
        """
        for atc_id in atc_code_ids:
            if not await self._repository.get_atc_code_by_id(atc_id):
                raise ValueError(f"ATC Code with ID {atc_id} not found.")
        await self._repository.add_atc_codes_to_medicine(medicine_id, atc_code_ids)

    async def remove_atc_codes_from_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        """
        Removes ATC codes from a medicine.
        """
        await self._repository.remove_atc_codes_from_medicine(medicine_id, atc_code_ids)
