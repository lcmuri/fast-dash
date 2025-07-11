# infrastructure/repositories/medicine.py
from uuid import UUID
from sqlalchemy.orm import Session
from domains.ims.medicine.entities.medicine import Medicine, MedicineCreate, MedicineUpdate
from domains.ims.medicine.repositories import MedicineRepository
from infrastructure.database.models.ims.medicine import MedicineModel

class MedicineRepositoryImpl(MedicineRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, medicine: MedicineCreate) -> Medicine:
        db_medicine = MedicineModel(**medicine.dict(exclude={"category_ids"}))
        self.db.add(db_medicine)
        self.db.commit()
        self.db.refresh(db_medicine)
        
        if medicine.category_ids:
            self._update_categories(db_medicine, medicine.category_ids)
        
        return Medicine.from_orm(db_medicine)
    
    def _update_categories(self, medicine: MedicineModel, category_ids: list[UUID]):
        medicine.categories = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.id.in_(category_ids))
            .all()
        )
        self.db.commit()
    
    # Implement other CRUD methods following same pattern

# Similar implementations for Category, ATCCode, and DoseForm repositories