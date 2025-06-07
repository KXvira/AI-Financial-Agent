"""
Gemini API client service for AI-powered financial reconciliation
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger("financial-agent.ai.gemini")

class GeminiConfig:
    """Configuration for Gemini API"""
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "your-api-key")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        self.temperature = float(os.environ.get("GEMINI_TEMPERATURE", "0.2"))
        self.max_output_tokens = int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
        

class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self):
        self.config = GeminiConfig()
        genai.configure(api_key=self.config.api_key)
        
        # Check which model to use based onhgy67 config
        # Create generation config as a dictionary which is the expected format
        generation_config = {
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_output_tokens,
            "top_p": 0.95,
            "top_k": 40
        }
        
        # Use the genai package's public method to get a GenerativeModel
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config=generation_config
        )
    
    async def reconcile_payment(self, payment_data: Dict[str, Any], invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reconcile a payment against a list of possible invoices
        
        Args:
            payment_data: The payment data from M-Pesa
            invoices: List of pending invoices
            
        Returns:
            Dict with reconciliation result
        """
        try:
            # Create a prompt for reconciliation
            prompt = self._create_reconciliation_prompt(payment_data, invoices)
            
            # Send to Gemini
            response = await self._generate_response(prompt)
            
            # Parse the response into structured data
            reconciliation_result = self._parse_reconciliation_response(response)
            
            # Log result
            logger.info(f"Payment reconciliation result: {json.dumps(reconciliation_result)}")
            
            return reconciliation_result
            
        except Exception as e:
            logger.error(f"Error in payment reconciliation: {str(e)}")
            raise
    
    async def categorize_expense(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize a transaction into appropriate expense category
        
        Args:
            transaction_data: The transaction data
            
        Returns:
            Dict with categorization result
        """
        try:
            # Create a prompt for categorization
            prompt = self._create_categorization_prompt(transaction_data)
            
            # Send to Gemini
            response = await self._generate_response(prompt)
            
            # Parse the response into structured data
            categorization_result = self._parse_categorization_response(response)
            
            # Log result
            logger.info(f"Transaction categorization result: {json.dumps(categorization_result)}")
            
            return categorization_result
            
        except Exception as e:
            logger.error(f"Error in transaction categorization: {str(e)}")
            raise
    
    async def detect_anomalies(self, transaction_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect anomalies in transaction data
        
        Args:
            transaction_data: The current transaction data
            historical_data: Historical transaction data for comparison
            
        Returns:
            Dict with anomaly detection result
        """
        try:
            # Create a prompt for anomaly detection
            prompt = self._create_anomaly_detection_prompt(transaction_data, historical_data)
            
            # Send to Gemini
            response = await self._generate_response(prompt)
            
            # Parse the response into structured data
            anomaly_result = self._parse_anomaly_response(response)
            
            return anomaly_result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            raise
    
    async def generate_financial_insights(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate financial insights from transaction and business data
        
        Args:
            financial_data: Financial data for analysis
            
        Returns:
            Dict with financial insights
        """
        try:
            # Create a prompt for insight generation
            prompt = self._create_insight_prompt(financial_data)
            
            # Send to Gemini
            response = await self._generate_response(prompt)
            
            # Parse the response into structured data
            insights = self._parse_insights_response(response)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating financial insights: {str(e)}")
            raise
    
    async def _generate_response(self, prompt: str) -> str:
        """
        Generate a response from Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            String response from Gemini
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def _create_reconciliation_prompt(self, payment_data: Dict[str, Any], invoices: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for payment reconciliation
        """
        # Format payment data into a readable string
        payment_str = json.dumps(payment_data, indent=2)
        
        # Format invoices into a readable string
        invoices_str = json.dumps(invoices, indent=2)
        
        # Create the prompt
        prompt = f"""You are an expert financial reconciliation AI assistant. 
Your task is to determine which invoice matches the following M-Pesa payment.

PAYMENT DETAILS:
```json
{payment_str}
```

PENDING INVOICES:
```json
{invoices_str}
```

Analyze the following factors to find the best match:
1. Payment amount vs invoice amount (exact match or within 5%)
2. Phone number of payer matches customer contact
3. Reference number or payment description matches invoice number
4. Invoice date is before payment date
5. Any other relevant factors

Return your analysis in JSON format with these fields:
- matched_invoice_id: The ID of the matched invoice, or null if no match
- confidence_score: A score from 0-100 indicating confidence level
- match_reason: Brief explanation of why this invoice matches
- partial_payment: true/false indicating if this appears to be a partial payment
- action_required: Whether human review is needed (true if confidence < 70)

Output JSON format only, no additional text.
"""
        
        return prompt
    
    def _parse_reconciliation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response from Gemini into structured data
        """
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure required fields
                required_fields = ["matched_invoice_id", "confidence_score", "match_reason"]
                for field in required_fields:
                    if field not in result:
                        result[field] = None
                
                return result
            else:
                logger.warning(f"Could not parse JSON from response: {response}")
                return {
                    "matched_invoice_id": None,
                    "confidence_score": 0,
                    "match_reason": "Could not parse response",
                    "partial_payment": False,
                    "action_required": True
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing reconciliation response: {str(e)}")
            return {
                "matched_invoice_id": None,
                "confidence_score": 0,
                "match_reason": f"Error parsing response: {str(e)}",
                "partial_payment": False,
                "action_required": True
            }
    
    def _create_categorization_prompt(self, transaction_data: Dict[str, Any]) -> str:
        """Create a prompt for transaction categorization"""
        transaction_str = json.dumps(transaction_data, indent=2)
        
        prompt = f"""You are an expert financial categorization AI assistant specialized in Kenyan business transactions.
Your task is to categorize the following transaction into the most appropriate expense or income category.

TRANSACTION DETAILS:
```json
{transaction_str}
```

Categorize this transaction into one of the following categories:
- Office Supplies
- Utilities
- Rent
- Salaries
- Marketing
- Travel
- Professional Services
- Software Subscriptions
- Equipment
- Maintenance
- Food and Entertainment
- Telecommunications
- Insurance
- Taxes
- Banking Fees
- Sales Revenue
- Service Revenue
- Interest Income
- Other Income
- Uncategorized

Return your analysis in JSON format with these fields:
- category: The determined category
- subcategory: A more specific subcategory if applicable
- confidence_score: A score from 0-100 indicating confidence level
- explanation: Brief explanation for this categorization
- action_required: Whether human review is needed (true if confidence < 70)

Output JSON format only, no additional text.
"""
        
        return prompt

    def _parse_categorization_response(self, response: str) -> Dict[str, Any]:
        """Parse the categorization response"""
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure required fields
                required_fields = ["category", "confidence_score", "explanation"]
                for field in required_fields:
                    if field not in result:
                        result[field] = None
                
                return result
            else:
                logger.warning(f"Could not parse JSON from response: {response}")
                return {
                    "category": "Uncategorized",
                    "confidence_score": 0,
                    "explanation": "Could not parse response",
                    "action_required": True
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing categorization response: {str(e)}")
            return {
                "category": "Uncategorized",
                "confidence_score": 0,
                "explanation": f"Error parsing response: {str(e)}",
                "action_required": True
            }
    
    def _create_anomaly_detection_prompt(self, transaction_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> str:
        """Create a prompt for anomaly detection"""
        transaction_str = json.dumps(transaction_data, indent=2)
        historical_str = json.dumps(historical_data, indent=2)
        
        prompt = f"""You are an expert financial fraud detection AI assistant.
Your task is to determine if the following transaction shows any signs of being anomalous or potentially fraudulent.

CURRENT TRANSACTION:
```json
{transaction_str}
```

HISTORICAL TRANSACTIONS:
```json
{historical_str}
```

Analyze the following factors to detect potential anomalies:
1. Transaction amount compared to usual patterns
2. Time of day compared to usual patterns
3. Frequency of transactions
4. Unusual merchant or location
5. Any other relevant factors

Return your analysis in JSON format with these fields:
- is_anomalous: true/false indicating if this is an anomaly
- anomaly_score: A score from 0-100 indicating severity (higher is more anomalous)
- anomaly_type: Type of anomaly detected (e.g., "unusual_amount", "unusual_timing", "duplicate_payment")
- explanation: Brief explanation of why this is anomalous
- action_required: Whether human review is needed (true if anomaly_score > 70)
- recommendation: Brief recommendation for how to handle this transaction

Output JSON format only, no additional text.
"""
        
        return prompt

    def _parse_anomaly_response(self, response: str) -> Dict[str, Any]:
        """Parse the anomaly detection response"""
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure required fields
                required_fields = ["is_anomalous", "anomaly_score", "explanation"]
                for field in required_fields:
                    if field not in result:
                        result[field] = None
                
                return result
            else:
                logger.warning(f"Could not parse JSON from response: {response}")
                return {
                    "is_anomalous": False,
                    "anomaly_score": 0,
                    "explanation": "Could not parse response",
                    "action_required": True,
                    "recommendation": "Review manually"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing anomaly response: {str(e)}")
            return {
                "is_anomalous": False,
                "anomaly_score": 0,
                "explanation": f"Error parsing response: {str(e)}",
                "action_required": True,
                "recommendation": "Review manually"
            }
            
    def _create_insight_prompt(self, financial_data: Dict[str, Any]) -> str:
        """Create a prompt for generating financial insights"""
        financial_str = json.dumps(financial_data, indent=2)
        
        prompt = f"""You are an expert financial analyst AI assistant specialized in Kenyan business financial analysis.
Your task is to generate valuable business insights from the following financial data.

FINANCIAL DATA:
```json
{financial_str}
```

Generate insights on the following aspects:
1. Cash flow trends and projections
2. Revenue growth patterns
3. Expense optimization opportunities
4. Customer payment behavior
5. Key financial metrics (e.g., DSO, cash conversion cycle)

Return your analysis in JSON format with these fields:
- key_insights: List of 3-5 most important insights
- cash_flow_analysis: Brief analysis of cash flow trends
- revenue_analysis: Brief analysis of revenue patterns
- expense_analysis: Brief analysis of expense patterns and optimization opportunities
- customer_analysis: Brief analysis of customer payment behavior
- recommendations: List of 2-3 actionable recommendations

Output JSON format only, no additional text.
"""
        
        return prompt

    def _parse_insights_response(self, response: str) -> Dict[str, Any]:
        """Parse the financial insights response"""
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure required fields
                required_fields = ["key_insights", "recommendations"]
                for field in required_fields:
                    if field not in result:
                        result[field] = []
                
                return result
            else:
                logger.warning(f"Could not parse JSON from response: {response}")
                return {
                    "key_insights": ["Could not generate insights"],
                    "cash_flow_analysis": "Analysis unavailable",
                    "revenue_analysis": "Analysis unavailable",
                    "expense_analysis": "Analysis unavailable",
                    "customer_analysis": "Analysis unavailable",
                    "recommendations": ["Review financial data manually"]
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing insights response: {str(e)}")
            return {
                "key_insights": [f"Error parsing response: {str(e)}"],
                "cash_flow_analysis": "Analysis unavailable",
                "revenue_analysis": "Analysis unavailable",
                "expense_analysis": "Analysis unavailable",
                "customer_analysis": "Analysis unavailable",
                "recommendations": ["Review financial data manually"]
            }
