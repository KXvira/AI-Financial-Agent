"""
Budget Router - API endpoints for budget management
"""
import logging
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from datetime import date

from backend.models.budget import (
    Budget, BudgetCreate, BudgetUpdate, BudgetSummary,
    BudgetAnalytics, BudgetStatus, PeriodType
)
from backend.services.budget_service import BudgetService

logger = logging.getLogger("financial-agent.budget.router")

# Create router
router = APIRouter(prefix="/api/budgets", tags=["budgets"])

# Initialize service
budget_service = BudgetService()


@router.post("", response_model=Budget, status_code=201)
async def create_budget(budget_data: BudgetCreate):
    """
    Create a new budget
    
    Args:
        budget_data: Budget creation data
        
    Returns:
        Created budget
    """
    try:
        budget = await budget_service.create_budget(budget_data)
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating budget: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create budget")


@router.get("", response_model=List[Budget])
async def list_budgets(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[BudgetStatus] = Query(None, description="Filter by status"),
    period_type: Optional[PeriodType] = Query(None, description="Filter by period type"),
    active_only: bool = Query(False, description="Only return active budgets")
):
    """
    List budgets with optional filters
    
    Args:
        user_id: Filter by user ID
        category: Filter by category
        status: Filter by status
        period_type: Filter by period type
        active_only: Only return active budgets
        
    Returns:
        List of budgets
    """
    try:
        budgets = await budget_service.list_budgets(
            user_id=user_id,
            category=category,
            status=status,
            period_type=period_type,
            active_only=active_only
        )
        return budgets
    except Exception as e:
        logger.error(f"Error listing budgets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list budgets")


@router.get("/summary", response_model=BudgetSummary)
async def get_budget_summary(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get budget summary statistics
    
    Args:
        user_id: Optional user ID filter
        
    Returns:
        Budget summary
    """
    try:
        summary = await budget_service.get_budget_summary(user_id=user_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting budget summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get budget summary")


@router.get("/categories", response_model=List[str])
async def get_budget_categories(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get list of budget categories
    
    Args:
        user_id: Optional user ID filter
        
    Returns:
        List of category names
    """
    try:
        categories = await budget_service.get_categories(user_id=user_id)
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@router.get("/{budget_id}", response_model=Budget)
async def get_budget(
    budget_id: str = Path(..., description="Budget ID")
):
    """
    Get a budget by ID
    
    Args:
        budget_id: Budget ID
        
    Returns:
        Budget details
    """
    try:
        budget = await budget_service.get_budget(budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting budget: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get budget")


@router.put("/{budget_id}", response_model=Budget)
async def update_budget(
    budget_id: str = Path(..., description="Budget ID"),
    update_data: BudgetUpdate = None
):
    """
    Update a budget
    
    Args:
        budget_id: Budget ID
        update_data: Update data
        
    Returns:
        Updated budget
    """
    try:
        budget = await budget_service.update_budget(budget_id, update_data)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating budget: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update budget")


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: str = Path(..., description="Budget ID")
):
    """
    Delete a budget
    
    Args:
        budget_id: Budget ID
        
    Returns:
        No content
    """
    try:
        deleted = await budget_service.delete_budget(budget_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Budget not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting budget: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete budget")


@router.get("/{budget_id}/analytics", response_model=BudgetAnalytics)
async def get_budget_analytics(
    budget_id: str = Path(..., description="Budget ID")
):
    """
    Get detailed analytics for a budget
    
    Args:
        budget_id: Budget ID
        
    Returns:
        Budget analytics
    """
    try:
        analytics = await budget_service.get_budget_analytics(budget_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Budget not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting budget analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get budget analytics")


@router.post("/{budget_id}/recalculate", response_model=Budget)
async def recalculate_budget(
    budget_id: str = Path(..., description="Budget ID")
):
    """
    Recalculate actual spent from expenses
    
    Args:
        budget_id: Budget ID
        
    Returns:
        Updated budget
    """
    try:
        # Recalculate
        await budget_service._recalculate_budget_spent(budget_id)
        
        # Fetch updated budget
        budget = await budget_service.get_budget(budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        return budget
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating budget: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to recalculate budget")


logger.info("✅ Budget router initialized successfully")
