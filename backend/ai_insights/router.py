"""
FastAPI router for AI-powered financial insights
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from .service import (
    QueryRequest, 
    QueryResponse, 
    process_financial_query,
    health_check,
    validate_gemini_connection,
    validate_database_connection
)

logger = logging.getLogger("financial-agent.ai.insights.router")

# Create the router
router = APIRouter(prefix="/ai", tags=["AI Financial Insights"])

@router.post("/ask", response_model=QueryResponse)
async def ask_financial_question(request: QueryRequest) -> QueryResponse:
    """
    Ask a financial question and get AI-powered insights.
    
    This endpoint uses Retrieval-Augmented Generation (RAG) to:
    1. Retrieve relevant financial data from your database
    2. Generate insights using Google's Gemini AI
    
    Args:
        request: Query request containing your financial question
        
    Returns:
        AI-generated financial insights based on your business data
        
    Example:
        POST /ai/ask
        {
            "query": "What was my revenue trend for the last 3 months?"
        }
    """
    try:
        return await process_financial_query(request)
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process financial query"
        )

@router.get("/health", response_model=Dict[str, Any])
async def get_ai_health() -> Dict[str, Any]:
    """
    Check the health status of the AI insights service.
    
    Returns:
        Health status including database and Gemini API connectivity
    """
    try:
        return await health_check()
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform health check"
        )

@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """
    Get detailed status of AI service components.
    
    Returns:
        Detailed status of each service component
    """
    try:
        return {
            "ai_insights_service": "running",
            "database_status": "connected" if validate_database_connection() else "disconnected",
            "gemini_api_status": "connected" if validate_gemini_connection() else "disconnected",
            "supported_queries": [
                "Revenue trends and analysis",
                "Expense categorization and optimization",
                "Invoice and payment status summaries",
                "Cash flow analysis",
                "Business performance metrics",
                "Payment gateway statistics"
            ],
            "example_queries": [
                "What was my revenue for the last 3 months?",
                "Show me my top expense categories",
                "How many invoices are still pending payment?",
                "What's my average transaction amount?",
                "Which payment gateway performs best?"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get service status"
        )
