# app/infrastructure/database/models/ims/medicine.py

from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    DECIMAL,
    UniqueConstraint,    
)
from sqlalchemy.orm import (
    Mapped,
    relationship,
    mapped_column,
)
# Import MPTT
from sqlalchemy_mptt.mixins import BaseNestedSets
from app.infrastructure.database.base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin


class ATCCode(Base, TimestampMixin, BaseNestedSets): # Added TimestampMixin, SoftDeleteMixin, BaseNestedSets
    __tablename__ = "atc_codes"

    """
    SQLAlchemy ORM model for 'atc_codes' table.
    Corresponds to 2025_06_03_132801_create_atc_codes_table.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at, deleted_at handled by mixins
    # MPTT will add lft, rgt, level, tree_id, parent_id automatically if not present.
    # We keep parent_id explicitly here as it's part of your original schema.

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('atc_codes.id'), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False) # MPTT also uses 'level'
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   

    # Many-to-many with Medicine (assuming a pivot table)
    medicines: Mapped[list["Medicine"]] = relationship(
        "Medicine",
        secondary="medicine_atc_code",
        back_populates="atc_codes",
        lazy="selectin",  # Use selectin loading for better performance
        overlaps="medicine_atc_codes_association"
    )

    medicine_atc_codes_association: Mapped[list["MedicineATCCode"]] = relationship(
        "MedicineATCCode",
        back_populates="atc_code",
        cascade="all, delete-orphan",
        overlaps="atc_codes,medicines"
    )


class Category(Base, TimestampMixin, BaseNestedSets): # Added TimestampMixin, BaseNestedSets
    __tablename__ = "categories"

    """
    SQLAlchemy ORM model for 'categories' table, using MPTT for hierarchy.
    Corresponds to 2025_06_07_142237_create_categories_table.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at handled by mixins
    # MPTT will add lft, rgt, level, tree_id, parent_id automatically if not present.
    # We keep parent_id explicitly here as it's part of your original schema.

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id'), nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)

    # MPTT will manage the parent/children relationships internally.
    # You generally don't define `parent = relationship(...)` or `children = relationship(...)`
    # directly when using MPTT for the primary tree structure.

    # Many-to-many with Medicine (via medicine_category pivot table)
    medicines: Mapped[list["Medicine"]] = relationship(
        "Medicine",
        secondary="medicine_category",
        back_populates="categories",
        overlaps="medicine_categories_association"
    )
    medicine_categories_association: Mapped[list["MedicineCategory"]] = relationship(
        "MedicineCategory",
        back_populates="category",
        cascade="all, delete-orphan",
        overlaps="medicines,categories"
    )


class DoseForm(Base, TimestampMixin): # Added TimestampMixin
    __tablename__ = "dose_forms"

    """
    SQLAlchemy ORM model for 'dose_forms' table.
    Corresponds to 2025_06_16_095143_create_dose_forms_table.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at handled by mixins

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Medicine(Base, TimestampMixin): # Added TimestampMixin
    __tablename__ = "medicines"

    """
    SQLAlchemy ORM model for 'medicines' table.
    Corresponds to 2025_06_03_130011_create_medicines_table.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at handled by mixins

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False) # Assuming slug is unique
    generic_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    # Many-to-many with Category (via medicine_category pivot table)
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="medicine_category",
        back_populates="medicines",
        overlaps="medicine_categories_association"
    )

    # One-to-many with Strength
    strengths: Mapped[list["Strength"]] = relationship("Strength", back_populates="medicine", cascade="all, delete-orphan")

    # Many-to-many with ATCCode (assuming a pivot table or direct relationship if applicable)
    atc_codes: Mapped[list["ATCCode"]] = relationship(
        "ATCCode",
        secondary="medicine_atc_code",
        back_populates="medicines",
        overlaps="medicine_atc_codes_association"
    )
    medicine_categories_association: Mapped[list["MedicineCategory"]] = relationship(
        "MedicineCategory",
        back_populates="medicine",
        cascade="all, delete-orphan",
        overlaps="categories,medicines"
    )
    medicine_atc_codes_association: Mapped[list["MedicineATCCode"]] = relationship(
        "MedicineATCCode",
        back_populates="medicine",
        cascade="all, delete-orphan",
        overlaps="atc_codes,medicines"
    )


