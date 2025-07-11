# app/application/schemas/ims/medicine_schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Enums (can be reused from core/enums or defined here if specific to schemas)
class ActiveStatusSchema:
    ACTIVE = "active"
    INACTIVE = "inactive"

class ATCCodeBase(BaseModel):
    name: str
    code: str = Field(..., description="e.g., 'A02BC02'")
    level: int = Field(..., ge=1, le=5, description="1 (Anatomical) to 5 (Chemical)")
    slug: str
    status: str = ActiveStatusSchema.ACTIVE
    description: Optional[str] = None

class ATCCodeCreate(ATCCodeBase):
    parent_id: Optional[int] = None
    created_by: Optional[str] = None # For tracking who created
    updated_by: Optional[str] = None # For tracking who updated
    deleted_by: Optional[str] = None # For tracking who deleted

class ATCCodeResponse(ATCCodeBase):
    id: int
    parent_id: Optional[int] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    status: str = ActiveStatusSchema.ACTIVE

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DoseFormBase(BaseModel):
    name: str
    description: Optional[str] = None

class DoseFormCreate(DoseFormBase):
    pass

class DoseFormResponse(DoseFormBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StrengthBase(BaseModel):
    concentration_amount: float = Field(..., gt=0, description="e.g., 1 (for 1mg)")
    concentration_unit: str = Field(..., description="e.g., 'mg'")
    volume_amount: Optional[float] = Field(None, gt=0, description="e.g., 1 (for 1ml)")
    volume_unit: Optional[str] = Field(None, description="e.g., 'ml'")
    chemical_form: Optional[str] = Field(None, description="e.g., 'sulphate'")
    info: Optional[str] = None
    description: Optional[str] = None

class StrengthCreate(StrengthBase):
    medicine_id: int
    dose_form_id: int

class StrengthResponse(StrengthBase):
    id: int
    medicine_id: int
    dose_form_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MedicineBase(BaseModel):
    name: str
    slug: str
    generic_name: Optional[str] = None
    status: str = ActiveStatusSchema.ACTIVE
    description: Optional[str] = None

class MedicineCreate(MedicineBase):
    # For creation, you might receive lists of IDs for relationships
    category_ids: List[int] = Field(default_factory=list, description="List of category IDs to associate with the medicine.")
    atc_code_ids: List[int] = Field(default_factory=list, description="List of ATC code IDs to associate with the medicine.")

class MedicineUpdate(BaseModel):
    # For updates, all fields are optional
    name: Optional[str] = None
    slug: Optional[str] = None
    generic_name: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    # For updating relationships, you might have separate endpoints or specific update models
    add_category_ids: Optional[List[int]] = None
    remove_category_ids: Optional[List[int]] = None
    add_atc_code_ids: Optional[List[int]] = None
    remove_atc_code_ids: Optional[List[int]] = None


class MedicineResponse(MedicineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Nested schemas for related data in responses
    categories: List[CategoryResponse] = Field(default_factory=list)
    strengths: List[StrengthResponse] = Field(default_factory=list)
    atc_codes: List[ATCCodeResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

# Schemas for associating relationships
class MedicineCategoryAssociation(BaseModel):
    medicine_id: int
    category_id: int

class MedicineATCCodeAssociation(BaseModel):
    medicine_id: int
    atc_code_id: int
