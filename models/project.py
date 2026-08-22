import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    DELAYED = "DELAYED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class GovernmentProject(Base):
    __tablename__ = "government_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    department = Column(String(150), nullable=False, index=True)
    project_type = Column(String(100), nullable=False, index=True)  # Road Widening, Metro Line, Drainage, Bridge
    
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ONGOING, nullable=False, index=True)
    progress = Column(Float, default=0.0, nullable=False)  # 0 to 100 percentage
    
    start_date = Column(Date, nullable=True)
    expected_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)

    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    geometry_wkt = Column(Text, nullable=True)

    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True, index=True)

    source = Column(String(150), default="Pune Municipal Corporation (PMC)", nullable=True)
    source_url = Column(String(500), nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    officer = relationship("Officer", back_populates="projects")
    warnings = relationship("Warning", back_populates="project")

    __table_args__ = (
        Index("idx_project_lat_lng", "latitude", "longitude"),
        Index("idx_project_status_dept", "status", "department"),
    )
