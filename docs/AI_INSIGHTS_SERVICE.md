# AI Financial Insights Service Documentation

## Overview

The AI Financial Insights Service provides conversational AI capabilities for financial queries using a Retrieval-Augmented Generation (RAG) architecture. It combines data retrieval from your MongoDB database with Google's Gemini AI to generate intelligent financial insights.

## Architecture

### RAG (Retrieval-Augmented Generation) Flow

1. **Retrieval Step**: Query relevant financial data from MongoDB
   - Transaction summaries by month
   - Invoice status and payment data
   - Expense categorization
   - Payment gateway statistics

2. **Generation Step**: Use Google Gemini AI to:
   - Interpret the retrieved data
   - Generate human-readable insights
   - Provide actionable recommendations

## API Endpoints

### POST `/ai/ask`

Ask a financial question and receive AI-powered insights.

**Request Body:**
```json
{
    "query": "What was my revenue trend for the last 3 months?"
}
```

**Response:**
```json
{
    "answer": "Based on your financial data, your revenue has shown a positive trend over the last 3 months...",
    "context_used": "Financial data from May-July 2025",
    "confidence": "high"
}
```

### GET `/ai/health`

Check the health status of the AI insights service.

**Response:**
```json
{
    "service": "AI Financial Insights",
    "status": "healthy",
    "database_connected": true,
    "gemini_api_connected": true,
    "timestamp": "2025-07-08T14:30:00"
}
```

### GET `/ai/status`

Get detailed status and capabilities of the AI service.

**Response:**
```json
{
    "ai_insights_service": "running",
    "database_status": "connected",
    "gemini_api_status": "connected",
    "supported_queries": [
        "Revenue trends and analysis",
        "Expense categorization and optimization",
        "Invoice and payment status summaries",
        "Cash flow analysis",
        "Business performance metrics",
        "Payment gateway statistics"
    ],
    "example_queries": [
        "What was my revenue for the last 3 months?",
        "Show me my top expense categories",
        "How many invoices are still pending payment?",
        "What's my average transaction amount?",
        "Which payment gateway performs best?"
    ]
}
```

## Supported Query Types

### Revenue Analysis
- "What was my revenue for the last 3 months?"
- "Show me my monthly revenue trends"
- "How does this month's revenue compare to last month?"

### Transaction Analysis
- "How many transactions did I process this month?"
- "What's my average transaction amount?"
- "Show me transaction patterns by payment gateway"

### Invoice Management
- "How many invoices are still pending payment?"
- "What's my invoice payment rate?"
- "Show me overdue invoices"

### Expense Tracking
- "What are my top expense categories?"
- "How much did I spend on office supplies this month?"
- "Show me expense optimization opportunities"

### Business Performance
- "What are my key business metrics?"
- "How is my cash flow looking?"
- "Give me a business performance summary"

## Configuration

### Environment Variables

```bash
# Database Configuration
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=kenya_fintech_suite

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro
```

### MongoDB Collections Used

1. **transactions**: Payment transaction data
2. **invoices**: Invoice and billing data
3. **analytics_cache**: Pre-computed analytics data (optional)

## Integration Guide

### Frontend Integration

```javascript
// Example frontend usage
const askFinancialQuestion = async (query) => {
    const response = await fetch('/ai/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
    });
    
    return await response.json();
};

// Usage
const insight = await askFinancialQuestion("What was my revenue last month?");
console.log(insight.answer);
```

### Backend Integration

```python
from backend.ai_insights import process_financial_query, QueryRequest

# Process a query
request = QueryRequest(query="Show me my expense breakdown")
response = await process_financial_query(request)
print(response.answer)
```

## Data Requirements

### Minimum Data for Meaningful Insights

1. **Transactions Table**:
   - At least 10 transactions
   - Timestamps within the last 3 months
   - Status field indicating completion

2. **Invoices Table**:
   - At least 5 invoices
   - Status information (paid, pending, overdue)
   - Customer and amount data

### Data Quality Recommendations

- Ensure transaction amounts are in consistent currency (KES)
- Use standardized status values across collections
- Include proper timestamps for time-based analysis
- Maintain customer contact information for reconciliation

## Error Handling

### Common Error Scenarios

1. **Insufficient Data**: When database has no relevant data
   - Returns informative message about data requirements
   - Suggests actions to improve data quality

2. **API Connection Issues**: When Gemini API is unavailable
   - Graceful fallback with error explanation
   - Maintains service availability for other features

3. **Database Connection Issues**: When MongoDB is unavailable
   - Clear error messages
   - Health check endpoints report status

## Security Considerations

### Data Privacy
- Financial data never leaves your infrastructure during processing
- Only aggregated, anonymized data is sent to Gemini API
- No customer personal information is included in AI prompts

### API Security
- Environment variables for sensitive credentials
- Input validation for all queries
- Rate limiting recommendations for production

## Performance Optimization

### Caching Strategy
- Pre-compute common analytics in `analytics_cache` collection
- Cache frequently requested insights
- Optimize MongoDB queries with proper indexing

### Query Optimization
- Limit data retrieval timeframes
- Use aggregation pipelines for complex queries
- Implement pagination for large datasets

## Testing

### Unit Tests
```bash
# Run the test script
python scripts/test_ai_insights.py
```

### Integration Tests
```bash
# Test with real database
python -m pytest tests/test_ai_insights_integration.py
```

## Troubleshooting

### Common Issues

1. **"No relevant data found"**
   - Check if transactions exist in database
   - Verify date ranges and data quality
   - Ensure proper collection names

2. **"Gemini API connection failed"**
   - Verify GEMINI_API_KEY is set correctly
   - Check internet connectivity
   - Confirm API quota and billing status

3. **"Database connection failed"**
   - Verify MONGO_URI is correct
   - Check MongoDB service status
   - Confirm database permissions

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger("financial-agent.ai.insights").setLevel(logging.DEBUG)
```

## Production Deployment

### Scaling Considerations
- Use connection pooling for MongoDB
- Implement request queuing for high load
- Consider caching for frequently asked questions

### Monitoring
- Monitor API response times
- Track Gemini API usage and costs
- Set up alerts for service health

### Security Hardening
- Use environment-specific API keys
- Implement proper CORS policies
- Add request rate limiting
- Enable audit logging for financial queries
