from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.precaution import TargetAudience, PrecautionPriority


class PrecautionBase(BaseModel):
    title: str
    description: str
    priority: PrecautionPriority = PrecautionPriority.MEDIUM
    action: str
    target_audience: TargetAudience = TargetAudience.CITIZEN


class PrecautionCreate(PrecautionBase):
    warning_id: int


class PrecautionOut(PrecautionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warning_id: int
