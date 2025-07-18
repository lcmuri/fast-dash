import json
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    event,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    declarative_mixin,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property


# --- 1. Base Declaration ---
# Define a base class for your declarative models
class Base(DeclarativeBase):
    """Base class which provides automated table name
    and sets up useful defaults.
    """
    __abstract__ = True # This base class itself won't be mapped to a table

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower() + "s"

    # Define a default constructor that accepts keyword arguments for mapped attributes
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                # Optionally raise an error or log a warning for unmapped attributes
                pass

    def __repr__(self):
        """Generic __repr__ for better debugging."""
        columns = ", ".join(f"{c.name}={getattr(self, c.name)!r}" for c in self.__table__.columns)
        return f"<{self.__class__.__name__}({columns})>"


# --- 2. TimestampMixin ---
@declarative_mixin
class TimestampMixin:
    """Provides created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated"
    )


# --- 3. SoftDeleteMixin ---
@declarative_mixin
class SoftDeleteMixin:
    """Provides a deleted_at column for soft deletion."""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the record was soft-deleted"
    )

    @hybrid_property
    def is_deleted(self) -> bool:
        """Returns True if the record is soft-deleted."""
        return self.deleted_at is not None

    @is_deleted.expression
    def is_deleted(cls):
        """SQL expression for is_deleted property."""
        return cls.deleted_at.isnot(None)

    def soft_delete(self, session: Session) -> None:
        """Marks the record as deleted by setting deleted_at timestamp."""
        self.deleted_at = func.now()
        session.add(self)
        session.flush() # Flush to ensure the change is applied for auditing if needed

    def restore(self, session: Session) -> None:
        """Restores a soft-deleted record by setting deleted_at to None."""
        self.deleted_at = None
        session.add(self)
        session.flush() # Flush to ensure the change is applied for auditing if needed


# --- 4. AuditMixin and AuditLog Model ---

# Define the AuditLog model (this will be a concrete table)
class AuditLog(Base):
    """Table to store audit trails for changes to other models."""
    __tablename__ = 'audit_logs' # Explicitly define table name for this concrete model

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="ID of the record being audited")
    action: Mapped[str] = mapped_column(String(20), nullable=False, comment="Type of action: INSERT, UPDATE, DELETE")
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="JSON string of old values")
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="JSON string of new values")
    changed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="User ID who made the change")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, table_name='{self.table_name}', "
            f"record_id='{self.record_id}', action='{self.action}', "
            f"changed_by='{self.changed_by}', changed_at='{self.changed_at}')>"
        )

# Placeholder for getting the current user ID
# In a real application, this would come from your authentication system (e.g., Flask-Login, FastAPI dependency)
def get_current_user_id() -> Optional[str]:
    """Simulates getting the current authenticated user's ID."""
    # For demonstration, let's return a fixed ID or None
    return "demo_user_123" # Replace with actual user ID retrieval logic


_T = TypeVar('_T', bound=Base)

