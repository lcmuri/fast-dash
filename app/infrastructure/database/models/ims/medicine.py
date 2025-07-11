# app/infrastructure/database/models/ims/medicine.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, func
from sqlalchemy.sql import expression
from sqlalchemy.ext.associationproxy import association_proxy # For many-to-many simplified access
from app.infrastructure.database.base import TimestampMixin, SoftDeleteMixin

# Base for declarative models
Base = declarative_base()

class ATCCode(Base):
    """
    SQLAlchemy ORM model for 'atc_codes' table.
    Corresponds to 2025_06_03_132801_create_atc_codes_table.php
    """
    __tablename__ = "atc_codes"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey('atc_codes.id'), nullable=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    level = Column(Integer, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    status = Column(String, default="active", nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    deleted_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True) # For soft deletes

    # Self-referencing relationship for hierarchical structure
    parent = relationship("ATCCode", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<ATCCode(id={self.id}, code='{self.code}', name='{self.name}')>"

class Category(Base, TimestampMixin):
    """
    SQLAlchemy ORM model for 'categories' table.
    Corresponds to 2025_06_07_142237_create_categories_table.php
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=True) # Added unique constraint based on common practice
    description = Column(Text, nullable=True)
    status = Column(String, default="active", nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Self-referencing relationship for hierarchical structure
    parent = relationship("Category", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class DoseForm(Base):
    """
    SQLAlchemy ORM model for 'dose_forms' table.
    Corresponds to 2025_06_16_095143_create_dose_forms_table.php
    """
    __tablename__ = "dose_forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DoseForm(id={self.id}, name='{self.name}')>"

class Medicine(Base):
    """
    SQLAlchemy ORM model for 'medicines' table.
    Corresponds to 2025_06_03_130011_create_medicines_table.php
    """
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False) # Assuming slug is unique
    generic_name = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    # Many-to-many with Category (via medicine_category pivot table)
    categories = relationship(
        "Category",
        secondary="medicine_category",
        back_populates="medicines"
    )

    # One-to-many with Strength
    strengths = relationship("Strength", back_populates="medicine", cascade="all, delete-orphan")

    # Many-to-many with ATCCode (assuming a pivot table or direct relationship if applicable)
    # For simplicity, assuming a direct many-to-many via a new pivot table `medicine_atc_code`
    atc_codes = relationship(
        "ATCCode",
        secondary="medicine_atc_code",
        back_populates="medicines"
    )

    def __repr__(self):
        return f"<Medicine(id={self.id}, name='{self.name}')>"

class MedicineCategory(Base):
    """
    SQLAlchemy ORM model for the 'medicine_category' pivot table.
    Corresponds to 2025_06_16_095248_medicine_category.php
    """
    __tablename__ = "medicine_category"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Define relationships from pivot table back to main tables
    medicine = relationship("Medicine", back_populates="medicine_categories_association")
    category = relationship("Category", back_populates="medicine_categories_association")

    __table_args__ = (UniqueConstraint('medicine_id', 'category_id', name='_medicine_category_uc'),)

# Add back_populates to Category and Medicine for the many-to-many relationship
Category.medicines = relationship(
    "Medicine",
    secondary="medicine_category",
    back_populates="categories"
)
Medicine.medicine_categories_association = relationship(
    "MedicineCategory",
    back_populates="medicine",
    cascade="all, delete-orphan"
)
Category.medicine_categories_association = relationship(
    "MedicineCategory",
    back_populates="category",
    cascade="all, delete-orphan"
)


class Strength(Base):
    """
    SQLAlchemy ORM model for 'strengths' table.
    Corresponds to 2025_06_16_095858_create_strengths_table.php
    """
    __tablename__ = "strengths"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    dose_form_id = Column(Integer, ForeignKey('dose_forms.id'), nullable=False)

    concentration_amount = Column(DECIMAL(8, 3), nullable=False)
    concentration_unit = Column(String, nullable=False)
    volume_amount = Column(DECIMAL(8, 3), nullable=True)
    volume_unit = Column(String, nullable=True)
    chemical_form = Column(String, nullable=True)
    info = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True) # For soft deletes

    # Relationships
    medicine = relationship("Medicine", back_populates="strengths")
    dose_form = relationship("DoseForm")

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

    def __repr__(self):
        return (
            f"<Strength(id={self.id}, medicine_id={self.medicine_id}, "
            f"concentration='{self.concentration_amount} {self.concentration_unit}')>"
        )

# Assuming a pivot table for Medicine and ATC codes (not explicitly in your migrations, but common)
class MedicineATCCode(Base):
    """
    SQLAlchemy ORM model for a pivot table between medicines and atc_codes.
    (This pivot table was not in your provided PHP migrations, but is implied
    by the domain entity's relationship to atc_codes. If it exists in your DB,
    you'd have a migration for it.)
    """
    __tablename__ = "medicine_atc_code"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    atc_code_id = Column(Integer, ForeignKey('atc_codes.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    medicine = relationship("Medicine", back_populates="medicine_atc_codes_association")
    atc_code = relationship("ATCCode", back_populates="medicine_atc_codes_association")

    __table_args__ = (UniqueConstraint('medicine_id', 'atc_code_id', name='_medicine_atc_code_uc'),)

# Add back_populates to Medicine and ATCCode for the many-to-many relationship
ATCCode.medicines = relationship(
    "Medicine",
    secondary="medicine_atc_code",
    back_populates="atc_codes"
)
Medicine.medicine_atc_codes_association = relationship(
    "MedicineATCCode",
    back_populates="medicine",
    cascade="all, delete-orphan"
)
ATCCode.medicine_atc_codes_association = relationship(
    "MedicineATCCode",
    back_populates="atc_code",
    cascade="all, delete-orphan"
)
