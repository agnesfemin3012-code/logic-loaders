from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.project import ProjectStatus
from app.schemas.officer import OfficerOut
from app.schemas.warning import WarningOut


class ProjectBase(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    department: str
    project_type: str
    status: ProjectStatus = ProjectStatus.ONGOING
    progress: float = Field(0.0, ge=0.0, le=100.0)
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    latitude: float
    longitude: float
    officer_id: Optional[int] = None
    source: Optional[str] = "Pune Municipal Corporation (PMC)"
    source_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_updated: datetime
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectOut):
    officer: Optional[OfficerOut] = None
    warnings: List[WarningOut] = []
    nearby_assets_count: int = 0
