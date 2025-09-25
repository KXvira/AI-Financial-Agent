# ==============================================================================
# fullstack_main.py
# AI-Powered Financial Insights Service (Full Stack Integration)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Imports and Setup
# ------------------------------------------------------------------------------
import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging
import json

# ------------------------------------------------------------------------------
# 2. Configuration and Initialization
# ------------------------------------------------------------------------------

# Load environment variables from a .env file for local development.
# Kevo will manage these securely in the production deployment.
load_dotenv()

# Configure the Gemini SDK using the API key.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "kenya_fintech_suite")

# Initialize MongoDB client
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

# Initialize the FastAPI application.
app = FastAPI(
    title="Kenya Fintech AI Assistant API - Full Stack",
    description="Full-stack AI-powered financial management system with web interface",
    version="1.0.0"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 3. Frontend Integration (CORS & Static Files)
# ------------------------------------------------------------------------------

# Step 3.1: Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 3.2: Create frontend directory and mount static files
# First, let's create a simple HTML frontend
frontend_dir = "frontend"
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

# We'll create the HTML file programmatically
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Financial Insights</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 0.5rem;
        }
        .user-message {
            background-color: #3b82f6;
            color: white;
            margin-left: 2rem;
        }
        .ai-message {
            background-color: #f3f4f6;
            color: #1f2937;
            margin-right: 2rem;
        }
        .typing {
            opacity: 0.7;
            font-style: italic;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-2">AI Financial Insights</h1>
            <p class="text-gray-600">Ask questions about your financial data</p>
        </header>

        <div class="max-w-4xl mx-auto">
            <!-- Financial Overview Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">Revenue</h3>
                    <p class="text-3xl font-bold text-green-600" id="revenue">KES 220,000</p>
                    <p class="text-sm text-gray-500">June 2025</p>
                </div>
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">Overdue Invoices</h3>
                    <p class="text-3xl font-bold text-red-600" id="overdue">KES 57,500</p>
                    <p class="text-sm text-gray-500">2 invoices</p>
                </div>
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">Payment Success</h3>
                    <p class="text-3xl font-bold text-blue-600" id="success">98%</p>
                    <p class="text-sm text-gray-500">Last 30 days</p>
                </div>
            </div>

            <!-- Chat Interface -->
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="bg-gray-800 text-white p-4">
                    <h2 class="text-xl font-semibold">AI Financial Assistant</h2>
                    <p class="text-sm text-gray-300">Ask questions about your financial data</p>
                </div>
                
                <div class="chat-container p-4" id="chatContainer">
                    <div class="ai-message message">
                        <strong>AI Assistant:</strong> Hello! I'm your AI financial assistant. I can help you analyze your financial data, check invoice status, review payment trends, and provide insights. What would you like to know?
                    </div>
                </div>

                <div class="border-t p-4">
                    <div class="flex gap-2">
                        <input
                            type="text"
                            id="queryInput"
                            placeholder="Ask about your finances..."
                            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            onclick="sendQuery()"
                            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>

            <!-- Quick Questions -->
            <div class="mt-8">
                <h3 class="text-lg font-semibold mb-4">Quick Questions</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button onclick="askQuickQuestion('What is my current financial status?')" 
                            class="p-3 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                        <div class="font-medium text-gray-800">Financial Status</div>
                        <div class="text-sm text-gray-600">Get an overview of your finances</div>
                    </button>
                    <button onclick="askQuickQuestion('Are there any overdue invoices?')" 
                            class="p-3 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                        <div class="font-medium text-gray-800">Overdue Invoices</div>
                        <div class="text-sm text-gray-600">Check unpaid invoices</div>
                    </button>
                    <button onclick="askQuickQuestion('How are my payment collections performing?')" 
                            class="p-3 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                        <div class="font-medium text-gray-800">Payment Collections</div>
                        <div class="text-sm text-gray-600">Review payment performance</div>
                    </button>
                    <button onclick="askQuickQuestion('What are my revenue trends?')" 
                            class="p-3 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                        <div class="font-medium text-gray-800">Revenue Trends</div>
                        <div class="text-sm text-gray-600">Analyze revenue patterns</div>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            
            if (!query) return;
            
            // Add user message to chat
            addMessage(query, 'user');
            input.value = '';
            
            // Show typing indicator
            const typingDiv = addMessage('AI is thinking...', 'ai', true);
            
            try {
                const response = await fetch('/ai/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        user_id: 'web_user_' + Date.now()
                    })
                });
                
                const data = await response.json();
                
                // Remove typing indicator
                typingDiv.remove();
                
                if (response.ok) {
                    addMessage(data.answer, 'ai');
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', 'ai');
                }
            } catch (error) {
                typingDiv.remove();
                addMessage('Error connecting to AI service. Please try again.', 'ai');
            }
        }
        
        function askQuickQuestion(question) {
            document.getElementById('queryInput').value = question;
            sendQuery();
        }
        
        function addMessage(message, type, isTyping = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message ${isTyping ? 'typing' : ''}`;
            
            const prefix = type === 'user' ? 'You:' : 'AI Assistant:';
            messageDiv.innerHTML = `<strong>${prefix}</strong> ${message}`;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return messageDiv;
        }
        
        // Allow Enter key to send message
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendQuery();
            }
        });
    </script>
</body>
</html>
'''

# Write the HTML file
with open(os.path.join(frontend_dir, "index.html"), "w") as f:
    f.write(html_content)

# ------------------------------------------------------------------------------
# 4. Pydantic Models for API Data Structure
# ------------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Defines the structure for incoming requests to the /ai/ask endpoint."""
    query: str
    user_id: str  # To scope data access to the correct user.

class QueryResponse(BaseModel):
    """Defines the structure for the response sent back to the client."""
    answer: str

# ------------------------------------------------------------------------------
# 5. Comprehensive Retrieval Logic (The "R" in RAG)
# ------------------------------------------------------------------------------

def retrieve_financial_context(query: str) -> str:
    """
    Retrieves comprehensive financial data from MongoDB collections.
    Falls back to mock data if MongoDB is not available.
    """
    logger.info(f"Retrieving context for query: '{query}'")
    
    try:
        if db is not None:
            # Real MongoDB retrieval logic
            context_parts = []
            
            # Query Biggie's invoices collection
            overdue_invoices = list(db.invoices.find({
                "status": "overdue",
                "due_date": {"$lt": datetime.now()}
            }).limit(5))
            
            if overdue_invoices:
                invoice_summary = []
                for inv in overdue_invoices:
                    invoice_summary.append(f"{inv.get('invoice_number', 'N/A')} (KES {inv.get('amount', 0)})")
                context_parts.append(f"Outstanding Invoices: {', '.join(invoice_summary)}")
            
            # Query Muchamo's transactions collection
            recent_transactions = list(db.transactions.find({
                "timestamp": {"$gte": datetime.now() - timedelta(days=30)}
            }))
            
            if recent_transactions:
                successful = len([t for t in recent_transactions if t.get("status") == "successful"])
                failed = len([t for t in recent_transactions if t.get("status") == "failed"])
                context_parts.append(f"Recent Payment Health: {successful} Successful, {failed} Failed")
            
            # Query Munga's analytics_cache collection
            revenue_data = list(db.analytics_cache.find({
                "metric_type": "revenue_monthly"
            }).sort("period", -1).limit(2))
            
            if revenue_data:
                revenue_summary = []
                for data in revenue_data:
                    period = data.get("period", "Unknown")
                    amount = data.get("value", 0)
                    revenue_summary.append(f"{period}: {amount:,} KES")
                context_parts.append(f"Revenue Data: {', '.join(revenue_summary)}")
            
            if context_parts:
                return "Financial Context:\\n" + "\\n".join(context_parts)
        
        # Fallback to mock data
        return retrieve_mock_financial_context()
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return retrieve_mock_financial_context()

def retrieve_mock_financial_context() -> str:
    """
    Mock financial data for demonstration purposes.
    This simulates the data from different team members' collections.
    """
    # --- Step 1: Query Biggie's `invoices` Collection ---
    mock_overdue_invoices: List[Dict[str, Any]] = [
        {"invoice_number": "INV-2025-071", "customer_name": "Tech Innovators Ltd", "amount": 45000, "due_date": "2025-06-25"},
        {"invoice_number": "INV-2025-073", "customer_name": "Green Grocers", "amount": 12500, "due_date": "2025-06-30"},
    ]
    overdue_invoices_str = ", ".join([f"{inv['invoice_number']} (KES {inv['amount']})" for inv in mock_overdue_invoices])
    
    # --- Step 2: Query Muchamo's `transactions` Collection ---
    mock_transaction_summary = {"successful": 98, "failed": 2}
    transaction_health_str = f"{mock_transaction_summary['successful']} Successful, {mock_transaction_summary['failed']} Failed in the last 30 days."

    # --- Step 3: Query Munga's `analytics_cache` Collection ---
    mock_revenue_summary = {
        "june_2025": 220000,
        "july_2025": 155000
    }
    
    # --- Step 4: Combine all data into a comprehensive context ---
    final_context = f"""
    Comprehensive Financial Context:
    - High-Level Revenue (Analytics):
      - Revenue for June 2025: {mock_revenue_summary['june_2025']:,} KES
      - Revenue for July 2025: {mock_revenue_summary['july_2025']:,} KES

    - Outstanding Invoices:
      - Currently Overdue: {overdue_invoices_str}

    - Recent Payment Health:
      - Transaction Status (Last 30 Days): {transaction_health_str}
    """
    
    return final_context

# ------------------------------------------------------------------------------
# 6. Generation Logic (The "G" in RAG)
# ------------------------------------------------------------------------------

def generate_insight(query: str, context: str) -> str:
    """
    Uses the Gemini SDK to generate the final answer based on the query and context.
    """
    try:
        # Initialize the generative model from the Gemini SDK.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Detailed prompt template for Kenyan SMB financial assistant
        prompt = f"""
You are an expert financial assistant for Small and Medium Businesses in Kenya.
Your role is to provide accurate, actionable financial insights based on the provided data.

IMPORTANT INSTRUCTIONS:
- Use a helpful, professional, and clear tone
- Base your answer ONLY on the provided financial context
- If the context doesn't contain enough information, clearly state this
- Focus on actionable insights and recommendations
- Use Kenyan Shilling (KES) currency format
- Consider the Kenyan business environment (M-Pesa, banking, etc.)
- Provide specific numbers and examples where possible

FINANCIAL CONTEXT:
{context}

USER QUESTION:
{query}

EXPERT FINANCIAL ANALYSIS:
Please provide a comprehensive answer based on the available financial data.
Include specific insights, trends, and actionable recommendations where possible.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error during Gemini content generation: {e}")
        return "I apologize, but I encountered an error while analyzing your financial data. Please try again later."

# ------------------------------------------------------------------------------
# 7. API Endpoints
# ------------------------------------------------------------------------------

@app.post("/ai/ask", response_model=QueryResponse)
async def ask_financial_question(request: QueryRequest):
    """
    Main AI endpoint that orchestrates the RAG process:
    1. Receives a user query
    2. Retrieves comprehensive financial context
    3. Generates AI-powered insights using Gemini
    4. Returns the final answer
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # Step 1: Retrieve financial context (RAG - Retrieval)
        context_data = retrieve_financial_context(request.query)
        
        # Step 2: Generate AI insights (RAG - Generation)
        final_answer = generate_insight(request.query, context_data)
        
        # Step 3: Return structured response
        return QueryResponse(answer=final_answer)
        
    except Exception as e:
        logger.error(f"Error in /ai/ask endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/ai/health")
async def health_check():
    """Health check endpoint to confirm the service is running."""
    try:
        # Test database connection
        db_status = "connected" if db is not None else "disconnected"
        
        # Test Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        test_response = model.generate_content("Hello")
        gemini_status = "connected" if test_response else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "gemini_api": gemini_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stats")
async def get_financial_stats():
    """Get current financial statistics for the dashboard."""
    try:
        # This would normally query the database
        return {
            "revenue": "KES 220,000",
            "overdue_invoices": "KES 57,500",
            "payment_success_rate": "98%",
            "total_transactions": 100,
            "successful_transactions": 98,
            "failed_transactions": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------------------
# 8. Static Files Mount (Must be last to avoid route conflicts)
# ------------------------------------------------------------------------------

# Mount static files - this should be AFTER all API routes
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# ------------------------------------------------------------------------------
# 9. Main Application Entry Point
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Full-Stack AI Financial Insights Service...")
    print("🌐 Web Interface: http://localhost:8002")
    print("📋 API Documentation: http://localhost:8002/docs")
    print("🔍 Health Check: http://localhost:8002/ai/health")
    print("💬 AI Endpoint: http://localhost:8002/ai/ask")
    
    uvicorn.run(
        "fullstack_main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
