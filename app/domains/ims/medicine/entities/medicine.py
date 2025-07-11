# app/domains/ims/medicine/entities/medicine.py

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

# Enums (if applicable, could be defined in a central core/enums or here)
class ActiveStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"

@dataclass
class ATCCodeEntity:
    """
    Domain entity for ATC Codes.
    Represents the core concept of an ATC code, independent of persistence.
    """
    id: Optional[int] = None
    parent_id: Optional[int] = None
    name: str
    code: str
    level: int
    slug: str
    status: str = ActiveStatus.ACTIVE
    description: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class CategoryEntity:
    """
    Domain entity for Categories.
    Includes MPTT-related fields for hierarchical representation.
    """
    id: Optional[int] = None
    parent_id: Optional[int] = None
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    status: str = ActiveStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    level: Optional[int] = None # Added for MPTT level
    # lft: Optional[int] = None # MPTT left value (can be included if domain needs it)
    # rgt: Optional[int] = None # MPTT right value (can be included if domain needs it)
    children: List["CategoryEntity"] = field(default_factory=list) # For hierarchical representation
