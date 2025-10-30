"""
Expense API Router
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import logging

from .models import ExpenseSummary, ExpenseStats
from .service import ExpenseService
from database.mongodb import get_database, Database

logger = logging.getLogger("financial-agent.expenses")

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def get_expense_service(db: Database = Depends(get_database)) -> ExpenseService:
    """Dependency to get expense service"""
    return ExpenseService(db)


@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(
    days: int = Query(365, ge=1, le=730, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=100, description="Number of recent expenses to return"),
    service: ExpenseService = Depends(get_expense_service)
):
    """
    Get expense summary from receipts
    
    Returns:
    - Total expenses across all time
    - Monthly total (current month)
    - Category breakdown
    - Recent expenses list
    
    **days**: Number of days to look back (default: 365)
    **limit**: Number of recent expenses to return (default: 10)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    logger.info(f"Fetching expense summary for {days} days, limit {limit}")
    
    return await service.get_expense_summary(
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@router.get("/stats", response_model=ExpenseStats)
async def get_expense_stats(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    service: ExpenseService = Depends(get_expense_service)
):
    """
    Get detailed expense statistics
    
    Returns detailed breakdown of expenses by category, payment method, etc.
    """
    # Parse dates
    start_dt = None
    end_dt = None
    
    if start_date:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if end_date:
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    return await service.get_expense_stats(
        start_date=start_dt,
        end_date=end_dt
    )
