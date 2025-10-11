"""
Dashboard Router - API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
import logging

from dashboard.models import DashboardData, DashboardStats
from dashboard.service import DashboardService
from auth.middleware import get_current_user
from auth.models import User
from database.mongodb import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardData,
    summary="Get dashboard statistics",
    description="Get computed dashboard statistics with real data from database"
)
async def get_dashboard_statistics(
    period_days: int = Query(
        30, 
        ge=1, 
        le=365,
        description="Number of days for statistics period"
    )
) -> DashboardData:
    """
    Get complete dashboard statistics
    
    Returns:
    - Total invoices with percentage change
    - Payments received with percentage change
    - Outstanding balance with percentage change
    - Daily cash flow with percentage change
    - Recent payments list
    - Recent transactions list
    
    All percentage changes are computed by comparing current period
    with the previous period of same length.
    
    Note: Currently returns aggregated data across all users.
    User-specific filtering will be added once authentication is fixed.
    """
    try:
        db_instance = Database.get_instance()
        db = db_instance.db
        
        dashboard_service = DashboardService(db)
        # For now, pass None as user_id to get all data
        dashboard_data = await dashboard_service.get_dashboard_stats(
            user_id=None,
            period_days=period_days
        )
        
        logger.info(f"Dashboard stats retrieved for all users (period: {period_days} days)")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )


@router.get(
    "/stats/summary",
    response_model=DashboardStats,
    summary="Get dashboard statistics summary",
    description="Get only the statistics summary without recent transactions"
)
async def get_dashboard_stats_summary(
    period_days: int = Query(
        30,
        ge=1,
        le=365,
        description="Number of days for statistics period"
    ),
    current_user: User = Depends(get_current_user)
) -> DashboardStats:
    """
    Get dashboard statistics summary only
    
    Lighter endpoint that returns only the statistics
    without recent payments and transactions lists.
    """
    try:
        db_instance = Database.get_instance()
        db = db_instance.db
        
        dashboard_service = DashboardService(db)
        dashboard_data = await dashboard_service.get_dashboard_stats(
            user_id=current_user.id,
            period_days=period_days
        )
        
        return dashboard_data.statistics
        
    except Exception as e:
        logger.error(f"Dashboard stats summary error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics summary"
        )


@router.get(
    "/health",
    summary="Dashboard health check"
)
async def dashboard_health():
    """Health check endpoint for dashboard service"""
    return {
        "status": "healthy",
        "service": "Dashboard API",
        "version": "1.0.0"
    }
