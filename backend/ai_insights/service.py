# ==============================================================================
# AI-Powered Financial Insights Service using RAG and Gemini SDK
# ==============================================================================
#
# Objective:
# This script creates a new FastAPI service that provides AI-powered financial analysis.
# It uses a Retrieval-Augmented Generation (RAG) architecture.
# - The "Retrieval" step fetches relevant financial data from our MongoDB database.
# - The "Generation" step uses the Google Gemini SDK to interpret the data and answer user questions.
# This service will power the "Conversational AI for financial queries" feature.
#
# Team Integration:
# - This backend service will be called by Diana's frontend application.
# - It relies on the MongoDB database schema and infrastructure managed by Kevo.
# - It processes transaction and invoice data from Muchamo's and Biggie's services.

# ------------------------------------------------------------------------------
# 1. Imports and Setup
# ------------------------------------------------------------------------------
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# Setup logging
logger = logging.getLogger("financial-agent.ai.insights")

# ------------------------------------------------------------------------------
# 2. Configuration and Initialization
# ------------------------------------------------------------------------------
class AIInsightsConfig:
    """Configuration for AI Insights Service"""
    
    def __init__(self):
        # Database configuration
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = os.environ.get("DATABASE_NAME", "kenya_fintech_suite")
        
        # Gemini API configuration
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "your-api-key")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        
        # Configure Gemini SDK
        genai.configure(api_key=self.gemini_api_key)

# Initialize configuration
config = AIInsightsConfig()

# Initialize MongoDB connection
client = MongoClient(config.mongo_uri)
db = client[config.database_name]

# Initialize Gemini model
generation_config = {
    "temperature": 0.3,
    "max_output_tokens": 2048,
    "top_p": 0.95,
    "top_k": 40
}

model = genai.GenerativeModel(
    model_name=config.gemini_model,
    generation_config=generation_config
)

# ------------------------------------------------------------------------------
# 3. Pydantic Models for API Data Structure
# ------------------------------------------------------------------------------
class QueryRequest(BaseModel):
    """Request model for financial query"""
    query: str
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What was my revenue trend for the last 3 months?"
            }
        }

class QueryResponse(BaseModel):
    """Response model for financial insights"""
    answer: str
    context_used: Optional[str] = None
    confidence: Optional[str] = "high"
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Based on your financial data, your revenue has shown a positive trend over the last 3 months...",
                "context_used": "Financial data from May-July 2025",
                "confidence": "high"
            }
        }

