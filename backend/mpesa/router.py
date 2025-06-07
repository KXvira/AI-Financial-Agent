"""
M-Pesa API router endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import json

from .service import MpesaService

logger = logging.getLogger("financial-agent.mpesa.router")

router = APIRouter(prefix="/api/mpesa", tags=["mpesa"])

# Initialize M-Pesa service
mpesa_service = MpesaService()

@router.post("/stk-push")
async def stk_push(
    request: Dict[str, Any] = Body(...),
):
    """
    Initiate STK Push payment request
    """
    try:
        phone_number = request.get("phone_number")
        amount = request.get("amount")
        reference = request.get("reference")
        description = request.get("description", "Payment")
        
        if not phone_number or not amount or not reference:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        result = await mpesa_service.initiate_stk_push(
            phone_number=phone_number,
            amount=float(amount),
            reference=reference,
            description=description
        )
        
        return {
            "success": True,
            "message": "STK push initiated",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error initiating STK Push: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query-status")
async def query_transaction_status(
    request: Dict[str, Any] = Body(...),
):
    """
    Check status of an STK Push transaction
    """
    try:
        checkout_request_id = request.get("checkout_request_id")
        
        if not checkout_request_id:
            raise HTTPException(status_code=400, detail="Missing checkout_request_id")
        
        result = await mpesa_service.check_transaction_status(checkout_request_id)
        
        return {
            "success": True,
            "message": "Transaction status",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error checking transaction status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/callback")
async def mpesa_callback(
    request: Request,
):
    """
    Handle M-Pesa callback from Safaricom
    """
    try:
        # Get raw callback data
        callback_data = await request.json()
        
        result = await mpesa_service.process_callback(callback_data)
        
        # Return success response to Safaricom
        return {
            "ResultCode": 0,
            "ResultDesc": "Callback processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing M-Pesa callback: {str(e)}")
        # Still return success to Safaricom to prevent retries
        return {
            "ResultCode": 0,
            "ResultDesc": "Callback received"
        }
