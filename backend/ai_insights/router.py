# ==============================================================================
# AI Insights FastAPI Router
# ==============================================================================
#
# This module defines the FastAPI routes for the AI-powered financial insights service.
# It provides endpoints for asking financial questions and getting AI-generated insights.

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from .service import (
    get_ai_insights_service, 
    FinancialRAGService, 
    FinancialQuery, 
    AIInsightResponse,
    QueryRequest,
    QueryResponse
)

# Setup logging
logger = logging.getLogger("financial-agent.ai.router")

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------
router = APIRouter(
    prefix="/ai",
    tags=["AI Insights"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# ------------------------------------------------------------------------------
# Dependency Injection
# ------------------------------------------------------------------------------
def get_service() -> FinancialRAGService:
    """Dependency to get the AI insights service"""
    return get_ai_insights_service()

# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@router.post("/ask", response_model=QueryResponse)
async def ask_financial_question(
    request: QueryRequest,
    service: FinancialRAGService = Depends(get_service)
) -> QueryResponse:
    """
    Ask a financial question and get AI-powered insights
    
    This endpoint expects a QueryRequest and returns a QueryResponse.
    It follows the exact RAG architecture specified in the requirements:
    1. Retrieves financial context from MongoDB
    2. Generates insights using Google Gemini SDK
    
    Example request:
    {
        "query": "What are my spending patterns this month?"
    }
    """
    try:
        logger.info(f"Received financial query: {request.query[:100]}...")
        
        # Validate the query
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 3 characters long"
            )
        
        # Process the query using RAG architecture
        response = service.ask_financial_question(request)
        
        logger.info("Successfully generated financial insight")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing financial query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing your question: {str(e)}"
        )

@router.post("/ask-advanced", response_model=AIInsightResponse)
async def ask_advanced_financial_question(
    query: FinancialQuery,
    service: FinancialRAGService = Depends(get_service)
) -> AIInsightResponse:
    """
    Ask a financial question and get AI-powered insights
    
    This endpoint accepts a financial question and returns AI-generated insights
    based on the user's financial data from the MongoDB database.
    
    Example questions:
    - "What are my spending patterns this month?"
    - "How much revenue did we generate from M-Pesa payments?"
    - "Which customers have outstanding invoices?"
    - "Show me a summary of my financial health"
    """
    try:
        logger.info(f"Received financial query: {query.question[:100]}...")
        
        # Validate the query
        if not query.question or len(query.question.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Question must be at least 3 characters long"
            )
        
        # Get AI insights
        insight = service.get_financial_insight(query)
        
        logger.info("Successfully generated financial insight")
        return insight
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing financial query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing your question: {str(e)}"
        )

@router.get("/health")
async def health_check(
    service: FinancialRAGService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Check the health of the AI insights service
    
    Returns the status of database connections, AI model availability,
    and other system health indicators.
    """
    try:
        health_status = service.health_check()
        
        if health_status["status"] == "healthy":
            return JSONResponse(
                status_code=200,
                content=health_status
            )
        else:
            return JSONResponse(
                status_code=503,
                content=health_status
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "error"
            }
        )

@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """
    Get basic service status and configuration info
    """
    try:
        import os
        
        status = {
            "service": "AI Financial Insights",
            "version": "1.0.0",
            "status": "running",
            "features": [
                "Financial Q&A",
                "Transaction Analysis", 
                "Customer Insights",
                "Revenue Analytics",
                "M-Pesa Integration"
            ],
            "ai_model": os.environ.get("GEMINI_MODEL", "gemini-1.5-pro"),
            "database": os.environ.get("DATABASE_NAME", "kenya_fintech_suite")
        }
        
        return JSONResponse(
            status_code=200,
            content=status
        )
        
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to get service status"
        )

# ------------------------------------------------------------------------------
# Example Usage Endpoint (for testing and demonstration)
# ------------------------------------------------------------------------------

@router.get("/examples")
async def get_example_queries() -> Dict[str, Any]:
    """
    Get example queries that can be asked to the AI insights service
    """
    examples = {
        "transaction_analysis": [
            "What are my spending patterns this month?",
            "How much did I spend on groceries last quarter?",
            "Show me my largest transactions this year"
        ],
        "revenue_insights": [
            "What's my total revenue this month?",
            "How much revenue came from M-Pesa payments?",
            "Compare this month's revenue to last month"
        ],
        "customer_analytics": [
            "Which customers have outstanding invoices?",
            "Who are my top spending customers?",
            "Show me customer payment patterns"
        ],
        "financial_health": [
            "Give me a summary of my financial health",
            "What are my main expense categories?",
            "How is my cash flow looking?"
        ],
        "forecasting": [
            "Predict my expenses for next month",
            "What's my expected revenue trend?",
            "Should I be concerned about any financial patterns?"
        ]
    }
    
    return {
        "message": "Here are example questions you can ask the AI insights service",
        "categories": examples,
        "usage_tip": "You can also specify date ranges and transaction types in your queries"
    }

# ------------------------------------------------------------------------------
# Data Summary Endpoint
# ------------------------------------------------------------------------------
@router.get("/data-summary")
async def get_data_summary(
    service: FinancialRAGService = Depends(get_ai_insights_service)
) -> Dict[str, Any]:
    """
    Get a summary of financial data from the database.
    
    Returns:
        Dict containing summary statistics for transactions, invoices, and revenue
    """
    try:
        # Get database instance
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database.mongodb import Database
        db = Database.get_instance()
        
        # Fetch data from database
        total_transactions = await db.transactions.count_documents({})
        total_invoices = await db.invoices.count_documents({})
        pending_invoices = await db.invoices.count_documents({"status": "sent"})
        
        # Count M-Pesa payments specifically (from payments collection)
        mpesa_transactions = await db.payments.count_documents({
            "payment_method": {"$regex": "mpesa", "$options": "i"}
        })
        
        # Calculate total revenue from completed transactions
        revenue_pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.transactions.aggregate(revenue_pipeline).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Calculate pending amount from pending invoices
        pending_pipeline = [
            {"$match": {"status": {"$in": ["sent", "overdue"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        pending_result = await db.invoices.aggregate(pending_pipeline).to_list(1)
        pending_amount = pending_result[0]["total"] if pending_result else 0
        
        return {
            "total_transactions": total_transactions,
            "total_invoices": total_invoices,
            "mpesa_transactions": mpesa_transactions,
            "pending_invoices": pending_invoices,
            "total_revenue": f"KES {total_revenue:,.2f}",
            "pending_amount": f"KES {pending_amount:,.2f}"
        }
        
    except Exception as e:
        logger.error(f"Error fetching data summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data summary: {str(e)}")
