"""
Budget models for financial tracking and management
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class PeriodType(str, Enum):
    """Budget period types"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class BudgetStatus(str, Enum):
    """Budget status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    EXCEEDED = "exceeded"


class AlertLevel(str, Enum):
    """Alert levels for budget monitoring"""
    NONE = "none"
    WARNING = "warning"      # 50-79%
    CRITICAL = "critical"    # 80-99%
    EXCEEDED = "exceeded"    # 100%+


class BudgetCategory(BaseModel):
    """Budget category details"""
    name: str
    subcategory: Optional[str] = None


class BudgetCreate(BaseModel):
    """Schema for creating a new budget"""
    category: str = Field(..., description="Main budget category (e.g., 'Marketing', 'Salaries')")
    subcategory: Optional[str] = Field(None, description="Subcategory for more specific tracking")
    amount: float = Field(..., gt=0, description="Budgeted amount")
    period_type: PeriodType = Field(default=PeriodType.MONTHLY, description="Budget period type")
    start_date: date = Field(..., description="Budget start date")
    end_date: date = Field(..., description="Budget end date")
    alert_threshold: float = Field(default=80.0, ge=0, le=100, description="Alert threshold percentage (0-100)")
    description: Optional[str] = Field(None, description="Budget description or notes")
    user_id: Optional[str] = Field(None, description="User ID for multi-user systems")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('amount must be greater than 0')
        return round(v, 2)


class BudgetUpdate(BaseModel):
    """Schema for updating an existing budget"""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    period_type: Optional[PeriodType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    status: Optional[BudgetStatus] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('amount must be greater than 0')
        if v is not None:
            return round(v, 2)
        return v


class Budget(BaseModel):
    """Complete budget model"""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    user_id: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    amount: float = Field(..., gt=0, description="Budgeted amount")
    actual_spent: float = Field(default=0.0, ge=0, description="Actual amount spent")
    period_type: PeriodType = PeriodType.MONTHLY
    start_date: date
    end_date: date
    alert_threshold: float = Field(default=80.0, ge=0, le=100)
    description: Optional[str] = None
    status: BudgetStatus = BudgetStatus.ACTIVE
    alert_level: AlertLevel = AlertLevel.NONE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage"""
        if self.amount <= 0:
            return 0.0
        return round((self.actual_spent / self.amount) * 100, 2)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining budget amount"""
        return round(max(0, self.amount - self.actual_spent), 2)
    
    @property
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded"""
        return self.actual_spent > self.amount
    
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in budget period"""
        today = date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    @property
    def is_active(self) -> bool:
        """Check if budget period is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == BudgetStatus.ACTIVE
    
    def update_alert_level(self) -> AlertLevel:
        """Update and return alert level based on utilization"""
        utilization = self.utilization_percentage
        
        if utilization >= 100:
            self.alert_level = AlertLevel.EXCEEDED
            self.status = BudgetStatus.EXCEEDED
        elif utilization >= self.alert_threshold:
            self.alert_level = AlertLevel.CRITICAL
        elif utilization >= 50:
            self.alert_level = AlertLevel.WARNING
        else:
            self.alert_level = AlertLevel.NONE
        
        return self.alert_level
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class BudgetSummary(BaseModel):
    """Summary of budget status"""
    total_budgets: int = 0
    total_budgeted: float = 0.0
    total_spent: float = 0.0
    total_remaining: float = 0.0
    average_utilization: float = 0.0
    budgets_exceeded: int = 0
    budgets_on_track: int = 0
    budgets_warning: int = 0
    budgets_critical: int = 0
    by_category: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    by_period: Dict[str, Dict[str, float]] = Field(default_factory=dict)


class BudgetAnalytics(BaseModel):
    """Detailed budget analytics"""
    budget_id: str
    category: str
    period_type: str
    utilization_percentage: float
    utilization_trend: str  # "increasing", "decreasing", "stable"
    spending_rate: float  # spending per day
    projected_end_balance: float
    days_until_exceeded: Optional[int] = None
    recommendation: str
    risk_level: str  # "low", "medium", "high"


class BudgetAlert(BaseModel):
    """Budget alert notification"""
    budget_id: str
    category: str
    alert_level: AlertLevel
    current_utilization: float
    amount_spent: float
    amount_remaining: float
    message: str
    triggered_at: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = False
