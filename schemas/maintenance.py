from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.maintenance import WorkOrderStatus, WorkOrderPriority


class WorkOrderBase(BaseModel):
    asset_id: int
    warning_id: Optional[int] = None
    assigned_to: Optional[int] = None
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    description: str
    due_date: Optional[datetime] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    assigned_to: Optional[int] = None
    priority: Optional[WorkOrderPriority] = None
    description: Optional[str] = None
    status: Optional[WorkOrderStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verification_notes: Optional[str] = None


class WorkOrderOut(WorkOrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: WorkOrderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
