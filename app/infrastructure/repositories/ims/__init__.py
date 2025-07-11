# app/infrastructure/repositories/ims/__init__.py

# This file makes the 'ims' directory a Python package
# and allows for easier imports of the concrete repositories.

from .medicine_sqlalchemy_repository import MedicineSQLAlchemyRepository

__all__ = [
    "MedicineSQLAlchemyRepository"
]
