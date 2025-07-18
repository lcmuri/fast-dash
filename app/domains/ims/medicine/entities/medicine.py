# app/domains/ims/medicine/entities/medicine.py

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

# Enums (if applicable, could be defined in a central core/enums or here)
class ActiveStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"

@dataclass
class ATCCodeEntity:
    """
    Domain entity for ATC Codes.
    Represents the core concept of an ATC code, independent of persistence.
    """
    
    name: str
    code: str
    level: int
    slug: str
    status: str = ActiveStatus.ACTIVE
    id: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 

@dataclass
class CategoryEntity:
    """
    Domain entity for Categories.
    Includes MPTT-related fields for hierarchical representation.
    """
    name: str
    id: Optional[int] = None
    parent_id: Optional[int] = None    
    slug: Optional[str] = None
    description: Optional[str] = None
    status: str = ActiveStatus.ACTIVE    
    level: Optional[int] = None # Added for MPTT level
    # lft: Optional[int] = None # MPTT left value (can be included if domain needs it)
    # rgt: Optional[int] = None # MPTT right value (can be included if domain needs it)
    children: List["CategoryEntity"] = field(default_factory=list) # For hierarchical representation
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class DoseFormEntity:
    """
    Domain entity for Dose Forms.
    """
    name: str
    id: Optional[int] = None   
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class StrengthEntity:
    """
    Domain entity for Strengths.
    Note: This entity includes medicine_id and dose_form_id for conceptual linkage,
    but in a pure domain model, these might be represented by direct object references
    if the domain logic requires it. For simplicity here, we keep IDs.
    """
    
    medicine_id: int
    dose_form_id: int
    concentration_amount: float
    concentration_unit: str
    id: Optional[int] = None
    volume_amount: Optional[float] = None
    volume_unit: Optional[str] = None
    chemical_form: Optional[str] = None
    info: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    

@dataclass
class MedicineEntity:
    """
    Domain entity for Medicine.
    This represents the core business concept of a medicine.
    It should be independent of database specifics or API formats.
    """
    name: str
    slug: str
    id: Optional[int] = None    
    generic_name: Optional[str] = None
    status: str = ActiveStatus.ACTIVE
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Relationships (optional in pure domain entity, depends on domain needs)
    # For simplicity, we might just store IDs or load related entities via services
    categories: List[CategoryEntity] = field(default_factory=list)
    strengths: List[StrengthEntity] = field(default_factory=list)
    atc_codes: List[ATCCodeEntity] = field(default_factory=list) # Assuming a many-to-many or one-to-many relationship