@declarative_mixin
class AuditMixin:
    """
    Provides auditing capabilities for a model by logging changes to AuditLog table.
    """
    # This relationship is defined dynamically for each inheriting class
    @declared_attr
    def audit_logs(cls) -> Mapped[list[AuditLog]]:
        """Defines a relationship to the AuditLog table for this specific model."""
        return relationship(
            AuditLog,
            primaryjoin=f"and_("
                        f"AuditLog.table_name == '{cls.__tablename__}', "
                        f"AuditLog.record_id == cast({cls.__name__}.id, String)" # Cast ID to string for record_id
                        f")",
            viewonly=True, # Prevent SQLAlchemy from managing this relationship for persistence
            order_by=AuditLog.changed_at.desc()
        )

    @classmethod
    def __declare_last__(cls):
        """
        Register event listeners after the class is fully declared.
        This ensures all columns and relationships are set up.
        """
        event.listen(cls, 'before_insert', cls._audit_before_insert)
        event.listen(cls, 'before_update', cls._audit_before_update)
        event.listen(cls, 'before_delete', cls._audit_before_delete)

    @classmethod
    def _audit_before_insert(cls, mapper: Any, connection: Any, target: _T) -> None:
        """Event listener for 'before_insert'."""
        session = Session(bind=connection) # Create a session bound to the current connection
        new_values = {
            c.name: getattr(target, c.name)
            for c in target.__table__.columns
            if c.name != 'id' # ID is not available before insert
        }
        # ID will be available after the insert, so we'll log it as 'pending' for now
        # and update it in a 'after_insert' if needed, or rely on the DB for ID.
        # For simplicity, we'll assume ID is set by DB and captured in 'record_id' later.
        # Or, more robustly, we could use 'after_insert' to get the actual ID.
        # For this example, we'll use a placeholder for record_id and assume it's
        # captured correctly in a real scenario (e.g., by flushing and then getting the ID).

        # For 'before_insert', the target.id might not be set yet if it's auto-incrementing.
        # A common pattern is to use 'after_insert' or rely on the DB to set the ID.
        # For simplicity, we'll use a placeholder and note this limitation.
        # In a real app, you'd likely flush the session here to get the ID, or use
        # a different event or a custom session extension.
        # For this example, we'll just use a generic placeholder for record_id.
        # A more robust solution might involve:
        #   1. Using a UUID for primary keys.
        #   2. Using after_insert event to get the generated ID.
        #   3. Relying on the DB to generate the ID and then fetching it.

        # For this demo, let's assume `target.id` is available after a flush,
        # or we'll use a temporary identifier.
        # A simpler approach for 'before_insert' is to just log the new values
        # and let the 'record_id' be updated later if needed.
        # For `before_insert`, `target.id` might not be populated yet if it's an auto-incrementing primary key.
        # We'll use a placeholder for `record_id` and note this.
        # In a real application, you might use `after_insert` to get the generated ID.
        record_id_placeholder = "pending_id" # This will need to be updated after insert

        audit_entry = AuditLog(
            table_name=cls.__tablename__,
            record_id=str(getattr(target, 'id', record_id_placeholder)), # Attempt to get ID, or use placeholder
            action="INSERT",
            old_values=None,
            new_values=json.dumps(new_values, default=str), # default=str handles datetime objects
            changed_by=get_current_user_id(),
        )
        session.add(audit_entry)


    @classmethod
    def _audit_before_update(cls, mapper: Any, connection: Any, target: _T) -> None:
        """Event listener for 'before_update'."""
        session = Session(bind=connection)
        # Get original values from the database
        original_data = {}
        # Iterate over changed attributes
        changed_data = {}
        for attr in target._sa_instance_state.attrs:
            if attr.key in target.__table__.columns.keys() and attr.history.has_changes():
                # Get old value (before update)
                old_value = attr.history.unchanged[0] if attr.history.unchanged else None
                # Get new value (after update)
                new_value = attr.history.added[0] if attr.history.added else None

                # Only include if values are different (and not None for both)
                if old_value != new_value:
                    original_data[attr.key] = old_value
                    changed_data[attr.key] = new_value

        if changed_data: # Only log if there are actual changes
            audit_entry = AuditLog(
                table_name=cls.__tablename__,
                record_id=str(target.id),
                action="UPDATE",
                old_values=json.dumps(original_data, default=str),
                new_values=json.dumps(changed_data, default=str),
                changed_by=get_current_user_id(),
            )
            session.add(audit_entry)

    @classmethod
    def _audit_before_delete(cls, mapper: Any, connection: Any, target: _T) -> None:
        """Event listener for 'before_delete'."""
        session = Session(bind=connection)
        old_values = {c.name: getattr(target, c.name) for c in target.__table__.columns}
        audit_entry = AuditLog(
            table_name=cls.__tablename__,
            record_id=str(target.id),
            action="DELETE",
            old_values=json.dumps(old_values, default=str),
            new_values=None,
            changed_by=get_current_user_id(),
        )
        session.add(audit_entry)
