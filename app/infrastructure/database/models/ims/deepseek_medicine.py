from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from infrastructure.database.base import Base, TimestampMixin, SoftDeleteMixin

# infrastructure/database/models/ims/medicine.py > MedicineModel
class MedicineModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "medicines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False)
    generic_name = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    description = Column(Text, nullable=True)
    
    # Relationships
    strengths = relationship("Strength", back_populates="medicine", cascade="all, delete-orphan")
    categories = relationship(
        "Category",
        secondary="medicine_category",
        back_populates="medicines",
        lazy="selectin"  # Eager loading
    )
    
    __mapper_args__ = {
        "eager_defaults": True
    }


# infrastructure/database/models/ims/medicine.py > ATCCodeModel
class ATCCodeModel(Base):
    __tablename__ = 'atc_codes'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('atc_codes.id'), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True)
    level = Column(Integer)
    slug = Column(String(255), unique=True)
    status = Column(String(20), default='active')
    description = Column(Text, nullable=True)
    
    parent = relationship("ATCCode", remote_side=[id])
    medicines = relationship("Medicine", back_populates="atc_code")


# infrastructure/database/models/ims/medicine.py > StrengthModel
class StrengthModel(Base):
    __tablename__ = 'strengths'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey('medicines.id'))
    dose_form_id = Column(UUID(as_uuid=True), ForeignKey('dose_forms.id'))
    
    concentration_amount = Column(Numeric(8, 3))
    concentration_unit = Column(String(20))
    volume_amount = Column(Numeric(8, 3), nullable=True)
    volume_unit = Column(String(20), nullable=True)
    chemical_form = Column(String(100), nullable=True)
    info = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    medicine = relationship("Medicine", back_populates="strengths")
    dose_form = relationship("DoseForm", back_populates="strengths")