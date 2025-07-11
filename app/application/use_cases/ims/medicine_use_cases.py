# app/application/use_cases/ims/medicine_use_cases.py

from typing import List, Optional
from fastapi import HTTPException, status

from app.domains.ims.medicine.entities.medicine import (
    MedicineEntity,
    CategoryEntity,
    DoseFormEntity,
    StrengthEntity,
    ATCCodeEntity
)
from app.domains.ims.medicine.services.medicine_service import MedicineService
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

class MedicineUseCases:
    """
    Application-level use cases for Medicine.
    Orchestrates interactions between schemas, domain services, and repositories.
    Handles application-specific logic, error mapping, and data transformation.
    """
    def __init__(self, medicine_service: MedicineService):
        self._medicine_service = medicine_service

    # --- Medicine Use Cases ---
    async def create_medicine(self, medicine_create: MedicineCreate) -> MedicineResponse:
        """
        Creates a new medicine, handles category and ATC code associations.
        """
        # Convert schema to domain entity
        medicine_entity = MedicineEntity(
            name=medicine_create.name,
            slug=medicine_create.slug,
            generic_name=medicine_create.generic_name,
            status=medicine_create.status,
            description=medicine_create.description
        )

        try:
            created_medicine_entity = await self._medicine_service.create_new_medicine(medicine_entity)
            if medicine_create.category_ids:
                await self._medicine_service.add_categories_to_medicine(
                    created_medicine_entity.id, medicine_create.category_ids
                )
            if medicine_create.atc_code_ids:
                await self._medicine_service.add_atc_codes_to_medicine(
                    created_medicine_entity.id, medicine_create.atc_code_ids
                )

            # Re-fetch the complete entity to include relationships for the response
            full_medicine_entity = await self._medicine_service.get_medicine_details(created_medicine_entity.id)
            return MedicineResponse.model_validate(full_medicine_entity) # Pydantic v2+

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create medicine: {e}")


    async def get_medicine_by_id(self, medicine_id: int) -> MedicineResponse:
        """
        Retrieves a medicine by ID.
        """
        medicine_entity = await self._medicine_service.get_medicine_details(medicine_id)
        if not medicine_entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
        return MedicineResponse.model_validate(medicine_entity)

    async def list_medicines(self, skip: int = 0, limit: int = 100) -> List[MedicineResponse]:
        """
        Lists all medicines with pagination.
        """
        medicine_entities = await self._medicine_service.list_all_medicines(skip, limit)
        return [MedicineResponse.model_validate(entity) for entity in medicine_entities]

    async def update_medicine(self, medicine_id: int, medicine_update: MedicineUpdate) -> MedicineResponse:
        """
        Updates an existing medicine and handles relationship updates.
        """
        existing_medicine_entity = await self._medicine_service.get_medicine_details(medicine_id)
        if not existing_medicine_entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")

        # Apply updates from schema to entity, only if present in the update payload
        update_data = medicine_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            # Exclude relationship lists from direct attribute setting, as they are handled separately
            if hasattr(existing_medicine_entity, key) and key not in ["add_category_ids", "remove_category_ids", "add_atc_code_ids", "remove_atc_code_ids"]:
                setattr(existing_medicine_entity, key, value)

        try:
            updated_medicine_entity = await self._medicine_service.update_medicine_details(medicine_id, existing_medicine_entity)

            # Handle category relationship updates
            if medicine_update.add_category_ids:
                await self._medicine_service.add_categories_to_medicine(medicine_id, medicine_update.add_category_ids)
            if medicine_update.remove_category_ids:
                await self._medicine_service.remove_categories_from_medicine(medicine_id, medicine_update.remove_category_ids)

            # Handle ATC code relationship updates
            if medicine_update.add_atc_code_ids:
                await self._medicine_service.add_atc_codes_to_medicine(medicine_id, medicine_update.add_atc_code_ids)
            if medicine_update.remove_atc_code_ids:
                await self._medicine_service.remove_atc_codes_from_medicine(medicine_id, medicine_update.remove_atc_code_ids)

            # Re-fetch the complete entity to ensure all relationships are updated in response
            full_updated_medicine_entity = await self._medicine_service.get_medicine_details(medicine_id)
            return MedicineResponse.model_validate(full_updated_medicine_entity)

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update medicine: {e}")


    async def delete_medicine(self, medicine_id: int) -> bool:
        """
        Deletes a medicine.
        """
        success = await self._medicine_service.delete_medicine_record(medicine_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
        return True

    # --- Category Use Cases ---
    async def create_category(self, category_create: CategoryCreate) -> CategoryResponse:
        category_entity = CategoryEntity(
            name=category_create.name,
            slug=category_create.slug,
            description=category_create.description,
            status=category_create.status,
            # parent_id is handled by the service layer for MPTT insertion
        )
        try:
            created_category = await self._medicine_service.create_new_category(category_entity, category_create.parent_id)
            return CategoryResponse.model_validate(created_category)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_category_by_id(self, category_id: int) -> CategoryResponse:
        category_entity = await self._medicine_service.get_category_by_id(category_id)
        if not category_entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategoryResponse.model_validate(category_entity)

    async def update_category(self, category_id: int, category_update: CategoryUpdate) -> CategoryResponse:
        existing_category_entity = await self._medicine_service.get_category_by_id(category_id)
        if not existing_category_entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Apply updates from schema to entity
        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(existing_category_entity, key):
                setattr(existing_category_entity, key, value)
        
        try:
            updated_category = await self._medicine_service.update_category_details(category_id, existing_category_entity)
            return CategoryResponse.model_validate(updated_category)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update category: {e}")

    async def delete_category(self, category_id: int) -> bool:
        success = await self._medicine_service.delete_category_record(category_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or could not be deleted.")
        return True

    async def list_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryResponse]:
        category_entities = await self._medicine_service.list_all_categories(skip, limit)
        return [CategoryResponse.model_validate(entity) for entity in category_entities]

    async def get_category_tree(self) -> List[CategoryResponse]:
        """
        Retrieves all categories in a hierarchical tree structure.
        """
        category_entities_tree = await self._medicine_service.get_category_tree()
        # Recursively convert entities to response schemas
        def convert_entity_to_response(entity: CategoryEntity) -> CategoryResponse:
            response = CategoryResponse.model_validate(entity)
            response.children = [convert_entity_to_response(child) for child in entity.children]
            return response

        return [convert_entity_to_response(root) for root in category_entities_tree]

    # --- DoseForm Use Cases ---
    async def create_dose_form(self, dose_form_create: DoseFormCreate) -> DoseFormResponse:
        dose_form_entity = DoseFormEntity(
            name=dose_form_create.name,
            description=dose_form_create.description
        )
        try:
            created_dose_form = await self._medicine_service.create_new_dose_form(dose_form_entity)
            return DoseFormResponse.model_validate(created_dose_form)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def list_dose_forms(self, skip: int = 0, limit: int = 100) -> List[DoseFormResponse]:
        dose_form_entities = await self._medicine_service.list_all_dose_forms(skip, limit)
        return [DoseFormResponse.model_validate(entity) for entity in dose_form_entities]

    # --- Strength Use Cases ---
    async def create_strength(self, strength_create: StrengthCreate) -> StrengthResponse:
        strength_entity = StrengthEntity(
            medicine_id=strength_create.medicine_id,
            dose_form_id=strength_create.dose_form_id,
            concentration_amount=strength_create.concentration_amount,
            concentration_unit=strength_create.concentration_unit,
            volume_amount=strength_create.volume_amount,
            volume_unit=strength_create.volume_unit,
            chemical_form=strength_create.chemical_form,
            info=strength_create.info,
            description=strength_create.description
        )
        try:
            created_strength = await self._medicine_service.create_new_strength(strength_entity)
            return StrengthResponse.model_validate(created_strength)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def list_strengths_for_medicine(self, medicine_id: int) -> List[StrengthResponse]:
        strength_entities = await self._medicine_service.list_strengths_for_medicine(medicine_id)
        return [StrengthResponse.model_validate(entity) for entity in strength_entities]

    # --- ATC Code Use Cases ---
    async def create_atc_code(self, atc_code_create: ATCCodeCreate) -> ATCCodeResponse:
        atc_code_entity = ATCCodeEntity(
            parent_id=atc_code_create.parent_id,
            name=atc_code_create.name,
            code=atc_code_create.code,
            level=atc_code_create.level,
            slug=atc_code_create.slug,
            status=atc_code_create.status,
            description=atc_code_create.description,
            created_by=atc_code_create.created_by,
            updated_by=atc_code_create.updated_by,
            deleted_by=atc_code_create.deleted_by
        )
        try:
            created_atc_code = await self._medicine_service.create_new_atc_code(atc_code_entity)
            return ATCCodeResponse.model_validate(created_atc_code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def list_atc_codes(self, skip: int = 0, limit: int = 100) -> List[ATCCodeResponse]:
        atc_code_entities = await self._medicine_service.list_all_atc_codes(skip, limit)
        return [ATCCodeResponse.model_validate(entity) for entity in atc_code_entities]
