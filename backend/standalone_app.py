"""
Standalone FastAPI Backend for AI Financial Agent
CORS-only communication with Next.js frontend
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import os
import logging
from datetime import datetime
import json

# Try to import dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Environment variables need to be set manually.")

# Import application modules
try:
    from database.mongodb import Database
    from ai_insights.service import FinancialRAGService, get_ai_insights_service
    database_available = True
except ImportError as e:
    print(f"Warning: Database or AI service not available: {e}")
    database_available = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("financial-agent-standalone")

# Pydantic models for API requests and responses
class AIQueryRequest(BaseModel):
    """Request model for AI financial queries"""
    query: str = Field(..., min_length=3, max_length=1000, description="Financial question to ask")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")

class AIQueryResponse(BaseModel):
    """Response model for AI financial queries"""
    response: str = Field(..., description="AI-generated financial insight")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    database_connected: bool = Field(..., description="Database connection status")

# Create FastAPI app
app = FastAPI(
    title="AI Financial Agent - Standalone Backend",
    description="Standalone FastAPI backend for AI-powered financial insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default port
        "http://localhost:3001",  # Alternative Next.js port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database if available
if database_available:
    @app.on_event("startup")
    async def startup_db_client():
        logger.info("Initializing database connection...")
        try:
            app.db = Database.get_instance()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            
    @app.on_event("shutdown")
    async def shutdown_db_client():
        logger.info("Closing database connection...")
        if hasattr(app, "db"):
            try:
                await app.db.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_connected = False
    if database_available and hasattr(app, "db"):
        try:
            # Simple database ping
            await app.db.ping()
            db_connected = True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
    
    return HealthResponse(
        status="healthy",
        service="AI Financial Agent Backend",
        version="1.0.0",
        database_connected=db_connected
    )

# AI insights endpoint
@app.post("/ai/ask", response_model=AIQueryResponse)
async def ask_ai_question(request: AIQueryRequest):
    """
    Ask AI a financial question using RAG architecture
    
    This endpoint:
    1. Retrieves relevant financial context from MongoDB
    2. Uses Gemini SDK to generate AI-powered insights
    3. Returns structured response with confidence and sources
    """
    try:
        logger.info(f"Received AI query: {request.query[:100]}...")
        
        # Validate input
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # If AI service is available, use it
        if database_available:
            try:
                service = get_ai_insights_service()
                
                # Create a query request object for the service
                from ai_insights.service import QueryRequest
                query_req = QueryRequest(query=request.query)
                
                # Get AI response
                ai_response = service.ask_financial_question(query_req)
                
                return AIQueryResponse(
                    response=ai_response.response,
                    confidence=ai_response.confidence,
                    sources=ai_response.sources,
                    timestamp=ai_response.timestamp
                )
                
            except Exception as e:
                logger.error(f"AI service error: {e}")
                # Fall back to mock response
                return _mock_ai_response(request.query)
        else:
            # Return mock response when services not available
            return _mock_ai_response(request.query)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def _mock_ai_response(query: str) -> AIQueryResponse:
    """Generate a mock AI response for testing"""
    mock_responses = {
        "spending": "Based on your recent transactions, your spending patterns show increased activity in food and transportation categories. Consider budgeting more carefully in these areas.",
        "income": "Your income streams appear stable with regular monthly deposits. Consider diversifying your income sources for better financial security.",
        "savings": "Your savings rate is currently at 15% of your income. Financial experts recommend saving at least 20% for optimal financial health.",
        "investments": "Your investment portfolio shows moderate growth. Consider rebalancing your assets to include more diverse options.",
        "default": "I understand you're asking about your finances. While I don't have access to your specific data right now, I recommend reviewing your recent transactions and creating a budget to track your spending patterns."
    }
    
    # Simple keyword matching for mock responses
    query_lower = query.lower()
    response = mock_responses["default"]
    
    for keyword, mock_response in mock_responses.items():
        if keyword in query_lower:
            response = mock_response
            break
    
    return AIQueryResponse(
        response=response,
        confidence=0.75,
        sources=["Mock Data"],
        timestamp=datetime.now()
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "AI Financial Agent - Standalone Backend",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "ai_query": "/ai/ask",
            "docs": "/docs"
        }
    }

# Environment info endpoint for debugging (development only)
@app.get("/api/env")
async def env_info():
    """Environment info for debugging"""
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "production":
        return {
            "environment": env,
            "debug": False
        }
    else:
        return {
            "environment": env,
            "debug": True,
            "database_available": database_available,
            "mongo_uri": os.environ.get("MONGO_URI", "Not set"),
            "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        "standalone_app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
