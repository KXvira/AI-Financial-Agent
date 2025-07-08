# AI Insights Service Documentation

## Overview

The AI Insights Service is a core component of the AI Financial Agent that provides conversational AI capabilities for financial analysis. It uses a Retrieval-Augmented Generation (RAG) architecture to combine data retrieval from MongoDB with AI generation using Google's Gemini SDK.

## Architecture

### RAG (Retrieval-Augmented Generation)

The service follows a two-step process:

1. **Retrieval**: Fetch relevant financial data from MongoDB based on user queries
2. **Generation**: Use Google Gemini SDK to interpret the data and generate intelligent responses

### Components

- **Service Layer** (`backend/ai_insights/service.py`): Core business logic and RAG implementation
- **API Layer** (`backend/ai_insights/router.py`): FastAPI endpoints for external access
- **Integration** (`backend/app.py`): Integration with the main FastAPI application

## Features

### Core Capabilities

- **Transaction Analysis**: Analyze spending patterns, categorize expenses, identify trends
- **Revenue Insights**: Track income sources, M-Pesa payments, revenue trends
- **Customer Analytics**: Customer payment patterns, outstanding invoices, top customers
- **Financial Health**: Overall financial summaries and health assessments
- **Forecasting**: Basic prediction and trend analysis

### Supported Queries

The AI can answer questions like:
- "What are my spending patterns this month?"
- "How much revenue did I generate from M-Pesa payments?"
- "Which customers have outstanding invoices?"
- "Show me a summary of my financial health"
- "Compare this month's revenue to last month"

## API Endpoints

### Base URL: `/ai`

#### 1. Ask Financial Question
```http
POST /ai/ask
```

**Request Body:**
```json
{
  "question": "What are my spending patterns this month?",
  "context": "monthly analysis",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "transaction_type": "all"
}
```

**Response:**
```json
{
  "question": "What are my spending patterns this month?",
  "answer": "Based on your financial data for January 2024...",
  "confidence": 0.85,
  "data_sources": ["transactions", "invoices"],
  "timestamp": "2024-01-31T10:30:00",
  "suggestions": [
    "Consider reducing discretionary spending",
    "Set up automatic savings transfers"
  ]
}
```

#### 2. Health Check
```http
GET /ai/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_api": "connected",
  "timestamp": "2024-01-31T10:30:00"
}
```

#### 3. Service Status
```http
GET /ai/status
```

**Response:**
```json
{
  "service": "AI Financial Insights",
  "version": "1.0.0",
  "status": "running",
  "features": ["Financial Q&A", "Transaction Analysis", ...],
  "ai_model": "gemini-1.5-pro",
  "database": "kenya_fintech_suite"
}
```

#### 4. Example Queries
```http
GET /ai/examples
```

Returns example questions organized by category.

## Configuration

### Environment Variables

Required environment variables in `.env`:

```bash
# Database
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=kenya_fintech_suite

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_OUTPUT_TOKENS=2048
```

### Database Schema

The service expects the following MongoDB collections:

- **transactions**: Financial transaction records
- **invoices**: Invoice data
- **customers**: Customer information

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 3. Start the Service

```bash
# Start the FastAPI server
python app.py

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the Service

```bash
# Run the test script
python scripts/test_ai_insights.py
```

## Usage Examples

### Frontend Integration

```javascript
// Ask a financial question
const response = await fetch('/ai/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: "What are my top expenses this month?",
    date_range: {
      start: "2024-01-01",
      end: "2024-01-31"
    }
  })
});

const insight = await response.json();
console.log(insight.answer);
```

### Python Client

```python
import requests

# Ask a question
response = requests.post('http://localhost:8000/ai/ask', json={
    "question": "How is my financial health?",
    "context": "monthly review"
})

if response.status_code == 200:
    insight = response.json()
    print(f"AI Answer: {insight['answer']}")
```

## Development

### Adding New Features

1. **Data Retrieval**: Extend retrieval methods in `FinancialRAGService`
2. **AI Prompts**: Modify prompt templates for better responses
3. **Endpoints**: Add new API endpoints in the router
4. **Testing**: Update test scripts to cover new functionality

### Code Structure

```
backend/ai_insights/
├── __init__.py          # Package initialization
├── service.py           # Core RAG service implementation
└── router.py            # FastAPI routes and endpoints
```

### Key Classes

- **`AIInsightsConfig`**: Configuration management
- **`FinancialQuery`**: Request model for user queries
- **`AIInsightResponse`**: Response model for AI insights
- **`FinancialRAGService`**: Main service class implementing RAG

## Troubleshooting

### Common Issues

1. **"Gemini API Key not found"**
   - Ensure `GEMINI_API_KEY` is set in your `.env` file
   - Verify the API key is valid and has proper permissions

2. **"Database connection failed"**
   - Check `MONGO_URI` in your `.env` file
   - Ensure MongoDB is running and accessible

3. **"Service unhealthy"**
   - Check the `/ai/health` endpoint for specific error details
   - Verify all dependencies are installed correctly

### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
```

Check logs for detailed error information:

```bash
# View application logs
tail -f /var/log/ai-financial-agent.log
```

## Performance Considerations

### Optimization Tips

1. **Database Queries**: Add indexes on frequently queried fields
2. **Caching**: Implement Redis caching for common queries
3. **Rate Limiting**: Add rate limiting to prevent API abuse
4. **Async Processing**: Use async operations for better scalability

### Monitoring

Monitor the service using:

- Health check endpoint (`/ai/health`)
- Response times and error rates
- Database query performance
- Gemini API usage and costs

## Security

### Best Practices

1. **API Keys**: Store securely in environment variables
2. **Input Validation**: Validate all user inputs
3. **Rate Limiting**: Implement request rate limiting
4. **Authentication**: Add authentication for production use

### Data Privacy

- Financial data is processed in memory only
- No sensitive data is logged in plain text
- Implement data anonymization for AI training if needed

## Team Integration

### Frontend (Diana)
- Use the `/ai/ask` endpoint to integrate conversational AI
- Display AI responses in a chat-like interface
- Handle different response types and suggestions

### Backend (Kevo)
- Monitor database performance with AI queries
- Optimize database schema for AI retrieval
- Implement proper indexing strategies

### Services (Muchamo & Biggie)
- Ensure transaction and invoice data is properly formatted
- Maintain consistent data schemas across services
- Implement proper data validation

## Future Enhancements

### Planned Features

1. **Advanced Analytics**: More sophisticated financial analysis
2. **Predictive Modeling**: Better forecasting capabilities
3. **Multi-language Support**: Support for Swahili and other local languages
4. **Voice Integration**: Voice-based queries and responses
5. **Custom Reports**: AI-generated financial reports

### Scalability

- Implement horizontal scaling for high load
- Add caching layers for better performance
- Consider implementing model fine-tuning for domain-specific responses

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all function parameters
- Add comprehensive docstrings
- Write unit tests for new features

### Testing

```bash
# Run unit tests
pytest backend/ai_insights/tests/

# Run integration tests
python scripts/test_ai_insights.py

# Run load tests
python scripts/load_test_ai.py
```

## Support

For issues and questions:

1. Check this documentation first
2. Review the troubleshooting section
3. Check the logs for error details
4. Open an issue in the project repository

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: AI Financial Agent Team
