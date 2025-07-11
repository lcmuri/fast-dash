# infrastructure/database/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import func, Column, DateTime
from typing import Optional

Base = declarative_base()

@declarative_mixin
class TimestampMixin:
    """
    Adds automatic timestamp columns to models:
    - created_at: when record was first created
    - updated_at: when record was last updated
    """
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

@declarative_mixin
class SoftDeleteMixin:
    """
    Adds soft delete functionality to models:
    - deleted_at: when record was marked as deleted (nullable)
    - soft_delete(): method to mark as deleted
    """
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Mark the record as deleted without physical deletion"""
        self.deleted_at = func.now()