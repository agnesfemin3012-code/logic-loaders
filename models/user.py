import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    ENGINEER = "ENGINEER"
    FIELD_TECHNICIAN = "FIELD_TECHNICIAN"
    ANALYST = "ANALYST"
    CITIZEN = "CITIZEN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    officer_profile = relationship("Officer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="assignee", foreign_keys="WorkOrder.assigned_to")
    audit_logs = relationship("AuditLog", back_populates="user")
