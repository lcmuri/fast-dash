# domains/crm/customer/entities/customer.py
from datetime import datetime
from typing import Optional
from enum import Enum

class CustomerType(str, Enum):
    WALK_IN = "walk_in"
    TELESALES = "telesales"
    WHOLESALE = "wholesale"
    RETAIL = "retail"

class CustomerEntity:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        phone: str = "",
        email: Optional[str] = None,
        customer_type: CustomerType = CustomerType.WALK_IN,
        company_name: Optional[str] = None,
        address: Optional[str] = None,
        is_active: bool = True,
        last_visit: Optional[datetime] = None,
        total_visits: int = 0,
        total_spent: float = 0.0,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.customer_type = customer_type
        self.company_name = company_name
        self.address = address
        self.is_active = is_active
        self.last_visit = last_visit
        self.total_visits = total_visits
        self.total_spent = total_spent
        self.created_at = created_at or datetime.now()