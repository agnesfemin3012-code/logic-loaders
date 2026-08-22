import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkOrderStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"


class WorkOrderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    warning_id = Column(Integer, ForeignKey("warnings.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    priority = Column(Enum(WorkOrderPriority), default=WorkOrderPriority.MEDIUM, nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.OPEN, nullable=False, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Relationships
    asset = relationship("InfrastructureAsset", back_populates="work_orders")
    warning = relationship("Warning", back_populates="work_orders")
    assignee = relationship("User", back_populates="work_orders", foreign_keys=[assigned_to])

    __table_args__ = (
        Index("idx_work_order_status_prio", "status", "priority"),
    )
