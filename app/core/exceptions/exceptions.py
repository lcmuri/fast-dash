# core/exceptions.py
from fastapi import status
from typing import Optional, Any, Dict, List

class AppException(Exception):
    """Base exception class for the application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class NotFoundException(AppException):
    """Raised when a requested resource is not found"""
    
    def __init__(
        self,
        entity_name: str,
        entity_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{entity_name} not found"
        if entity_id:
            message += f" with id {entity_id}"
            
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="not_found",
            details=details or {"entity": entity_name, "id": entity_id}
        )

class ValidationException(AppException):
    """Raised when data validation fails"""
    
    def __init__(
        self,
        message: str,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error",
            details={
                **(details or {}),
                "errors": errors or []
            }
        )

class BusinessRuleException(AppException):
    """Raised when a business rule is violated"""
    
    def __init__(
        self,
        rule_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="business_rule_violation",
            details={
                **(details or {}),
                "rule": rule_name
            }
        )

class RepositoryException(AppException):
    """Raised when a repository operation fails"""
    
    def __init__(
        self,
        operation: str,
        entity_name: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"Failed to {operation} {entity_name}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="repository_error",
            details={
                **(details or {}),
                "operation": operation,
                "entity": entity_name
            }
        )