# ------------------------------------------------------------------------------
# 4. Retrieval Logic (The "R" in RAG)
# ------------------------------------------------------------------------------
def retrieve_financial_context(query: str) -> str:
    """
    Retrieve relevant financial data from MongoDB based on the user's query.
    
    Args:
        query: User's financial question
        
    Returns:
        Formatted context string with relevant financial data
    """
    try:
        context_parts = []
        current_date = datetime.now()
        
        # Determine time range based on query keywords
        if "month" in query.lower() or "monthly" in query.lower():
            months_back = 3
            if "last" in query.lower():
                # Extract number if mentioned (e.g., "last 6 months")
                words = query.lower().split()
                for i, word in enumerate(words):
                    if word.isdigit() and i < len(words) - 1 and "month" in words[i + 1]:
                        months_back = int(word)
                        break
        else:
            months_back = 2  # Default to 2 months
            
        start_date = current_date - timedelta(days=months_back * 30)
        
        # 1. Retrieve transaction summary data
        transactions_collection = db.transactions
        transaction_pipeline = [
            {
                "$match": {
                    "request_timestamp": {"$gte": start_date},
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$request_timestamp"},
                        "month": {"$month": "$request_timestamp"}
                    },
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        transaction_data = list(transactions_collection.aggregate(transaction_pipeline))
        
        if transaction_data:
            context_parts.append("TRANSACTION SUMMARY:")
            for data in transaction_data:
                month_name = datetime(data["_id"]["year"], data["_id"]["month"], 1).strftime("%B %Y")
                context_parts.append(
                    f"- {month_name}: {data['transaction_count']} transactions, "
                    f"Total: {data['total_amount']:,.2f} KES, "
                    f"Average: {data['avg_amount']:,.2f} KES"
                )
        
        # 2. Retrieve invoice summary data
        invoices_collection = db.invoices
        invoice_pipeline = [
            {
                "$match": {
                    "date_issued": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_issued"},
                        "month": {"$month": "$date_issued"},
                        "status": "$status"
                    },
                    "total_amount": {"$sum": "$total"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        invoice_data = list(invoices_collection.aggregate(invoice_pipeline))
        
        if invoice_data:
            context_parts.append("\nINVOICE SUMMARY:")
            # Group by month
            monthly_invoices = {}
            for data in invoice_data:
                month_key = f"{data['_id']['year']}-{data['_id']['month']}"
                if month_key not in monthly_invoices:
                    monthly_invoices[month_key] = {"total": 0, "paid": 0, "pending": 0, "overdue": 0}
                
                monthly_invoices[month_key]["total"] += data["count"]
                monthly_invoices[month_key][data["_id"]["status"]] = data["count"]
            
            for month_key, data in monthly_invoices.items():
                year, month = month_key.split("-")
                month_name = datetime(int(year), int(month), 1).strftime("%B %Y")
                context_parts.append(
                    f"- {month_name}: {data['total']} invoices "
                    f"(Paid: {data.get('paid', 0)}, Pending: {data.get('pending', 0)}, Overdue: {data.get('overdue', 0)})"
                )
        
        # 3. Retrieve top expense categories (if available in analytics cache)
        analytics_collection = db.analytics_cache
        expense_data = analytics_collection.find_one(
            {"type": "expense_categories", "date": {"$gte": start_date}},
            sort=[("date", -1)]
        )
        
        if expense_data and "categories" in expense_data:
            context_parts.append("\nTOP EXPENSE CATEGORIES:")
            for category, amount in expense_data["categories"].items():
                context_parts.append(f"- {category}: {amount:,.2f} KES")
        
        # 4. Retrieve recent payment gateway statistics
        gateway_pipeline = [
            {
                "$match": {
                    "request_timestamp": {"$gte": start_date},
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": "$gateway",
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        gateway_data = list(transactions_collection.aggregate(gateway_pipeline))
        
        if gateway_data:
            context_parts.append("\nPAYMENT GATEWAY SUMMARY:")
            for data in gateway_data:
                context_parts.append(
                    f"- {data['_id'].upper()}: {data['count']} transactions, "
                    f"Total: {data['total_amount']:,.2f} KES"
                )
        
        # 5. Add current date context
        context_parts.append(f"\nDATA PERIOD: {start_date.strftime('%B %Y')} to {current_date.strftime('%B %Y')}")
        context_parts.append(f"CURRENT DATE: {current_date.strftime('%B %d, %Y')}")
        
        return "\n".join(context_parts) if context_parts else ""
        
    except Exception as e:
        logger.error(f"Error retrieving financial context: {str(e)}")
        return f"Error accessing financial data: {str(e)}"

# ------------------------------------------------------------------------------
# 5. Generation Logic (The "G" in RAG)
# ------------------------------------------------------------------------------
def generate_insight(query: str, context: str) -> str:
    """
    Generate AI-powered financial insights using Gemini SDK.
    
    Args:
        query: User's financial question
        context: Retrieved financial data context
        
    Returns:
        AI-generated financial insight
    """
    try:
        # Create detailed prompt template
        prompt_template = """You are a helpful and professional financial assistant specialized in Small and Medium Business (SMB) financial analysis in Kenya. You provide clear, actionable insights based on financial data.

IMPORTANT INSTRUCTIONS:
1. Base your answer ONLY on the provided financial context data
2. If the context doesn't contain relevant information, clearly state this limitation
3. Use Kenyan Shilling (KES) currency format in your responses
4. Provide specific, actionable recommendations when possible
5. Be concise but comprehensive in your analysis
6. Focus on practical business insights that help SMB owners make informed decisions

FINANCIAL CONTEXT DATA:
{context}

USER QUESTION:
{query}

Please provide a detailed financial analysis and answer based on the above context. If the context is insufficient to answer the question completely, explain what additional data would be helpful."""

        # Format the prompt with actual data
        formatted_prompt = prompt_template.format(context=context, query=query)
        
        # Generate response using Gemini
        response = model.generate_content(formatted_prompt)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating insight with Gemini: {str(e)}")
        return f"I apologize, but I'm unable to process your request at the moment due to a technical issue: {str(e)}. Please try again later or contact support if the problem persists."

# ------------------------------------------------------------------------------
# 6. FastAPI Endpoint to Tie It All Together
# ------------------------------------------------------------------------------
# Note: This would typically be integrated into the main FastAPI app
# For now, we'll define the endpoint function that can be imported

async def process_financial_query(request: QueryRequest) -> QueryResponse:
    """
    Process a financial query using RAG architecture.
    
    Args:
        request: Query request containing the user's question
        
    Returns:
        Query response with AI-generated insights
    """
    try:
        # Step 1: Retrieve relevant financial context
        logger.info(f"Processing query: {request.query}")
        context = retrieve_financial_context(request.query)
        
        # Step 2: Generate AI insights using retrieved context
        if context:
            answer = generate_insight(request.query, context)
            confidence = "high"
            context_summary = "Financial data from database"
        else:
            answer = "I don't have enough financial data to answer your question accurately. Please ensure your business has recorded transactions and invoices in the system."
            confidence = "low"
            context_summary = "No relevant data found"
        
        # Step 3: Return structured response
        return QueryResponse(
            answer=answer,
            context_used=context_summary,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error processing financial query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your query: {str(e)}"
        )

# ------------------------------------------------------------------------------
# 7. Additional Utility Functions
# ------------------------------------------------------------------------------
def validate_gemini_connection() -> bool:
    """Validate that Gemini API is properly configured"""
    try:
        test_response = model.generate_content("Test connection")
        return bool(test_response.text)
    except Exception as e:
        logger.error(f"Gemini API connection failed: {str(e)}")
        return False

def validate_database_connection() -> bool:
    """Validate that MongoDB connection is working"""
    try:
        # Ping the database
        client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Health check function for the service
async def health_check() -> Dict[str, Any]:
    """Check the health of all service dependencies"""
    return {
        "service": "AI Financial Insights",
        "status": "healthy",
        "database_connected": validate_database_connection(),
        "gemini_api_connected": validate_gemini_connection(),
        "timestamp": datetime.now().isoformat()
    }
