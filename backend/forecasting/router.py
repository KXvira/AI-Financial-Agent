"""
Forecasting API Router
Endpoints for cash flow prediction and model management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Import our forecasting services
from .models import ForecastingService, ForecastInput, ForecastResult
from ..explainable_ai.service import ExplainableAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/forecasts", tags=["forecasting"])

# Global service instances (would be dependency injected in production)
forecasting_service = ForecastingService()
explainable_ai_service = ExplainableAIService()

# Mock data for demonstration
SAMPLE_HISTORICAL_DATA = [
    {"date": "2024-09-01", "amount": 15000, "type": "income", "description": "Sales"},
    {"date": "2024-09-02", "amount": -2500, "type": "expense", "description": "Supplies"},
    {"date": "2024-09-03", "amount": 8000, "type": "income", "description": "Services"},
    {"date": "2024-09-04", "amount": -1200, "type": "expense", "description": "Utilities"},
    {"date": "2024-09-05", "amount": 12000, "type": "income", "description": "Product sales"},
    {"date": "2024-09-06", "amount": -800, "type": "expense", "description": "Transport"},
    {"date": "2024-09-07", "amount": 6500, "type": "income", "description": "Consulting"},
    {"date": "2024-09-08", "amount": -3000, "type": "expense", "description": "Rent"},
    {"date": "2024-09-09", "amount": 9200, "type": "income", "description": "Sales"},
    {"date": "2024-09-10", "amount": -1500, "type": "expense", "description": "Marketing"},
]

@router.post("/train")
async def train_forecasting_models(
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Train both Prophet and LSTM forecasting models
    
    - **historical_data**: Optional historical transaction data
    - Returns training results and model information
    """
    try:
        # Use provided data or sample data
        training_data = historical_data if historical_data else SAMPLE_HISTORICAL_DATA
        
        if len(training_data) < 10:
            raise HTTPException(
                status_code=400,
                detail="Insufficient historical data. At least 10 data points required."
            )
        
        # Train models
        training_results = forecasting_service.train_models(training_data)
        
        logger.info(f"Models trained successfully with {len(training_data)} data points")
        
        return {
            "success": True,
            "message": "Forecasting models trained successfully",
            "training_results": training_results,
            "data_points_used": len(training_data),
            "models_available": ["prophet", "lstm"]
        }
        
    except Exception as e:
        logger.error(f"Model training error: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/predict")
async def generate_forecast(
    start_date: datetime,
    end_date: datetime,
    frequency: str = Query(default="D", description="Frequency: D=Daily, W=Weekly, M=Monthly"),
    confidence_interval: float = Query(default=0.8, ge=0.1, le=0.99),
    include_seasonality: bool = True,
    model_type: Optional[str] = Query(default=None, description="Specific model: 'prophet' or 'lstm'"),
    include_explanation: bool = True
) -> Dict[str, Any]:
    """
    Generate cash flow forecast
    
    - **start_date**: Start date for prediction
    - **end_date**: End date for prediction  
    - **frequency**: Prediction frequency (D/W/M)
    - **confidence_interval**: Confidence level (0.1-0.99)
    - **include_seasonality**: Include seasonal patterns
    - **model_type**: Specific model to use (optional)
    - **include_explanation**: Include AI explanation
    """
    try:
        # Validate date range
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        forecast_days = (end_date - start_date).days
        if forecast_days > 365:
            raise HTTPException(status_code=400, detail="Forecast period cannot exceed 365 days")
        
        # Create forecast input
        forecast_input = ForecastInput(
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            include_seasonality=include_seasonality,
            confidence_interval=confidence_interval
        )
        
        # Generate forecast
        if model_type:
            # Single model prediction
            if model_type == "prophet":
                forecast_result = forecasting_service.prophet_model.generate_forecast(forecast_input)
                result = {"forecast": forecast_result.dict(), "model_used": "prophet"}
            elif model_type == "lstm":
                # Need recent data for LSTM
                recent_data = [float(item["amount"]) for item in SAMPLE_HISTORICAL_DATA[-30:]]
                forecast_result = forecasting_service.lstm_model.generate_forecast(forecast_input, recent_data)
                result = {"forecast": forecast_result.dict(), "model_used": "lstm"}
            else:
                raise HTTPException(status_code=400, detail="Invalid model type. Use 'prophet' or 'lstm'")
        else:
            # Comprehensive forecast with both models
            recent_data = [float(item["amount"]) for item in SAMPLE_HISTORICAL_DATA[-30:]]
            comprehensive_result = forecasting_service.generate_comprehensive_forecast(forecast_input, recent_data)
            result = comprehensive_result
        
        # Add explanation if requested
        if include_explanation and "forecast" in result:
            forecast_data = result["forecast"]
            if isinstance(forecast_data, dict) and "predictions" in forecast_data:
                # Get first prediction for explanation
                first_prediction = forecast_data["predictions"][0] if forecast_data["predictions"] else {}
                
                explanation_data = {
                    "predicted_amount": first_prediction.get("predicted_amount", 0),
                    "base_amount": sum(item["amount"] for item in SAMPLE_HISTORICAL_DATA[-7:]) / 7,  # Last week average
                    "seasonal_factor": first_prediction.get("seasonal_component", 0),
                    "trend_component": first_prediction.get("trend_component", 0)
                }
                
                explanation = explainable_ai_service.explain_prediction("cash_flow_forecast", explanation_data)
                result["explanation"] = {
                    "explanation_id": explanation.explanation_id,
                    "natural_language": explanation.natural_language_explanation,
                    "confidence_score": explanation.confidence_score,
                    "feature_importances": [
                        {
                            "feature": f.feature_name,
                            "importance": f.importance,
                            "contribution": f.contribution,
                            "description": f.description
                        }
                        for f in explanation.feature_importances
                    ]
                }
        
        logger.info(f"Forecast generated for {forecast_days} days")
        return result
        
    except Exception as e:
        logger.error(f"Forecast generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")

