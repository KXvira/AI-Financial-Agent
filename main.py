# ==============================================================================
# main.py
# AI-Powered Financial Insights Service using RAG and Gemini SDK
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Imports and Setup
# ------------------------------------------------------------------------------
import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any

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

# Initialize the FastAPI application.
app = FastAPI(
    title="Kenya Fintech AI Assistant API",
    description="API for the AI-Powered Financial Management System"
)

# For this detailed example, we will simulate the database connection and data.
# In the real application, this would be a live connection to MongoDB Atlas.
# client = MongoClient(os.getenv("MONGO_URI"))
# db = client.kenya_fintech_suite

# ------------------------------------------------------------------------------
# 3. Pydantic Models for API Data Structure
# ------------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Defines the structure for incoming requests to the /ai/ask endpoint."""
    query: str
    user_id: str  # To scope data access to the correct user.

class QueryResponse(BaseModel):
    """Defines the structure for the response sent back to the client."""
    answer: str

# ------------------------------------------------------------------------------
# 4. Comprehensive Retrieval Logic (The "R" in RAG)
# ------------------------------------------------------------------------------

def retrieve_financial_context(query: str, user_id: str) -> str:
    """
    Retrieves a comprehensive financial context from multiple data sources.

    This function simulates querying the MongoDB collections managed by different
    team members to build a rich context for the language model.
    """
    print(f"Retrieving context for query: '{query}' for user: '{user_id}'")
    
    # --- Step 1: Query Biggie's `invoices` Collection ---
    # This simulates fetching overdue invoices from the collection Biggie manages.
    mock_overdue_invoices: List[Dict[str, Any]] = [
        {"invoice_number": "INV-2025-071", "customer_name": "Tech Innovators Ltd", "amount": 45000, "due_date": "2025-06-25"},
        {"invoice_number": "INV-2025-073", "customer_name": "Green Grocers", "amount": 12500, "due_date": "2025-06-30"},
    ]
    overdue_invoices_str = ", ".join([f"{inv['invoice_number']} (KES {inv['amount']})" for inv in mock_overdue_invoices])
    
    # --- Step 2: Query Muchamo's `transactions` Collection ---
    # This simulates analyzing recent payment data from Muchamo's service.
    mock_transaction_summary = {"successful": 98, "failed": 2}
    transaction_health_str = f"{mock_transaction_summary['successful']} Successful, {mock_transaction_summary['failed']} Failed in the last 30 days."

    # --- Step 3: Query Munga's `analytics_cache` Collection ---
    # This simulates fetching high-level summaries from the analytics cache.
    mock_revenue_summary = {
        "june_2025": 220000,
        "july_2025": 155000
    }
    
    # --- Step 4: Combine all data into a single, comprehensive context string ---
    # This rich context will allow the Gemini model to answer more complex questions.
    final_context = f"""
    Comprehensive Financial Context:
    - High-Level Revenue (Munga's Analytics):
      - Revenue for June 2025: {mock_revenue_summary['june_2025']:,} KES
      - Revenue for July 2025: {mock_revenue_summary['july_2025']:,} KES

    - Outstanding Invoices (Biggie's Data):
      - Currently Overdue: {overdue_invoices_str}

    - Recent Payment Health (Muchamo's Data):
      - Transaction Status (Last 30 Days): {transaction_health_str}
    """
    
    return final_context

# ------------------------------------------------------------------------------
# 5. Generation Logic (The "G" in RAG)
# ------------------------------------------------------------------------------

def generate_insight(query: str, context: str) -> str:
    """
    Uses the Gemini SDK to generate the final answer based on the query and context.
    """
    
    # Initialize the generative model from the Gemini SDK.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # This detailed prompt template is crucial for getting high-quality responses.
    # It instructs the model on its persona, constraints, and data sources.
    prompt = f"""
    You are an expert financial assistant for Small and Medium Businesses in Kenya.
    Your tone must be helpful, clear, and professional. You must synthesize information
    from all parts of the provided context to answer the user's question.

    Base your answer ONLY on the provided context. Do not make up information, numbers, or
    invoice details. If the context does not contain the answer, state that you do
    not have enough information to answer fully.

    ---
    COMPREHENSIVE CONTEXT:
    {context}
    ---
    
    USER QUESTION:
    {query}
    
    EXPERT ANSWER:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error during Gemini content generation: {e}")
        return "I'm sorry, but I encountered an error while analyzing your data. Please try again later."


# ------------------------------------------------------------------------------
# 6. FastAPI Endpoint to Tie It All Together
# ------------------------------------------------------------------------------

@app.post("/ai/ask", response_model=QueryResponse)
async def ask_financial_question(request: QueryRequest):
    """
    This endpoint orchestrates the RAG process:
    1. Receives a user query.
    2. Retrieves a comprehensive financial context.
    3. Generates a data-driven insight using Gemini.
    4. Returns the final answer.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # Step 1: Call the retrieval function.
        context_data = retrieve_financial_context(request.query, request.user_id)
        
        # Step 2: Call the generation function.
        final_answer = generate_insight(request.query, context_data)
        
        # Step 3: Create and return the response.
        return QueryResponse(answer=final_answer)
        
    except Exception as e:
        print(f"An error occurred in the /ai/ask endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/health")
async def health_check():
    """A simple endpoint to confirm the service is running."""
    return {"status": "healthy"}

# ------------------------------------------------------------------------------
# 7. Main Application Entry Point
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI-Powered Financial Insights Service...")
    print("📋 Documentation available at: http://localhost:8001/docs")
    print("🔍 Health check available at: http://localhost:8001/health")
    print("💬 Ask questions at: http://localhost:8001/ai/ask")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Using port 8001 to avoid conflicts with main app
        reload=True
    )
