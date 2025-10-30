from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class PeriodType(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"

class BudgetTemplate(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Budget category")
    subcategory: Optional[str] = Field(None, description="Budget subcategory")
    amount: float = Field(..., gt=0, description="Template budget amount")
    period_type: PeriodType = Field(..., description="Budget period type")
    alert_threshold: float = Field(80.0, ge=0, le=100, description="Alert threshold percentage")
    is_default: bool = Field(False, description="Whether this is a system default template")
    created_by: Optional[str] = Field(None, description="User who created the template")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Monthly Marketing Budget",
                "description": "Standard marketing budget for digital campaigns",
                "category": "Marketing",
                "subcategory": "Digital Ads",
                "amount": 5000.0,
                "period_type": "monthly",
                "alert_threshold": 80.0
            }
        }

class BudgetTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    amount: float = Field(..., gt=0)
    period_type: PeriodType
    alert_threshold: float = Field(80.0, ge=0, le=100)

class BudgetTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    period_type: Optional[PeriodType] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)
