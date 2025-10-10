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
        self.database_name = os.environ.get("MONGO_DB", "financial_agent")
        
        # Gemini API configuration
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "your-api-key")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Configure Gemini SDK
        genai.configure(api_key=self.gemini_api_key)

# ------------------------------------------------------------------------------
# 3. Pydantic Models for API Data Structure
# ------------------------------------------------------------------------------
class QueryRequest(BaseModel):
    """Model for incoming financial queries"""
    query: str

class QueryResponse(BaseModel):
    """Model for outgoing AI responses"""
    answer: str

class FinancialQuery(BaseModel):
    """Extended model for financial queries from users"""
    question: str
    context: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None  # {"start": "2024-01-01", "end": "2024-12-31"}
    transaction_type: Optional[str] = None  # "all", "income", "expense", "mpesa"

class AIInsightResponse(BaseModel):
    """Extended model for AI insight responses"""
    question: str
    answer: str
    confidence: float
    data_sources: List[str]
    timestamp: str
    suggestions: Optional[List[str]] = None

# ------------------------------------------------------------------------------
# 4. Core RAG Service Class
# ------------------------------------------------------------------------------
class FinancialRAGService:
    """
    Retrieval-Augmented Generation Service for Financial Insights
    
    This service combines:
    1. Data retrieval from MongoDB (transactions, invoices, etc.)
    2. AI generation using Google Gemini SDK
    """
    
    def __init__(self, config: AIInsightsConfig):
        self.config = config
        self.client = MongoClient(config.mongo_uri)
        self.db = self.client[config.database_name]
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(config.gemini_model)
        
        logger.info(f"Initialized FinancialRAGService with database: {config.database_name}")

    # --------------------------------------------------------------------------
    # 4. Retrieval Logic (The "R" in RAG)
    # --------------------------------------------------------------------------
    
    def retrieve_financial_context(self, query: str) -> str:
        """
        Retrieve relevant financial data from MongoDB based on the user's query.
        This function accesses the 'analytics_cache' collection and other financial data.
        """
        try:
            context_parts = []
            
            # Skip analytics_cache for now and go directly to transactions/invoices
            logger.info("Retrieving financial context from database...")
            
            # Access analytics_cache collection for key metrics
            analytics_cache = self.db.analytics_cache
            
            # Get recent revenue data (last 2 months)
            recent_months = []
            for i in range(2):
                month_start = datetime.now().replace(day=1) - timedelta(days=i*30)
                month_key = month_start.strftime("%Y-%m")
                recent_months.append(month_key)
            
            # Fetch revenue data
            revenue_docs = list(analytics_cache.find({
                "metric_type": "revenue_monthly",
                "period": {"$in": recent_months}
            }))
            
            if revenue_docs:
                context_parts.append("Recent Revenue Data:")
                for doc in revenue_docs:
                    period = doc.get("period", "Unknown")
                    amount = doc.get("value", 0)
                    context_parts.append(f"- Revenue for {period}: {amount:,.2f} KES")
            
            # Get expense categories
            expense_docs = list(analytics_cache.find({
                "metric_type": "expense_categories",
                "period": datetime.now().strftime("%Y-%m")
            }))
            
            if expense_docs:
                context_parts.append("\nTop Expense Categories:")
                for doc in expense_docs:
                    category = doc.get("category", "Unknown")
                    amount = doc.get("value", 0)
                    context_parts.append(f"- {category}: {amount:,.2f} KES")
            
            # Get transaction summary (skip analytics cache and go directly to transactions)
            logger.info("Looking for recent transactions...")
            recent_transactions = list(self.db.transactions.find({
                "request_timestamp": {"$gte": datetime.now() - timedelta(days=30)}
            }).limit(50))
            logger.info(f"Found {len(recent_transactions)} recent transactions")
            
            if recent_transactions:
                    total_amount = sum(t.get("amount", 0) for t in recent_transactions)
                    completed_amount = sum(t.get("amount", 0) for t in recent_transactions if t.get("status") == "completed")
                    context_parts.append(f"Recent Transactions (Last 30 days):")
                    context_parts.append(f"- Total transactions: {len(recent_transactions)}")
                    context_parts.append(f"- Total amount: {total_amount:,.2f} KES")
                    context_parts.append(f"- Completed amount: {completed_amount:,.2f} KES")
                    
                    # Group by gateway (payment method)
                    mpesa_count = len([t for t in recent_transactions if t.get("gateway") == "mpesa"])
                    if mpesa_count > 0:
                        context_parts.append(f"- M-Pesa transactions: {mpesa_count}")
                        
                    # Add invoice data
                    recent_invoices = list(self.db.invoices.find({
                        "date_issued": {"$gte": datetime.now() - timedelta(days=30)}
                    }).limit(20))
                    
                    if recent_invoices:
                        invoice_total = sum(inv.get("total_amount", 0) for inv in recent_invoices)
                        paid_invoices = len([inv for inv in recent_invoices if inv.get("status") == "paid"])
                        pending_invoices = len([inv for inv in recent_invoices if inv.get("status") in ["sent", "overdue"]])
                        
                        context_parts.append(f"\nRecent Invoices (Last 30 days):")
                        context_parts.append(f"- Total invoices: {len(recent_invoices)}")
                        context_parts.append(f"- Total invoice value: {invoice_total:,.2f} KES")
                        context_parts.append(f"- Paid invoices: {paid_invoices}")
                        context_parts.append(f"- Pending invoices: {pending_invoices}")
            
            # Join all context parts
            if context_parts:
                return "Financial Context:\n" + "\n".join(context_parts)
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error retrieving financial context: {str(e)}")
            return ""
    
    def retrieve_transaction_data(self, query: FinancialQuery) -> Dict[str, Any]:
        """
        Enhanced retrieval function for structured transaction data
        """
        try:
            # Build MongoDB query based on user's request
            mongo_query = {}
            
            # Date range filtering
            if query.date_range:
                date_filter = {}
                if query.date_range.get("start"):
                    date_filter["$gte"] = datetime.fromisoformat(query.date_range["start"])
                if query.date_range.get("end"):
                    date_filter["$lte"] = datetime.fromisoformat(query.date_range["end"])
                if date_filter:
                    mongo_query["timestamp"] = date_filter
            
            # Transaction type filtering
            if query.transaction_type and query.transaction_type != "all":
                if query.transaction_type == "mpesa":
                    mongo_query["payment_method"] = "mpesa"
                elif query.transaction_type == "income":
                    mongo_query["type"] = "credit"
                elif query.transaction_type == "expense":
                    mongo_query["type"] = "debit"
            
            # Retrieve transactions
            transactions = list(self.db.transactions.find(mongo_query).limit(100))
            
            # Retrieve invoices
            invoices = list(self.db.invoices.find(mongo_query).limit(50))
            
            # Calculate summary statistics
            total_transactions = len(transactions)
            total_amount = sum(t.get("amount", 0) for t in transactions)
            
            # Prepare structured data for AI
            retrieved_data = {
                "transactions": transactions,
                "invoices": invoices,
                "summary": {
                    "total_transactions": total_transactions,
                    "total_amount": total_amount,
                    "date_range": query.date_range,
                    "transaction_type": query.transaction_type
                },
                "data_sources": ["transactions", "invoices"]
            }
            
            logger.info(f"Retrieved {total_transactions} transactions and {len(invoices)} invoices")
            return retrieved_data
            
        except Exception as e:
            logger.error(f"Error retrieving transaction data: {str(e)}")
            return {"error": str(e), "data_sources": []}

    # --------------------------------------------------------------------------
    # 5. Generation Logic (The "G" in RAG)
    # --------------------------------------------------------------------------
    
    def generate_insight(self, query: str, context: str) -> str:
        """
        Generate AI insights using the Gemini SDK based on retrieved context.
        This function creates a detailed prompt and uses the model to generate the final answer.
        """
        try:
            # Create detailed prompt template
            prompt_template = """
You are a helpful and professional financial assistant for Small and Medium Businesses in Kenya.
Your role is to provide accurate, actionable financial insights based ONLY on the provided context data.

IMPORTANT INSTRUCTIONS:
- Base your answer ONLY on the provided financial context below
- If the context doesn't contain enough information, clearly state this limitation
- Focus on actionable insights and recommendations for Kenyan SMBs
- Use Kenyan Shilling (KES) currency format
- Be professional, clear, and concise
- If you're uncertain about something, say so rather than guessing

FINANCIAL CONTEXT:
{context}

USER QUERY:
{query}

Please provide a comprehensive answer based on the available financial data above.
Include specific numbers and insights where possible.
If the context is insufficient, explain what additional data would be needed.
"""
            
            # Format the prompt with actual data
            formatted_prompt = prompt_template.format(
                context=context if context else "No financial data available in the system.",
                query=query
            )
            
            # Generate response using Gemini
            response = self.model.generate_content(formatted_prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return f"I apologize, but I encountered an error while analyzing your financial data: {str(e)}"
    
    def generate_financial_insight(self, query: FinancialQuery, retrieved_data: Dict[str, Any]) -> AIInsightResponse:
        """
        Enhanced generation function that returns structured AI insights
        """
        try:
            # Prepare the prompt for Gemini
            system_prompt = """
            You are a financial advisor AI assistant for a Kenyan fintech company. 
            You have access to transaction data, invoice data, and customer information.
            
            Your role is to:
            1. Analyze financial data and provide actionable insights
            2. Answer questions about spending patterns, revenue trends, and financial health
            3. Suggest improvements for financial management
            4. Explain complex financial concepts in simple terms
            5. Focus on Kenyan market context (KES currency, M-Pesa payments, etc.)
            
            Always be helpful, accurate, and professional. If you're uncertain about something,
            say so rather than guessing.
            """
            
            # Format the retrieved data for the prompt
            data_summary = self._format_data_for_prompt(retrieved_data)
            
            # Construct the full prompt
            full_prompt = f"""
            {system_prompt}
            
            User Question: {query.question}
            
            Available Financial Data:
            {data_summary}
            
            Please provide a comprehensive answer to the user's question based on the available data.
            Include specific numbers and insights where possible.
            """
            
            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)
            
            # Parse and structure the response
            ai_response = AIInsightResponse(
                question=query.question,
                answer=response.text,
                confidence=0.85,  # Could be calculated based on data quality
                data_sources=retrieved_data.get("data_sources", []),
                timestamp=datetime.now().isoformat(),
                suggestions=self._extract_suggestions(response.text)
            )
            
            logger.info(f"Generated AI insight for question: {query.question[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI insight: {str(e)}")
            # Return a fallback response
            return AIInsightResponse(
                question=query.question,
                answer=f"I apologize, but I encountered an error while analyzing your financial data: {str(e)}",
                confidence=0.0,
                data_sources=[],
                timestamp=datetime.now().isoformat()
            )
    
    def _format_data_for_prompt(self, data: Dict[str, Any]) -> str:
        """
        Format retrieved data into a readable format for the AI prompt
        """
        if "error" in data:
            return f"Error retrieving data: {data['error']}"
        
        summary = data.get("summary", {})
        transactions = data.get("transactions", [])
        
        formatted = f"""
        Summary:
        - Total Transactions: {summary.get('total_transactions', 0)}
        - Total Amount: KES {summary.get('total_amount', 0):,.2f}
        - Date Range: {summary.get('date_range', 'All time')}
        - Transaction Type: {summary.get('transaction_type', 'All types')}
        
        Recent Transactions (sample):
        """
        
        # Add sample transactions (first 5)
        for i, txn in enumerate(transactions[:5]):
            formatted += f"""
        {i+1}. Amount: KES {txn.get('amount', 0):,.2f} | Type: {txn.get('type', 'Unknown')} | Method: {txn.get('payment_method', 'Unknown')}
        """
        
        if len(transactions) > 5:
            formatted += f"\n... and {len(transactions) - 5} more transactions"
        
        return formatted
    
    def _extract_suggestions(self, ai_response: str) -> List[str]:
        """
        Extract actionable suggestions from AI response
        """
        # Simple extraction - in production, could use more sophisticated NLP
        suggestions = []
        lines = ai_response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'should', 'consider']):
                suggestions.append(line.strip())
        
        return suggestions[:3]  # Return top 3 suggestions

    # --------------------------------------------------------------------------
    # 6. Main Service Methods - Tying It All Together
    # --------------------------------------------------------------------------
    
    def ask_financial_question(self, request: QueryRequest) -> QueryResponse:
        """
        Main endpoint function that ties retrieval and generation together.
        This implements the complete RAG pipeline for the /ai/ask endpoint.
        """
        try:
            # Step 1: Retrieve financial context (RAG - Retrieval)
            context = self.retrieve_financial_context(request.query)
            
            # Step 2: Generate AI insights (RAG - Generation)
            answer = self.generate_insight(request.query, context)
            
            # Step 3: Create and return response
            response = QueryResponse(answer=answer)
            
            logger.info(f"Successfully processed query: {request.query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing financial question: {str(e)}")
            # Return error response
            return QueryResponse(
                answer=f"I apologize, but I encountered an error while processing your question: {str(e)}"
            )
    
    def get_financial_insight(self, query: FinancialQuery) -> AIInsightResponse:
        """
        Enhanced method that returns structured insights with additional metadata
        """
        logger.info(f"Processing financial query: {query.question}")
        
        # Step 1: Retrieve relevant data (RAG - Retrieval)
        retrieved_data = self.retrieve_transaction_data(query)
        
        # Step 2: Generate AI insights (RAG - Generation)
        insight = self.generate_financial_insight(query, retrieved_data)
        
        return insight
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the AI insights service
        """
        try:
            # Check database connection
            db_status = self.client.admin.command('ping')
            
            # Check Gemini API (simple test)
            test_response = self.model.generate_content("Hello, are you working?")
            
            return {
                "status": "healthy",
                "database": "connected",
                "gemini_api": "connected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# ------------------------------------------------------------------------------
# 7. Service Instance (Singleton)
# ------------------------------------------------------------------------------
_service_instance = None

def get_ai_insights_service() -> FinancialRAGService:
    """
    Get the singleton instance of the AI insights service
    """
    global _service_instance
    
    if _service_instance is None:
        config = AIInsightsConfig()
        _service_instance = FinancialRAGService(config)
    
    return _service_instance
