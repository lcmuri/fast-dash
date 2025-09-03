# app/infrastructure/repositories/ims/medicine_sqlalchemy_repository.py

from typing import List, Optional, Dict, Any # Added Dict, Any for raw data return
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select # Import select for modern SQLAlchemy queries
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

from rich.console import Console

console = Console()

class MedicineSQLAlchemyRepository(IMedicineRepository):
    """
    Concrete implementation of IMedicineRepository using SQLAlchemy and MPTT for categories.
    Translates between domain entities and SQLAlchemy ORM models.
    """
    def __init__(self, db: Session):
        self.db = db

    # --- Helper functions for entity <-> ORM model conversion ---
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
            # print("Warning: Received None in _to_category_entity") # Keep for debugging if needed
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
            level=orm_category.level, # Include MPTT level
            children=[] # Children will be populated when building the tree or explicitly loaded
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

    # --- Medicine CRUD ---
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
        orm_medicine.updated_at = func.now() # Manually update timestamp if not handled by ORM default

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

    # --- Category CRUD (MPTT-aware) ---
    async def get_category_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        """
        Retrieves a single category by its ID. Does not include children by default.
        """
        orm_category = self.db.query(Category).filter(Category.id == category_id).first()
        return self._to_category_entity(orm_category)

    async def get_category_by_slug(self, slug: str) -> Optional[CategoryEntity]:
        orm_category = self.db.query(Category).filter(Category.slug == slug).first()
        return self._to_category_entity(orm_category)

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryEntity]:
        """Get all categories as a flat list with pagination."""
        orm_categories = self.db.query(Category).offset(skip).limit(limit).all()
        return [self._to_category_entity(c) for c in orm_categories]

    async def get_category_tree(self) -> List[CategoryEntity]:
        """Returns complete category hierarchy as a list of root CategoryEntities with nested children."""
        all_categories = self.db.query(Category).order_by(Category.tree_id, Category.left).all()
        
        category_map = {cat.id: self._to_category_entity(cat) for cat in all_categories}
        root_categories = []
        
        for orm_cat in all_categories:
            entity = category_map[orm_cat.id]
            
            if orm_cat.parent_id:
                parent = category_map.get(orm_cat.parent_id)
                if parent:
                    parent.children.append(entity)
            else:
                root_categories.append(entity)
        
        return root_categories

    async def get_category_subtree(self, category_id: int) -> Optional[CategoryEntity]:
        """Get a category with all its descendants as a subtree."""
        root_category = self.db.query(Category).filter(Category.id == category_id).first()
        if not root_category:
            return None
            
        # Get all descendants using MPTT properties, including the root itself
        descendants = self.db.query(Category).filter(
            Category.tree_id == root_category.tree_id,
            Category.left >= root_category.left,
            Category.right <= root_category.right
        ).order_by(Category.left).all()
            
        category_map = {}
        for cat in descendants:
            category_map[cat.id] = self._to_category_entity(cat)
                
        for cat in descendants:
            if cat.id == root_category.id:
                continue # Skip the root itself when assigning children
                
            parent = category_map.get(cat.parent_id)
            if parent:
                parent.children.append(category_map[cat.id])
                    
        return category_map[root_category.id]

    # --- NEW METHODS FOR LAZY LOADING ---

    async def get_top_level_categories_with_child_count(self) -> List[Dict[str, Any]]:
        """
        Retrieves top-level categories and the count of their direct children.
        Returns a list of dictionaries, not CategoryEntity, to include `children_count`.
        """
        # Query for all categories and their direct children counts
        # This is more efficient than fetching all and then processing in Python
        subquery = (
            self.db.query(
                Category.parent_id,
                func.count(Category.id).label("children_count")
            )
            .filter(Category.parent_id.isnot(None)) # Only consider children
            .group_by(Category.parent_id)
            .subquery()
        )

        query = self.db.query(
            Category,
            subquery.c.children_count
        ).outerjoin(
            subquery, Category.id == subquery.c.parent_id
        ).filter(
            Category.parent_id.is_(None) # Filter for top-level categories
        ).order_by(Category.name)

        results = query.all()

        formatted_results = []
        for orm_category, children_count in results:
            category_dict = {
                "id": orm_category.id,
                "name": orm_category.name,
                "slug": orm_category.slug,
                "description": orm_category.description,
                "status": orm_category.status,
                "parent_id": orm_category.parent_id,
                "created_at": orm_category.created_at.isoformat() if orm_category.created_at else None,
                "updated_at": orm_category.updated_at.isoformat() if orm_category.updated_at else None,
                "level": orm_category.level,
                "has_children": (children_count or 0) > 0, # Ensure children_count is not None
                "children_count": (children_count or 0)
            }
            formatted_results.append(category_dict)
        return formatted_results

    async def get_children_of_category_with_child_count(self, category_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves direct children of a given category and the count of their direct children.
        Returns a list of dictionaries.
        """
        # First, check if the parent category exists.
        parent_exists = self.db.query(Category.id).filter(Category.id == category_id).first()
        if not parent_exists:
            return [] # Or raise an error if you prefer to indicate parent not found

        # Optimized query to get direct children and their respective child counts
        subquery = (
            self.db.query(
                Category.parent_id,
                func.count(Category.id).label("children_count")
            )
            .filter(Category.parent_id.isnot(None))
            .group_by(Category.parent_id)
            .subquery()
        )

        query = self.db.query(
            Category,
            subquery.c.children_count
        ).outerjoin(
            subquery, Category.id == subquery.c.parent_id
        ).filter(
            Category.parent_id == category_id # Filter for direct children of the given category_id
        ).order_by(Category.name)

        results = query.all()

        formatted_results = []
        for orm_category, children_count in results:
            category_dict = {
                "id": orm_category.id,
                "name": orm_category.name,
                "slug": orm_category.slug,
                "description": orm_category.description,
                "status": orm_category.status,
                "parent_id": orm_category.parent_id,
                "created_at": orm_category.created_at.isoformat() if orm_category.created_at else None,
                "updated_at": orm_category.updated_at.isoformat() if orm_category.updated_at else None,
                "level": orm_category.level,
                "has_children": (children_count or 0) > 0,
                "children_count": (children_count or 0)
            }
            formatted_results.append(category_dict)
        return formatted_results

    # --- Category CRUD (continued) ---
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
                # Use MPTT's append_child for proper tree maintenance
                parent_orm.append_child(orm_category) 
                self.db.commit()
                self.db.refresh(orm_category) # Refresh to get MPTT fields (level, lft, rgt)
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

        # Handle parent_id change if needed (requires MPTT's move_to method)
        # if category_entity.parent_id is not None and orm_category.parent_id != category_entity.parent_id:
        #     new_parent_orm = self.db.query(Category).filter(Category.id == category_entity.parent_id).first()
        #     if new_parent_orm:
        #         orm_category.move_to(new_parent_orm, position='last-child')
        #     else:
        #         raise ValueError(f"New parent category with ID {category_entity.parent_id} not found.")
        # elif category_entity.parent_id is None and orm_category.parent_id is not None:
        #     # Move to root
        #     orm_category.move_to(None) # MPTT allows moving to None for root

        self.db.add(orm_category)
        self.db.commit()
        self.db.refresh(orm_category)
        return self._to_category_entity(orm_category)

    async def delete_category(self, category_id: int) -> bool:
        orm_category = self.db.query(Category).filter(Category.id == category_id).first()
        if not orm_category:
            raise ValueError(f"Category with ID {category_id} not found.")
        
        try:
            # MPTT's delete() method deletes the node and its descendants
            self.db.delete(orm_category) # SQLAlchemy delete
            self.db.commit() # Commit triggers MPTT's tree reconstruction
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error deleting category: {e}") 

    async def move_category(self, category_id: int, new_parent_id: Optional[int]) -> bool:
        """Move category to new parent (None for root)"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
            
        try:
            if new_parent_id:
                new_parent = self.db.query(Category).filter(Category.id == new_parent_id).first()
                if not new_parent:
                    return False
                # Use MPTT's move_to method
                category.move_to(new_parent, position='last-child')
            else:
                # Move to root
                category.move_to(None) 
                    
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error moving category: {e}") # Provide more specific error info
    
    # --- DoseForm CRUD ---
    async def get_dose_form_by_id(self, dose_form_id: int) -> Optional[DoseFormEntity]:
        orm_dose_form = self.db.query(DoseForm).filter(DoseForm.id == dose_form_id).first()
        return self._to_dose_form_entity(orm_dose_form)

    async def get_all_dose_forms(self, skip: int = 0, limit: int = 100) -> List[DoseFormEntity]:
        orm_dose_forms = self.db.query(DoseForm).offset(skip).limit(limit).all()
        return [self._to_dose_form_entity(df) for df in orm_dose_forms]

    async def create_dose_form(self, dose_form_entity: DoseFormEntity) -> DoseFormEntity:
        orm_dose_form = DoseForm(
            name=dose_form_entity.name,
            description=dose_form_entity.description
        )
        self.db.add(orm_dose_form)
        self.db.commit()
        self.db.refresh(orm_dose_form)
        return self._to_dose_form_entity(orm_dose_form)

    # --- Strength CRUD ---
    async def get_strength_by_id(self, strength_id: int) -> Optional[StrengthEntity]:
        orm_strength = self.db.query(Strength).filter(Strength.id == strength_id).first()
        return self._to_strength_entity(orm_strength)

    async def get_strengths_for_medicine(self, medicine_id: int) -> List[StrengthEntity]:
        orm_strengths = self.db.query(Strength).filter(Strength.medicine_id == medicine_id).all()
        return [self._to_strength_entity(s) for s in orm_strengths]

    async def create_strength(self, strength_entity: StrengthEntity) -> StrengthEntity:
        orm_strength = Strength(
            medicine_id=strength_entity.medicine_id,
            dose_form_id=strength_entity.dose_form_id,
            concentration_amount=strength_entity.concentration_amount,
            concentration_unit=strength_entity.concentration_unit,
            volume_amount=strength_entity.volume_amount,
            volume_unit=strength_entity.volume_unit,
            chemical_form=strength_entity.chemical_form,
            info=strength_entity.info,
            description=strength_entity.description
        )
        self.db.add(orm_strength)
        self.db.commit()
        self.db.refresh(orm_strength)
        return self._to_strength_entity(orm_strength)

    # --- ATC Code CRUD ---
    async def get_atc_code_by_id(self, atc_code_id: int) -> Optional[ATCCodeEntity]:
        orm_atc_code = self.db.query(ATCCode).filter(ATCCode.id == atc_code_id).first()
        return self._to_atc_code_entity(orm_atc_code)

    async def get_atc_code_by_code(self, code: str) -> Optional[ATCCodeEntity]:
        orm_atc_code = self.db.query(ATCCode).filter(ATCCode.code == code).first()
        return self._to_atc_code_entity(orm_atc_code)

    async def get_atc_code_by_slug(self, slug: str) -> Optional[ATCCodeEntity]:
        orm_atc_code = self.db.query(ATCCode).filter(ATCCode.slug == slug).first()
        return self._to_atc_code_entity(orm_atc_code)

    async def get_all_atc_codes(self, skip: int = 0, limit: int = 100) -> List[ATCCodeEntity]:
        orm_atc_codes = self.db.query(ATCCode).offset(skip).limit(limit).all()
        return [self._to_atc_code_entity(atc) for atc in orm_atc_codes]

    async def create_atc_code(self, atc_code_entity: ATCCodeEntity) -> ATCCodeEntity:
        orm_atc_code = ATCCode(
            parent_id=atc_code_entity.parent_id,
            name=atc_code_entity.name,
            code=atc_code_entity.code,
            level=atc_code_entity.level,
            slug=atc_code_entity.slug,
            status=atc_code_entity.status,
            description=atc_code_entity.description,
            created_by=atc_code_entity.created_by,
            updated_by=atc_code_entity.updated_by,
            deleted_by=atc_code_entity.deleted_by
        )
        self.db.add(orm_atc_code)
        self.db.commit()
        self.db.refresh(orm_atc_code)
        return self._to_atc_code_entity(orm_atc_code)

    async def add_atc_codes_to_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            raise ValueError(f"Medicine with ID {medicine_id} not found.")

        existing_atc_code_ids = {atc.id for atc in orm_medicine.atc_codes}
        for atc_id in atc_code_ids:
            if atc_id not in existing_atc_code_ids:
                orm_atc_code = self.db.query(ATCCode).filter(ATCCode.id == atc_id).first()
                if orm_atc_code:
                    orm_medicine.atc_codes.append(orm_atc_code)
        self.db.commit()
        self.db.refresh(orm_medicine)

    async def remove_atc_codes_from_medicine(self, medicine_id: int, atc_code_ids: List[int]) -> None:
        orm_medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not orm_medicine:
            raise ValueError(f"Medicine with ID {medicine_id} not found.")

        atc_codes_to_remove = [atc for atc in orm_medicine.atc_codes if atc.id in atc_code_ids]
        for atc in atc_codes_to_remove:
            orm_medicine.atc_codes.remove(atc)
        self.db.commit()
        self.db.refresh(orm_medicine)