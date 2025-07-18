from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.domains.ims.medicine.repositories.medicine_repository import IMedicineRepository
from app.domains.ims.medicine.entities.medicine import (
    MedicineEntity,
    CategoryEntity,
    DoseFormEntity,
    StrengthEntity,
    ATCCodeEntity
)
from app.infrastructure.database.models.ims.medicine import (
    Medicine,
    Category,
    DoseForm,
    Strength,
    ATCCode,
    MedicineCategory,
    MedicineATCCode
)

class MedicineSQLAlchemyRepository(IMedicineRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_medicine_entity(self, orm_medicine: Medicine) -> MedicineEntity:
        if not orm_medicine:
            return None
        categories = [self._to_category_entity(cat) for cat in orm_medicine.categories]
        strengths = [self._to_strength_entity(s) for s in orm_medicine.strengths]
        atc_codes = [self._to_atc_code_entity(atc) for atc in orm_medicine.atc_codes]

        return MedicineEntity(
            id=orm_medicine.id,
            name=orm_medicine.name,
            slug=orm_medicine.slug,
            generic_name=orm_medicine.generic_name,
            status=orm_medicine.status,
            description=orm_medicine.description,
            created_at=orm_medicine.created_at,
            updated_at=orm_medicine.updated_at,
            categories=categories,
            strengths=strengths,
            atc_codes=atc_codes
        )

    def _to_category_entity(self, orm_category: Category) -> CategoryEntity:
        if not orm_category:
            return None
        return CategoryEntity(
            id=orm_category.id,
            parent_id=orm_category.parent_id,
            name=orm_category.name,
            slug=orm_category.slug,
            description=orm_category.description,
            status=orm_category.status,
            created_at=orm_category.created_at,
            updated_at=orm_category.updated_at,
            level=orm_category.level,
            children=[]
        )

    def _to_dose_form_entity(self, orm_dose_form: DoseForm) -> DoseFormEntity:
        if not orm_dose_form:
            return None
        return DoseFormEntity(
            id=orm_dose_form.id,
            name=orm_dose_form.name,
            description=orm_dose_form.description,
            created_at=orm_dose_form.created_at,
            updated_at=orm_dose_form.updated_at
        )

    def _to_strength_entity(self, orm_strength: Strength) -> StrengthEntity:
        if not orm_strength:
            return None
        return StrengthEntity(
            id=orm_strength.id,
            medicine_id=orm_strength.medicine_id,
            dose_form_id=orm_strength.dose_form_id,
            concentration_amount=float(orm_strength.concentration_amount),
            concentration_unit=orm_strength.concentration_unit,
            volume_amount=float(orm_strength.volume_amount) if orm_strength.volume_amount else None,
            volume_unit=orm_strength.volume_unit,
            chemical_form=orm_strength.chemical_form,
            info=orm_strength.info,
            description=orm_strength.description,
            created_at=orm_strength.created_at,
            updated_at=orm_strength.updated_at,
            deleted_at=orm_strength.deleted_at
        )

    def _to_atc_code_entity(self, orm_atc_code: ATCCode) -> ATCCodeEntity:
        if not orm_atc_code:
            return None
        return ATCCodeEntity(
            id=orm_atc_code.id,
            parent_id=orm_atc_code.parent_id,
            name=orm_atc_code.name,
            code=orm_atc_code.code,
            level=orm_atc_code.level,
            slug=orm_atc_code.slug,
            status=orm_atc_code.status,
            description=orm_atc_code.description,
            created_by=orm_atc_code.created_by,
            updated_by=orm_atc_code.updated_by,
            deleted_by=orm_atc_code.deleted_by,
            created_at=orm_atc_code.created_at,
            updated_at=orm_atc_code.updated_at,
            deleted_at=orm_atc_code.deleted_at
        )

    async def get_medicine_by_id(self, medicine_id: int) -> Optional[MedicineEntity]:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        return self._to_medicine_entity(orm_medicine)

    async def get_medicine_by_slug(self, slug: str) -> Optional[MedicineEntity]:
        orm_medicine = self.db.query(Medicine).filter(Medicine.slug == slug).first()
        return self._to_medicine_entity(orm_medicine)

    async def get_all_medicines(self, skip: int = 0, limit: int = 100) -> List[MedicineEntity]:
        orm_medicines = self.db.query(Medicine).offset(skip).limit(limit).all()
        return [self._to_medicine_entity(m) for m in orm_medicines]

    async def create_medicine(self, medicine_entity: MedicineEntity) -> MedicineEntity:
        orm_medicine = Medicine(
            name=medicine_entity.name,
            slug=medicine_entity.slug,
            generic_name=medicine_entity.generic_name,
            status=medicine_entity.status,
            description=medicine_entity.description
        )
        self.db.add(orm_medicine)
        self.db.commit()
        self.db.refresh(orm_medicine)
        return self._to_medicine_entity(orm_medicine)

    async def update_medicine(self, medicine_id: int, medicine_entity: MedicineEntity) -> Optional[MedicineEntity]:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            return None

        orm_medicine.name = medicine_entity.name
        orm_medicine.slug = medicine_entity.slug
        orm_medicine.generic_name = medicine_entity.generic_name
        orm_medicine.status = medicine_entity.status
        orm_medicine.description = medicine_entity.description
        orm_medicine.updated_at = func.now()

        self.db.add(orm_medicine)
        self.db.commit()
        self.db.refresh(orm_medicine)
        return self._to_medicine_entity(orm_medicine)

    async def delete_medicine(self, medicine_id: int) -> bool:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            return False
        self.db.delete(orm_medicine)
        self.db.commit()
        return True

    async def add_categories_to_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            raise ValueError(f"Medicine with ID {medicine_id} not found.")

        existing_category_ids = {cat.id for cat in orm_medicine.categories}
        for cat_id in category_ids:
            if cat_id not in existing_category_ids:
                orm_category = self.db.query(Category).filter(Category.id == cat_id).first()
                if orm_category:
                    orm_medicine.categories.append(orm_category)
        self.db.commit()
        self.db.refresh(orm_medicine)

    async def remove_categories_from_medicine(self, medicine_id: int, category_ids: List[int]) -> None:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            raise ValueError(f"Medicine with ID {medicine_id} not found.")

        categories_to_remove = [cat for cat in orm_medicine.categories if cat.id in category_ids]
        for cat in categories_to_remove:
            orm_medicine.categories.remove(cat)
        self.db.commit()
        self.db.refresh(orm_medicine)

    async def get_category_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        orm_category = self.db.query(Category).filter(Category.id == category_id).first()
        return self._to_category_entity(orm_category)

    async def get_category_by_slug(self, slug: str) -> Optional[CategoryEntity]:
        orm_category = self.db.query(Category).filter(Category.slug == slug).first()
        return self._to_category_entity(orm_category)

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryEntity]:
        orm_categories = self.db.query(Category).offset(skip).limit(limit).all()
        return [self._to_category_entity(c) for c in orm_categories]

    async def get_category_tree(self) -> List[CategoryEntity]:
        orm_categories = self.db.query(Category).order_by(Category.tree_id, Category.left).all()

        id_to_node = {category.id: category for category in orm_categories}

        for category in orm_categories:
            category.children = []

        roots = []

        for category in orm_categories:
            if category.parent_id and category.parent_id in id_to_node:
                parent = id_to_node[category.parent_id]
                parent.children.append(category)
            else:
                roots.append(category)

        def convert_orm_node_to_entity_node(orm_node: Category) -> CategoryEntity:
            entity_node = CategoryEntity(
                id=orm_node.id,
                parent_id=orm_node.parent_id,
                name=orm_node.name,
                slug=orm_node.slug,
                description=orm_node.description,
                status=orm_node.status,
                created_at=orm_node.created_at.isoformat() if orm_node.created_at else None,
                updated_at=orm_node.updated_at.isoformat() if orm_node.updated_at else None,
                level=orm_node.level,
                children=[convert_orm_node_to_entity_node(child) for child in (orm_node.children or [])]
            )
            return entity_node

        return [convert_orm_node_to_entity_node(root) for root in roots]

    async def create_category(self, category_entity: CategoryEntity, parent_id: Optional[int] = None) -> CategoryEntity:
        orm_category = Category(
            name=category_entity.name.lower().strip() if category_entity.name else None,
            slug=category_entity.slug.lower().strip() if category_entity.slug else None,
            description=category_entity.description,
            status=category_entity.status,
        )

        if parent_id:
            parent_orm = self.db.query(Category).filter(Category.id == parent_id).first()
            if not parent_orm:
                raise ValueError(f"Parent category with ID {parent_id} not found.")
            try:
                orm_category.parent_id = parent_id
                self.db.add(orm_category)
                self.db.commit()
                self.db.refresh(orm_category)
            except IntegrityError as e:
                self.db.rollback()
                raise ValueError(f"Failed to append child category: {e}")
        else:
            self.db.add(orm_category)
            self.db.commit()
            self.db.refresh(orm_category)

        return self._to_category_entity(orm_category)

    async def update_category(self, category_id: int, category_entity: CategoryEntity) -> Optional[CategoryEntity]:
        orm_category = self.db.query(Category).filter(Category.id == category_id).first()
        if not orm_category:
            return None

        orm_category.name = category_entity.name.lower().strip() if category_entity.name else None
        orm_category.slug = category_entity.slug.lower().strip() if category_entity.slug else None
        orm_category.description = category_entity.description
        orm_category.status = category_entity.status
        orm_category.updated_at = func.now()

        self.db.add(orm_category)
        self.db.commit()
        self.db.refresh(orm_category)
        return self._to_category_entity(orm_category)
