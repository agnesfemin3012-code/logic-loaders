import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TargetAudience(str, enum.Enum):
    CITIZEN = "CITIZEN"
    OFFICER = "OFFICER"
    ENGINEER = "ENGINEER"
    FIELD_TECHNICIAN = "FIELD_TECHNICIAN"


class PrecautionPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    IMMEDIATE = "IMMEDIATE"


class Precaution(Base):
    __tablename__ = "precautions"

    id = Column(Integer, primary_key=True, index=True)
    warning_id = Column(Integer, ForeignKey("warnings.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(PrecautionPriority), default=PrecautionPriority.MEDIUM, nullable=False)
    action = Column(Text, nullable=False)
    target_audience = Column(Enum(TargetAudience), default=TargetAudience.CITIZEN, nullable=False, index=True)

    # Relationships
    warning = relationship("Warning", back_populates="precautions")
