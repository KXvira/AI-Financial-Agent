# AI Insights Service Package
"""
AI-Powered Financial Insights Service using RAG and Gemini SDK

This package provides conversational AI capabilities for financial analysis,
combining retrieval from MongoDB with generation using Google's Gemini SDK.

Features:
- Natural language financial queries
- RAG (Retrieval-Augmented Generation) architecture
- MongoDB data retrieval and analysis
- Google Gemini SDK for AI generation
- FastAPI integration for web services

Team Integration:
- Frontend integration ready (Diana)
- Uses existing MongoDB schema (Kevo)
- Processes transaction/invoice data (Muchamo/Biggie)
"""

__version__ = "1.0.0"
__author__ = "AI Financial Agent Team"

# Export main classes for easy importing
from .service import (
    FinancialRAGService,
    AIInsightsConfig,
    QueryRequest,
    QueryResponse,
    FinancialQuery,
    AIInsightResponse,
    get_ai_insights_service
)

# Note: router import moved to avoid circular dependency issues

__all__ = [
    "FinancialRAGService",
    "AIInsightsConfig", 
    "QueryRequest",
    "QueryResponse",
    "FinancialQuery",
    "AIInsightResponse",
    "get_ai_insights_service"
]
