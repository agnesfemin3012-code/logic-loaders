from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class OfficerBase(BaseModel):
    employee_id: str
    department: str
    designation: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    office: Optional[str] = None
    public_contact: Optional[str] = None


class OfficerCreate(OfficerBase):
    user_id: Optional[int] = None


class OfficerUpdate(BaseModel):
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    office: Optional[str] = None
    public_contact: Optional[str] = None


class OfficerOut(OfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
