from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    department = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    office = Column(String(255), nullable=True)
    public_contact = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="officer_profile")
    projects = relationship("GovernmentProject", back_populates="officer")
