"""
Expense Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExpenseData(BaseModel):
    """Individual expense record"""
    id: str
    date: str
    vendor: str
    amount: float
    category: str
    status: str
    receipt_number: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None


class ExpenseSummary(BaseModel):
    """Expense summary response"""
    totalExpenses: float
    totalReceipts: int
    monthlyTotal: float
    categorySummary: Dict[str, float]
    recentExpenses: List[ExpenseData]


class ExpenseStats(BaseModel):
    """Detailed expense statistics"""
    total_amount: float
    total_count: int
    by_category: Dict[str, float]
    by_payment_method: Dict[str, float]
    average_expense: float
    period_start: datetime
    period_end: datetime
