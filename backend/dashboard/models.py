"""
Dashboard Statistics Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    """Main dashboard statistics"""
    total_invoices: float = Field(0.0, description="Total invoice amount")
    total_invoices_count: int = Field(0, description="Number of invoices")
    invoices_change_percent: float = Field(0.0, description="Percentage change from previous period")
    
    payments_received: float = Field(0.0, description="Total payments received")
    payments_count: int = Field(0, description="Number of payments")
    payments_change_percent: float = Field(0.0, description="Percentage change from previous period")
    
    outstanding_balance: float = Field(0.0, description="Outstanding balance")
    outstanding_change_percent: float = Field(0.0, description="Percentage change from previous period")
    
    daily_cash_flow: float = Field(0.0, description="Average daily cash flow")
    cash_flow_change_percent: float = Field(0.0, description="Percentage change from previous period")
    
    period_start: Optional[datetime] = Field(None, description="Period start date")
    period_end: Optional[datetime] = Field(None, description="Period end date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_invoices": 120000.0,
                "total_invoices_count": 15,
                "invoices_change_percent": 10.5,
                "payments_received": 95000.0,
                "payments_count": 12,
                "payments_change_percent": 15.2,
                "outstanding_balance": 25000.0,
                "outstanding_change_percent": -5.3,
                "daily_cash_flow": 1500.0,
                "cash_flow_change_percent": 2.1
            }
        }


class RecentPayment(BaseModel):
    """Recent payment information"""
    reference: str
    client: str
    amount: float
    currency: str = "KES"
    date: datetime
    status: str = "completed"


class RecentTransaction(BaseModel):
    """Recent transaction information"""
    id: str
    type: str  # invoice, payment, expense
    description: str
    amount: float
    currency: str = "KES"
    date: datetime
    status: str


class DashboardData(BaseModel):
    """Complete dashboard data"""
    statistics: DashboardStats
    recent_payments: List[RecentPayment] = []
    recent_transactions: List[RecentTransaction] = []
    total_expenses: float = 0.0
    expenses_change_percent: float = 0.0
