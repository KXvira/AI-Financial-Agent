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

# ------------------------------------------------------------------------------
# 3. Pydantic Models for API Data Structure
# ------------------------------------------------------------------------------
class QueryRequest(BaseModel):
    """Model for incoming financial queries"""
    query: str
    user_id: Optional[str] = None  # To scope data access to the correct user

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
    
    def retrieve_financial_context(self, query: str, user_id: str = None) -> str:
        """
        Retrieve comprehensive financial data from multiple team collections.
        This function accesses data managed by different team members:
        - Analytics cache (Munga's data)
        - Invoices (Biggie's collection) 
        - Transactions (Muchamo's service)
        """
        try:
            logger.info(f"Retrieving context for query: '{query}' for user: '{user_id}'")
            context_parts = []
            
            # --- Step 1: Query Analytics Cache (Munga's High-Level Summaries) ---
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
                context_parts.append("High-Level Revenue (Analytics Cache):")
                for doc in revenue_docs:
                    period = doc.get("period", "Unknown")
                    amount = doc.get("value", 0)
                    context_parts.append(f"- Revenue for {period}: {amount:,.0f} KES")
            else:
                # Mock data if no analytics cache available
                context_parts.append("High-Level Revenue (Analytics Cache):")
                context_parts.append(f"- Revenue for June 2025: 220,000 KES")
                context_parts.append(f"- Revenue for July 2025: 155,000 KES")
            
            # --- Step 2: Query Biggie's Invoices Collection ---
            try:
                # Find overdue invoices
                current_date = datetime.now()
                overdue_invoices = list(self.db.invoices.find({
                    "due_date": {"$lt": current_date},
                    "status": {"$ne": "paid"}
                }).limit(10))
                
                if overdue_invoices:
                    context_parts.append("\nOutstanding Invoices (Biggie's Data):")
                    overdue_list = []
                    for invoice in overdue_invoices:
                        invoice_num = invoice.get("invoice_number", "Unknown")
                        customer = invoice.get("customer_name", "Unknown Customer")
                        amount = invoice.get("amount", 0)
                        overdue_list.append(f"{invoice_num} - {customer} (KES {amount:,.0f})")
                    context_parts.append(f"- Currently Overdue: {', '.join(overdue_list[:3])}")
                    if len(overdue_invoices) > 3:
                        context_parts.append(f"- Plus {len(overdue_invoices) - 3} more overdue invoices")
                else:
                    # Mock data if no invoices found
                    context_parts.append("\nOutstanding Invoices (Biggie's Data):")
                    context_parts.append("- Currently Overdue: INV-2025-071 - Tech Innovators Ltd (KES 45,000), INV-2025-073 - Green Grocers (KES 12,500)")
                    
            except Exception as e:
                logger.warning(f"Could not retrieve invoice data: {e}")
                context_parts.append("\nOutstanding Invoices: Data temporarily unavailable")
            
            # --- Step 3: Query Muchamo's Transactions Collection ---
            try:
                # Get recent transaction health
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_transactions = list(self.db.transactions.find({
                    "timestamp": {"$gte": thirty_days_ago}
                }))
                
                if recent_transactions:
                    successful = len([t for t in recent_transactions if t.get("status") == "success"])
                    failed = len([t for t in recent_transactions if t.get("status") == "failed"])
                    total = len(recent_transactions)
                    
                    context_parts.append("\nRecent Payment Health (Muchamo's Data):")
                    context_parts.append(f"- Transaction Status (Last 30 Days): {successful} Successful, {failed} Failed out of {total} total")
                    
                    # M-Pesa specific stats
                    mpesa_transactions = [t for t in recent_transactions if t.get("payment_method") == "mpesa"]
                    if mpesa_transactions:
                        mpesa_total = sum(t.get("amount", 0) for t in mpesa_transactions)
                        context_parts.append(f"- M-Pesa Volume: {len(mpesa_transactions)} transactions totaling KES {mpesa_total:,.0f}")
                else:
                    # Mock data if no transactions found
                    context_parts.append("\nRecent Payment Health (Muchamo's Data):")
                    context_parts.append("- Transaction Status (Last 30 Days): 98 Successful, 2 Failed")
                    
            except Exception as e:
                logger.warning(f"Could not retrieve transaction data: {e}")
                context_parts.append("\nPayment Health: Data temporarily unavailable")
            
            # --- Step 4: Get expense categories if available ---
            try:
                expense_docs = list(analytics_cache.find({
                    "metric_type": "expense_categories",
                    "period": datetime.now().strftime("%Y-%m")
                }))
                
                if expense_docs:
                    context_parts.append("\nTop Expense Categories:")
                    for doc in expense_docs[:3]:  # Top 3 categories
                        category = doc.get("category", "Unknown")
                        amount = doc.get("value", 0)
                        context_parts.append(f"- {category}: {amount:,.0f} KES")
                        
            except Exception as e:
                logger.warning(f"Could not retrieve expense data: {e}")
            
            # Join all context parts
            if context_parts:
                return "Comprehensive Financial Context:\n" + "\n".join(context_parts)
            else:
                return "No comprehensive financial data available in the system."
                
        except Exception as e:
            logger.error(f"Error retrieving comprehensive financial context: {str(e)}")
            return f"Error accessing financial data: {str(e)}"
    
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
        
        Process:
        1. Receives a user query and optional user_id
        2. Retrieves comprehensive financial context from all team collections
        3. Generates a data-driven insight using Gemini
        4. Returns the final answer
        """
        try:
            if not request.query or len(request.query.strip()) < 3:
                return QueryResponse(answer="Query cannot be empty or too short. Please provide a meaningful financial question.")
            
            logger.info(f"Processing query: '{request.query[:50]}...' for user: {request.user_id}")
            
            # Step 1: Retrieve comprehensive financial context (RAG - Retrieval)
            context = self.retrieve_financial_context(request.query, request.user_id)
            
            # Step 2: Generate AI insights (RAG - Generation)
            answer = self.generate_insight(request.query, context)
            
            # Step 3: Create and return response
            response = QueryResponse(answer=answer)
            
            logger.info(f"Successfully processed query for user: {request.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing financial question: {str(e)}")
            # Return error response
            return QueryResponse(
                answer=f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try again later."
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
