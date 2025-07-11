# api/v1/endpoints/category.py
from typing import List
from fastapi import APIRouter, Depends
from domain.entities.category import Category, CategoryWithChildren
from application.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/{id}/tree", response_model=CategoryWithChildren)
async def get_category_tree(
    id: UUID,
    service: CategoryService = Depends(get_category_service),
    depth: int = 3
):
    """Get category with nested children up to specified depth"""
    return await service.get_with_children(id, max_depth=depth)

@router.get("/{id}/parents", response_model=List[Category])
async def get_category_parents(
    id: UUID,
    service: CategoryService = Depends(get_category_service)
):
    """Get all parent categories up to root"""
    return await service.get_parents(id)

# Similar recursive endpoints for ATC codes