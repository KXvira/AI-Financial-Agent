"""
Customer Statement Service
Generates detailed transaction history and balance reports for individual customers
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from database.mongodb import Database

class CustomerStatementService:
    """Service for generating customer statements"""
    
    def __init__(self, db: Database):
        self.db = db
        
    async def generate_customer_statement(
        self,
        customer_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_paid: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a detailed statement for a specific customer
        
        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            include_paid: Include paid invoices/transactions
            
        Returns:
            Customer statement with transaction history and balance details
        """
        # Parse dates
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
            
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            # Default to last 90 days
            start = end - timedelta(days=90)
        
        # Get customer details (customer_id can be MongoDB _id or customer_id UUID)
        customer = None
        
        # Try as MongoDB ObjectId first
        try:
            customer = await self.db.customers.find_one({"_id": ObjectId(customer_id)})
        except:
            pass
        
        # If not found, try as customer_id UUID
        if not customer:
            customer = await self.db.customers.find_one({"customer_id": customer_id})
        
        if not customer:
            return {
                "error": "Customer not found",
                "customer_id": customer_id
            }
        
        # Get the actual customer_id (UUID) for queries
        actual_customer_id = customer.get("customer_id")
        
        # Format dates as strings for comparison (data stores dates as YYYY-MM-DD strings)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        
        # Get invoices for customer (normalized schema) - use issue_date not date_issued
        invoice_match = {
            "customer_id": actual_customer_id,
            "issue_date": {"$gte": start_str, "$lte": end_str}
        }
        
        if not include_paid:
            invoice_match["status"] = {"$ne": "paid"}
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        # Get invoice IDs for payment lookup
        invoice_ids = [inv.get("invoice_id") for inv in invoices if inv.get("invoice_id")]
        
        # Calculate invoice totals from invoice_items (normalized schema)
        for invoice in invoices:
            invoice_id = invoice.get("invoice_id")
            # Get invoice items for this invoice
            items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
            # Calculate total from items - use "line_total" field
            calculated_total = sum(item.get("line_total", item.get("total", 0)) for item in items)
            # Store calculated total in invoice dict (don't modify database)
            invoice["calculated_total"] = calculated_total if calculated_total > 0 else invoice.get("total", invoice.get("total_amount", 0))
        
        # Get payments for customer (use payments collection, not transactions)
        # Payment dates are also stored as strings in YYYY-MM-DD format
        payment_match = {
            "$or": [
                {"customer_id": actual_customer_id},
                {"invoice_id": {"$in": invoice_ids}}
            ],
            "payment_date": {"$gte": start_str, "$lte": end_str},
            "status": {"$in": ["completed", "paid", "success"]}
        }
        
        payments = await self.db.payments.find(payment_match).to_list(length=None)
        
        # Calculate balances
        opening_balance = await self._calculate_opening_balance(actual_customer_id, start)
        
        # Use calculated totals from invoice_items for accurate amounts
        total_invoiced = sum(inv.get("calculated_total", 0) for inv in invoices)
        total_paid = sum(pay.get("amount", 0) for pay in payments)
        
        current_balance = opening_balance + total_invoiced - total_paid
        
        # Prepare transaction history
        transactions = []
        
        # Add invoices - use issue_date (string format YYYY-MM-DD)
        for invoice in invoices:
            transactions.append({
                "date": invoice.get("issue_date", datetime.now().strftime("%Y-%m-%d")),  # Use issue_date not date_issued
                "type": "invoice",
                "reference": invoice.get("invoice_number", invoice.get("invoice_id", "Unknown")),
                "description": f"Invoice {invoice.get('invoice_number', invoice.get('invoice_id', 'N/A'))}",
                "invoice_id": invoice.get("invoice_id", ""),
                "amount": invoice.get("calculated_total", 0),  # Use calculated total from invoice_items
                "payment": 0,
                "balance": 0,  # Will calculate running balance
                "status": invoice.get("status", "unknown"),
                "due_date": invoice.get("due_date")  # Already in string format
            })
        
        # Add payments - use payment_date (string format YYYY-MM-DD)
        for payment in payments:
            transactions.append({
                "date": payment.get("payment_date", datetime.now().strftime("%Y-%m-%d")),  # payment_date is string
                "type": "payment",
                "reference": payment.get("transaction_reference", "Unknown"),  # Normalized field
                "description": f"Payment - {payment.get('payment_method', 'Payment')}",
                "invoice_id": payment.get("invoice_id", ""),
                "amount": 0,
                "payment": payment.get("amount", 0),
                "balance": 0,  # Will calculate running balance
                "status": payment.get("status", "completed"),
                "due_date": None
            })
        
        # Sort by date (dates are already strings in YYYY-MM-DD format, so they sort correctly)
        transactions.sort(key=lambda x: x["date"])
        
        # Calculate running balance
        running_balance = opening_balance
        for txn in transactions:
            running_balance += txn["amount"] - txn["payment"]
            txn["balance"] = round(running_balance, 2)
            # Dates are already strings, no conversion needed
        
        # Get aging breakdown
        aging = await self._calculate_aging(customer_id)
        
        # Calculate summary metrics
        overdue_invoices = [inv for inv in invoices if inv.get("status") == "overdue"]
        overdue_amount = sum(inv.get("total_amount", 0) - inv.get("amount_paid", 0) for inv in overdue_invoices)
        
        paid_invoices = [inv for inv in invoices if inv.get("status") == "paid"]
        pending_invoices = [inv for inv in invoices if inv.get("status") not in ["paid", "cancelled", "refunded"]]
        
        return {
            "customer": {
                "id": customer_id,
                "name": customer.get("name", "Unknown"),
                "email": customer.get("email"),
                "phone": customer.get("phone_number") or customer.get("phone"),
                "address": customer.get("address"),
                "city": customer.get("city"),
                "country": customer.get("country", "Kenya")
            },
            "statement_period": {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "days": (end - start).days
            },
            "summary": {
                "opening_balance": round(opening_balance, 2),
                "total_invoiced": round(total_invoiced, 2),
                "total_paid": round(total_paid, 2),
                "closing_balance": round(current_balance, 2),
                "total_invoices": len(invoices),
                "paid_invoices": len(paid_invoices),
                "pending_invoices": len(pending_invoices),
                "overdue_invoices": len(overdue_invoices),
                "overdue_amount": round(overdue_amount, 2)
            },
            "aging": aging,
            "transactions": transactions,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _calculate_opening_balance(self, customer_id: str, date: datetime) -> float:
        """Calculate opening balance before the statement period"""
        # Get all invoices before the date (normalized schema)
        invoice_match = {
            "customer_id": customer_id,
            "date_issued": {"$lt": date}
        }
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        # Calculate totals from invoice_items for accurate amounts
        total_invoiced = 0
        for invoice in invoices:
            invoice_id = invoice.get("invoice_id")
            items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
            # Use "line_total" field from invoice_items
            calculated_total = sum(item.get("line_total", item.get("total", 0)) for item in items)
            total_invoiced += calculated_total if calculated_total > 0 else invoice.get("total", invoice.get("total_amount", 0))
        
        # Get all payments before the date
        invoice_ids = [inv.get("invoice_id") for inv in invoices if inv.get("invoice_id")]
        payment_match = {
            "$or": [
                {"customer_id": customer_id},
                {"invoice_id": {"$in": invoice_ids}}
            ],
            "payment_date": {"$lt": date},
            "status": {"$in": ["completed", "paid", "success"]}
        }
        
        payments = await self.db.payments.find(payment_match).to_list(length=None)
        total_paid = sum(pay.get("amount", 0) for pay in payments)
        
        return total_invoiced - total_paid
    
    async def _calculate_aging(self, customer_id: str) -> Dict[str, float]:
        """Calculate aging buckets for customer"""
        now = datetime.now()
        
        # Get all outstanding invoices (normalized schema)
        invoice_match = {
            "customer_id": customer_id,
            "status": {"$nin": ["paid", "cancelled", "refunded"]}
        }
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        aging = {
            "current": 0,
            "1-30_days": 0,
            "31-60_days": 0,
            "61-90_days": 0,
            "over_90_days": 0
        }
        
        for invoice in invoices:
            # Calculate invoice total from invoice_items (normalized schema)
            invoice_id = invoice.get("invoice_id")
            items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
            # Calculate total from items - use "line_total" field
            calculated_total = sum(item.get("line_total", item.get("total", 0)) for item in items)
            invoice_total = calculated_total if calculated_total > 0 else invoice.get("total", invoice.get("total_amount", 0))
            
            outstanding = invoice_total - invoice.get("amount_paid", 0)
            due_date = invoice.get("due_date")
            
            if not due_date:
                aging["current"] += outstanding
                continue
            
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            days_overdue = (now - due_date).days
            
            if days_overdue <= 0:
                aging["current"] += outstanding
            elif days_overdue <= 30:
                aging["1-30_days"] += outstanding
            elif days_overdue <= 60:
                aging["31-60_days"] += outstanding
            elif days_overdue <= 90:
                aging["61-90_days"] += outstanding
            else:
                aging["over_90_days"] += outstanding
        
        # Round all values
        for key in aging:
            aging[key] = round(aging[key], 2)
        
        return aging
    
    async def get_customer_list(self) -> List[Dict[str, Any]]:
        """Get list of all customers with their outstanding balances using aggregation"""
        
        # Use aggregation pipeline to calculate outstanding balances efficiently
        pipeline = [
            {
                "$lookup": {
                    "from": "invoices",
                    "localField": "customer_id",
                    "foreignField": "customer_id",
                    "as": "invoices"
                }
            },
            {
                "$addFields": {
                    "outstanding_invoices": {
                        "$filter": {
                            "input": "$invoices",
                            "as": "inv",
                            "cond": {
                                "$not": {
                                    "$in": ["$$inv.status", ["paid", "cancelled", "refunded"]]
                                }
                            }
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "outstanding_balance": {
                        "$sum": {
                            "$map": {
                                "input": "$outstanding_invoices",
                                "as": "inv",
                                "in": {
                                    "$subtract": [
                                        {"$ifNull": ["$$inv.total_amount", 0]},
                                        {"$ifNull": ["$$inv.amount_paid", 0]}
                                    ]
                                }
                            }
                        }
                    },
                    "invoice_count": {"$size": "$outstanding_invoices"}
                }
            },
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "name": 1,
                    "email": 1,
                    "phone": {"$ifNull": ["$phone", "$phone_number"]},
                    "outstanding_balance": {"$round": ["$outstanding_balance", 2]},
                    "invoice_count": 1,
                    "_id": 0  # Exclude _id from result to avoid ObjectId serialization issue
                }
            },
            {
                "$sort": {"outstanding_balance": -1}
            }
        ]
        
        result = await self.db.customers.aggregate(pipeline).to_list(length=None)
        
        # Format result - ensure proper types
        for customer in result:
            customer["name"] = customer.get("name", "Unknown")
            customer["outstanding_balance"] = round(float(customer.get("outstanding_balance", 0)), 2)
            customer["invoice_count"] = int(customer.get("invoice_count", 0))
        
        return result