class MedicineCategory(Base, TimestampMixin): # Added TimestampMixin
    __tablename__ = "medicine_category"

    """
    SQLAlchemy ORM model for the 'medicine_category' pivot table.
    Corresponds to 2025_06_16_095248_medicine_category.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at handled by mixins

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)

    # Define relationships from pivot table back to main tables
    medicine: Mapped["Medicine"] = relationship("Medicine", back_populates="medicine_categories_association")
    category: Mapped["Category"] = relationship("Category", back_populates="medicine_categories_association")

    __table_args__ = (UniqueConstraint('medicine_id', 'category_id', name='_medicine_category_uc'),)

    medicine: Mapped["Medicine"] = relationship(
    "Medicine",
    back_populates="medicine_categories_association",
    overlaps="categories,medicines"
    )
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="medicine_categories_association",
        overlaps="categories,medicines"
    )


class Strength(Base, TimestampMixin): # Added TimestampMixin
    __tablename__ = "strengths"
    """
    SQLAlchemy ORM model for 'strengths' table.
    Corresponds to 2025_06_16_095858_create_strengths_table.php
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at, deleted_at handled by mixins

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    dose_form_id: Mapped[int] = mapped_column(ForeignKey('dose_forms.id'), nullable=False)

    concentration_amount: Mapped[float] = mapped_column(DECIMAL(8, 3), nullable=False) # Changed to float for Mapped
    concentration_unit: Mapped[str] = mapped_column(String, nullable=False)
    volume_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(8, 3), nullable=True) # Changed to float for Mapped
    volume_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    chemical_form: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    info: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    medicine: Mapped["Medicine"] = relationship("Medicine", back_populates="strengths")
    dose_form: Mapped["DoseForm"] = relationship("DoseForm")

    __table_args__ = (
        UniqueConstraint(
            'medicine_id',
            'dose_form_id',
            'concentration_amount',
            'concentration_unit',
            'chemical_form',
            'volume_amount',
            'volume_unit',
            'info',
            name='_strength_unique_constraint'
        ),
    )


class MedicineATCCode(Base, TimestampMixin): # Added TimestampMixin
    __tablename__ = "medicine_atc_code"
    """
    SQLAlchemy ORM model for a pivot table between medicines and atc_codes.
    """
    # __tablename__ is handled by Base
    # id, created_at, updated_at handled by mixins

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    atc_code_id: Mapped[int] = mapped_column(ForeignKey('atc_codes.id', ondelete='CASCADE'), nullable=False)

    medicine: Mapped["Medicine"] = relationship("Medicine", back_populates="medicine_atc_codes_association")
    atc_code: Mapped["ATCCode"] = relationship("ATCCode", back_populates="medicine_atc_codes_association")

    __table_args__ = (UniqueConstraint('medicine_id', 'atc_code_id', name='_medicine_atc_code_uc'),)

    medicine: Mapped["Medicine"] = relationship(
    "Medicine",
    back_populates="medicine_atc_codes_association",
    overlaps="atc_codes,medicines"
    )
    atc_code: Mapped["ATCCode"] = relationship(
        "ATCCode",
        back_populates="medicine_atc_codes_association",
        overlaps="atc_codes,medicines"
    )

# --- Add back_populates to existing relationships if they were not Mapped[list] ---
# These were already mostly correct in your original file, just ensuring consistency
# with Mapped[] types and explicit back_populates.

# ATCCode.medicines is already defined in ATCCode class.
# Medicine.medicine_atc_codes_association is already defined in Medicine class.
# ATCCode.medicine_atc_codes_association is already defined in ATCCode class.


# Category.medicines is already defined in Category class.
# Medicine.medicine_categories_association is already defined in Medicine class.
# Category.medicine_categories_association is already defined in Category class.