@router.get("/models")
async def list_available_models() -> Dict[str, Any]:
    """
    List available forecasting models and their status
    """
    try:
        return {
            "available_models": [
                {
                    "name": "prophet",
                    "type": "time_series",
                    "description": "Facebook Prophet - Good for seasonal patterns",
                    "trained": forecasting_service.prophet_model.is_trained,
                    "strengths": ["Seasonal patterns", "Trend analysis", "Holiday effects"],
                    "best_for": "Businesses with clear seasonal patterns"
                },
                {
                    "name": "lstm", 
                    "type": "neural_network",
                    "description": "LSTM Neural Network - Good for complex patterns",
                    "trained": forecasting_service.lstm_model.is_trained,
                    "strengths": ["Complex patterns", "Non-linear relationships", "Long-term dependencies"],
                    "best_for": "Businesses with complex, irregular patterns"
                }
            ],
            "ensemble_available": forecasting_service.prophet_model.is_trained and forecasting_service.lstm_model.is_trained,
            "recommendation": "Use ensemble for best accuracy when both models are trained"
        }
        
    except Exception as e:
        logger.error(f"Model listing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/accuracy")
async def get_model_accuracy() -> Dict[str, Any]:
    """
    Get accuracy metrics for trained models
    """
    try:
        accuracy_data = {
            "prophet": {
                "trained": forecasting_service.prophet_model.is_trained,
                "metrics": {
                    "mape": 15.2,  # Mock data
                    "mae": 850.5,
                    "rmse": 1200.3,
                    "r_squared": 0.82
                } if forecasting_service.prophet_model.is_trained else None
            },
            "lstm": {
                "trained": forecasting_service.lstm_model.is_trained,
                "metrics": {
                    "mape": 12.8,  # Mock data
                    "mae": 720.1,
                    "rmse": 980.7,
                    "r_squared": 0.87
                } if forecasting_service.lstm_model.is_trained else None
            }
        }
        
        # Determine best model
        best_model = "lstm"  # Based on lower MAPE
        if forecasting_service.prophet_model.is_trained and forecasting_service.lstm_model.is_trained:
            recommendation = f"LSTM model shows better accuracy (MAPE: 12.8% vs 15.2%)"
        elif forecasting_service.prophet_model.is_trained:
            best_model = "prophet"
            recommendation = "Only Prophet model is trained"
        elif forecasting_service.lstm_model.is_trained:
            recommendation = "Only LSTM model is trained"
        else:
            best_model = None
            recommendation = "No models trained yet"
        
        return {
            "model_accuracy": accuracy_data,
            "best_model": best_model,
            "recommendation": recommendation,
            "accuracy_explanation": {
                "mape": "Mean Absolute Percentage Error - lower is better",
                "mae": "Mean Absolute Error in KES - lower is better", 
                "rmse": "Root Mean Square Error - lower is better",
                "r_squared": "Coefficient of determination - higher is better (max 1.0)"
            }
        }
        
    except Exception as e:
        logger.error(f"Accuracy retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get accuracy: {str(e)}")

@router.get("/health")
async def forecasting_health_check() -> Dict[str, Any]:
    """
    Health check for forecasting service
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "forecasting_service": "operational",
                "prophet_model": "trained" if forecasting_service.prophet_model.is_trained else "not_trained",
                "lstm_model": "trained" if forecasting_service.lstm_model.is_trained else "not_trained",
                "explainable_ai": "operational"
            },
            "capabilities": [
                "cash_flow_forecasting",
                "model_comparison", 
                "prediction_explanation",
                "accuracy_metrics"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }