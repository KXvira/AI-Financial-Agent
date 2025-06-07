"""
Reconciliation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List
import logging

from .service import ReconciliationService

logger = logging.getLogger("financial-agent.reconciliation.router")

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])

# Initialize reconciliation service
reconciliation_service = ReconciliationService()

@router.post("/reconcile")
async def reconcile_payment(
    payment_data: Dict[str, Any] = Body(...)
):
    """
    Reconcile a payment with pending invoices
    """
    try:
        result = await reconciliation_service.reconcile_payment(payment_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in reconciliation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue")
async def queue_for_reconciliation(
    payment_data: Dict[str, Any] = Body(...)
):
    """
    Queue a payment for reconciliation
    """
    try:
        result = await reconciliation_service.queue_for_reconciliation(payment_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in queue endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def process_batch():
    """
    Process batch reconciliation for unreconciled payments
    """
    try:
        result = await reconciliation_service.process_batch_reconciliation()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in batch endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
