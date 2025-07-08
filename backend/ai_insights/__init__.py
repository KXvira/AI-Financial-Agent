"""
AI-powered financial insights package using RAG and Gemini SDK.

This package provides conversational AI capabilities for financial queries,
combining data retrieval from MongoDB with Google's Gemini AI for insights generation.
"""

from .service import (
    QueryRequest,
    QueryResponse,
    process_financial_query,
    health_check,
    validate_gemini_connection,
    validate_database_connection
)

from .router import router

__all__ = [
    "QueryRequest",
    "QueryResponse", 
    "process_financial_query",
    "health_check",
    "validate_gemini_connection",
    "validate_database_connection",
    "router"
]
