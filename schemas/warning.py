from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.warning import WarningSeverity, WarningStatus
from app.schemas.precaution import PrecautionOut


class WarningBase(BaseModel):
    asset_id: Optional[int] = None
    project_id: Optional[int] = None
    warning_type: str
    severity: WarningSeverity = WarningSeverity.MODERATE
    title: str
    description: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    trigger: str
    recommended_action: Optional[str] = None


class WarningCreate(WarningBase):
    pass


class WarningAcknowledge(BaseModel):
    notes: Optional[str] = None


class WarningOut(WarningBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: WarningStatus
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    precautions: List[PrecautionOut] = []
