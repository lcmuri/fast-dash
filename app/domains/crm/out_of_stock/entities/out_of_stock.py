# domains/crm/out_of_stock/entities/out_of_stock.py
from datetime import datetime
from typing import Optional

class OutOfStockEntity:
    def __init__(
        self,
        id: Optional[int] = None,
        medicine_name: str = "",
        medicine_code: Optional[str] = None,
        customer_id: Optional[int] = None,
        requested_quantity: int = 1,
        urgency: str = "normal",  # low, normal, high, critical
        status: str = "pending",  # pending, ordered, fulfilled
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.medicine_name = medicine_name
        self.medicine_code = medicine_code
        self.customer_id = customer_id
        self.requested_quantity = requested_quantity
        self.urgency = urgency
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()