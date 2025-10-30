"""
AI Invoice Generation Service
Generates invoice drafts using Gemini AI based on customer context and natural language input
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available. AI features will be disabled.")

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

logger = logging.getLogger(__name__)


class AIInvoiceService:
    """Service for generating invoices using Gemini AI"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.logger = logger
        self.model = None
        
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.warning("GEMINI_API_KEY not set. AI features will be limited.")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.logger.info("Gemini AI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            self.model = None
    
    async def get_customer_context(self, customer_id: str) -> Dict[str, Any]:
        """
        Gather customer context for AI invoice generation
        Includes customer details, recent invoices, payment history, and patterns
        """
        try:
            # Get customer details
            customer = await self.db.customers.find_one({"customer_id": customer_id})
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            
            # Get recent invoices (last 10)
            recent_invoices = await self.db.invoices.find(
                {"customer_id": customer_id}
            ).sort("issue_date", -1).limit(10).to_list(10)
            
            # Get payment history (last 10)
            recent_payments = await self.db.receipts.find(
                {"customer_name": customer["name"]}
            ).sort("transaction_date", -1).limit(10).to_list(10)
            
            # Calculate patterns
            patterns = await self._analyze_patterns(customer_id, recent_invoices)
            
            context = {
                "customer": {
                    "id": customer["customer_id"],
                    "name": customer["name"],
                    "email": customer["email"],
                    "phone": customer["phone"],
                    "business_type": customer.get("business_type", ""),
                    "payment_terms": customer.get("payment_terms", 30),
                    "payment_status": customer.get("payment_status", "good"),
                    "total_invoices": customer.get("total_invoices", 0),
                    "outstanding_amount": customer.get("outstanding_amount", 0),
                },
                "recent_invoices": [
                    {
                        "invoice_id": inv.get("invoice_id", ""),
                        "amount": inv.get("amount", 0),
                        "status": inv.get("status", ""),
                        "issue_date": inv.get("issue_date", ""),
                        "items": inv.get("items", []),
                    }
                    for inv in recent_invoices[:5]  # Last 5 invoices
                ],
                "patterns": patterns,
                "preferences": customer.get("ai_preferences", {
                    "enabled": True,
                    "tone": "professional",
                    "language": "en"
                })
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error gathering customer context: {str(e)}")
            raise
    
    async def _analyze_patterns(self, customer_id: str, invoices: List[Dict]) -> Dict[str, Any]:
        """Analyze customer invoice patterns"""
        if not invoices:
            return {
                "average_invoice_amount": 0,
                "common_items": [],
                "typical_quantity": 1,
                "invoice_frequency": "monthly",
            }
        
        # Calculate average amount
        amounts = [inv.get("amount", 0) for inv in invoices]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        
        # Extract common items
        all_items = []
        for inv in invoices:
            items = inv.get("items", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        all_items.append(item.get("description", ""))
        
        # Count item frequency
        item_counts = {}
        for item in all_items:
            if item:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        # Get top 5 most common items
        common_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "average_invoice_amount": round(avg_amount, 2),
            "common_items": [item[0] for item in common_items],
            "typical_quantity": 1,
            "invoice_frequency": "monthly",
            "last_invoice_amount": amounts[0] if amounts else 0,
        }
    
    async def generate_invoice_draft(
        self,
        customer_id: str,
        user_input: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an invoice draft using AI based on user input and customer context
        
        Args:
            customer_id: Customer ID
            user_input: Natural language description of what to invoice
            options: Additional options (due_days, currency, etc.)
        
        Returns:
            Invoice draft with items, amounts, and metadata
        """
        if not self.model:
            return await self._generate_mock_invoice(customer_id, user_input, options)
        
        try:
            # Get customer context
            context = await self.get_customer_context(customer_id)
            
            # Build prompt
            prompt = self._build_invoice_prompt(context, user_input, options)
            
            # Generate invoice using Gemini
            response = await self._call_gemini(prompt)
            
            # Parse response
            invoice_draft = self._parse_invoice_response(response, context, options)
            
            return invoice_draft
            
        except Exception as e:
            self.logger.error(f"Error generating invoice draft: {str(e)}")
            raise
    
    def _build_invoice_prompt(
        self,
        context: Dict[str, Any],
        user_input: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the AI prompt for invoice generation"""
        options = options or {}
        
        customer = context["customer"]
        patterns = context["patterns"]
        preferences = context["preferences"]
        
        prompt = f"""You are an expert invoice generator. Generate a professional invoice based on the following context and user request.

CUSTOMER CONTEXT:
- Name: {customer['name']}
- Business Type: {customer['business_type']}
- Payment Terms: {customer['payment_terms']} days
- Payment Status: {customer['payment_status']}
- Total Invoices: {customer['total_invoices']}
- Outstanding: KES {customer['outstanding_amount']:,.2f}

HISTORICAL PATTERNS:
- Average Invoice Amount: KES {patterns['average_invoice_amount']:,.2f}
- Last Invoice Amount: KES {patterns['last_invoice_amount']:,.2f}
- Common Items: {', '.join(patterns['common_items'][:3]) if patterns['common_items'] else 'None'}

USER REQUEST:
{user_input}

INSTRUCTIONS:
1. Generate invoice items based on the user request
2. Use realistic pricing based on historical patterns
3. Include item description, quantity, unit price, and total
4. Calculate subtotal, tax (16% VAT if applicable), and total amount
5. Set appropriate due date based on payment terms
6. Use professional tone: {preferences.get('tone', 'professional')}

OUTPUT FORMAT (JSON):
{{
  "items": [
    {{
      "description": "Item description",
      "quantity": 1,
      "unit_price": 0.00,
      "total": 0.00
    }}
  ],
  "subtotal": 0.00,
  "tax_rate": 0.16,
  "tax_amount": 0.00,
  "total_amount": 0.00,
  "notes": "Additional notes or payment instructions",
  "due_days": {options.get('due_days', customer['payment_terms'])}
}}

Generate the invoice now. Return ONLY valid JSON, no markdown or explanations."""
        
        return prompt
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini AI with the prompt"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                )
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _parse_invoice_response(
        self,
        response: str,
        context: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse Gemini response into invoice draft"""
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            invoice_data = json.loads(cleaned_response)
            
            # Add metadata
            customer = context["customer"]
            due_days = invoice_data.get("due_days", customer["payment_terms"])
            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=due_days)
            
            draft = {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "issue_date": issue_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "items": invoice_data.get("items", []),
                "subtotal": invoice_data.get("subtotal", 0),
                "tax_rate": invoice_data.get("tax_rate", 0.16),
                "tax_amount": invoice_data.get("tax_amount", 0),
                "total_amount": invoice_data.get("total_amount", 0),
                "currency": options.get("currency", "KES") if options else "KES",
                "notes": invoice_data.get("notes", ""),
                "status": "draft",
                "generated_by": "ai",
                "generated_at": datetime.now().isoformat(),
            }
            
            return draft
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Response was: {response}")
            raise ValueError("AI generated invalid invoice format")
        except Exception as e:
            self.logger.error(f"Error parsing invoice response: {str(e)}")
            raise
    
    async def _generate_mock_invoice(
        self,
        customer_id: str,
        user_input: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a mock invoice when Gemini is not available"""
        try:
            context = await self.get_customer_context(customer_id)
            customer = context["customer"]
            patterns = context["patterns"]
            
            # Simple mock invoice based on patterns
            amount = patterns.get("average_invoice_amount", 10000)
            subtotal = amount
            tax_amount = subtotal * 0.16
            total = subtotal + tax_amount
            
            due_days = options.get("due_days", customer["payment_terms"]) if options else customer["payment_terms"]
            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=due_days)
            
            return {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "issue_date": issue_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "items": [
                    {
                        "description": f"Service as requested: {user_input[:50]}",
                        "quantity": 1,
                        "unit_price": subtotal,
                        "total": subtotal
                    }
                ],
                "subtotal": subtotal,
                "tax_rate": 0.16,
                "tax_amount": tax_amount,
                "total_amount": total,
                "currency": options.get("currency", "KES") if options else "KES",
                "notes": "Mock invoice generated (Gemini AI not configured)",
                "status": "draft",
                "generated_by": "mock",
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Error generating mock invoice: {str(e)}")
            raise
    
    async def save_draft(self, draft: Dict[str, Any]) -> str:
        """Save invoice draft to database"""
        try:
            # Add draft-specific metadata
            draft["created_at"] = datetime.now()
            draft["updated_at"] = datetime.now()
            
            result = await self.db.invoice_drafts.insert_one(draft)
            draft_id = str(result.inserted_id)
            
            self.logger.info(f"Saved invoice draft: {draft_id}")
            return draft_id
            
        except Exception as e:
            self.logger.error(f"Error saving draft: {str(e)}")
            raise
    
    async def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice draft by ID"""
        try:
            draft = await self.db.invoice_drafts.find_one({"_id": ObjectId(draft_id)})
            if draft:
                draft["_id"] = str(draft["_id"])
            return draft
        except Exception as e:
            self.logger.error(f"Error getting draft: {str(e)}")
            return None
    
    async def update_draft(self, draft_id: str, updates: Dict[str, Any]) -> bool:
        """Update invoice draft"""
        try:
            updates["updated_at"] = datetime.now()
            result = await self.db.invoice_drafts.update_one(
                {"_id": ObjectId(draft_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating draft: {str(e)}")
            return False
    
    async def delete_draft(self, draft_id: str) -> bool:
        """Delete invoice draft"""
        try:
            result = await self.db.invoice_drafts.delete_one({"_id": ObjectId(draft_id)})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting draft: {str(e)}")
            return False
    
    async def list_drafts(self, customer_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List invoice drafts, optionally filtered by customer"""
        try:
            query = {}
            if customer_id:
                query["customer_id"] = customer_id
            
            drafts = await self.db.invoice_drafts.find(query).sort(
                "created_at", -1
            ).limit(limit).to_list(limit)
            
            # Convert ObjectId to string
            for draft in drafts:
                draft["_id"] = str(draft["_id"])
            
            return drafts
        except Exception as e:
            self.logger.error(f"Error listing drafts: {str(e)}")
            return []
    
    async def convert_draft_to_invoice(self, draft_id: str) -> str:
        """Convert a draft to an actual invoice"""
        try:
            draft = await self.get_draft(draft_id)
            if not draft:
                raise ValueError(f"Draft {draft_id} not found")
            
            # Generate invoice ID
            count = await self.db.invoices.count_documents({})
            invoice_id = f"INV-{count + 1:04d}"
            
            # Create invoice from draft
            invoice = {
                "invoice_id": invoice_id,
                "customer_id": draft["customer_id"],
                "customer_name": draft["customer_name"],
                "issue_date": draft["issue_date"],
                "due_date": draft["due_date"],
                "items": draft["items"],
                "amount": draft["total_amount"],
                "paid_amount": 0,
                "status": "pending",
                "currency": draft.get("currency", "KES"),
                "notes": draft.get("notes", ""),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            
            # Insert invoice
            await self.db.invoices.insert_one(invoice)
            
            # Update customer totals
            await self._update_customer_totals(draft["customer_id"])
            
            # Delete the draft
            await self.delete_draft(draft_id)
            
            self.logger.info(f"Converted draft {draft_id} to invoice {invoice_id}")
            return invoice_id
            
        except Exception as e:
            self.logger.error(f"Error converting draft to invoice: {str(e)}")
            raise
    
    async def _update_customer_totals(self, customer_id: str):
        """Update customer financial totals after creating invoice"""
        try:
            # Recalculate from invoices
            pipeline = [
                {"$match": {"customer_id": customer_id}},
                {"$group": {
                    "_id": None,
                    "total_invoices": {"$sum": 1},
                    "total_billed": {"$sum": "$amount"},
                    "total_paid": {"$sum": "$paid_amount"},
                }}
            ]
            
            result = await self.db.invoices.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                outstanding = stats["total_billed"] - stats["total_paid"]
                
                await self.db.customers.update_one(
                    {"customer_id": customer_id},
                    {"$set": {
                        "total_invoices": stats["total_invoices"],
                        "total_billed": stats["total_billed"],
                        "total_paid": stats["total_paid"],
                        "outstanding_amount": outstanding,
                        "updated_at": datetime.now(),
                    }}
                )
        except Exception as e:
            self.logger.error(f"Error updating customer totals: {str(e)}")
