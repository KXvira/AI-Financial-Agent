"""
Customer Statement Service
Generates detailed transaction history and balance reports for individual customers
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
        
        # Get customer details
        customer = await self.db.customers.find_one({"_id": customer_id})
        
        if not customer:
            # Try to find by customer_id field
            customer = await self.db.customers.find_one({"customer_id": customer_id})
        
        if not customer:
            return {
                "error": "Customer not found",
                "customer_id": customer_id
            }
        
        # Get invoices for customer
        invoice_match = {
            "$or": [
                {"customer_id": customer_id},
                {"customer.id": customer_id},
                {"customer.customer_id": customer_id}
            ],
            "date_issued": {"$gte": start, "$lte": end}
        }
        
        if not include_paid:
            invoice_match["status"] = {"$ne": "paid"}
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        # Get payments for customer
        payment_match = {
            "$or": [
                {"customer_id": customer_id},
                {"reference": {"$regex": customer_id, "$options": "i"}},
                {"invoice_id": {"$in": [inv.get("_id") or inv.get("invoice_id") for inv in invoices]}}
            ],
            "timestamp": {"$gte": start, "$lte": end},
            "status": "completed"
        }
        
        payments = await self.db.transactions.find(payment_match).to_list(length=None)
        
        # Calculate balances
        opening_balance = await self._calculate_opening_balance(customer_id, start)
        
        total_invoiced = sum(inv.get("total_amount", 0) for inv in invoices)
        total_paid = sum(pay.get("amount", 0) for pay in payments)
        
        current_balance = opening_balance + total_invoiced - total_paid
        
        # Prepare transaction history
        transactions = []
        
        # Add invoices
        for invoice in invoices:
            transactions.append({
                "date": invoice.get("date_issued", datetime.now()),
                "type": "invoice",
                "reference": invoice.get("invoice_number", "Unknown"),
                "description": f"Invoice {invoice.get('invoice_number', 'N/A')}",
                "invoice_id": str(invoice.get("_id", "")),
                "amount": invoice.get("total_amount", 0),
                "payment": 0,
                "balance": 0,  # Will calculate running balance
                "status": invoice.get("status", "unknown"),
                "due_date": invoice.get("due_date")
            })
        
        # Add payments
        for payment in payments:
            transactions.append({
                "date": payment.get("timestamp", datetime.now()),
                "type": "payment",
                "reference": payment.get("mpesa_receipt_number") or payment.get("reference", "Unknown"),
                "description": f"Payment - {payment.get('payment_method', 'M-Pesa')}",
                "invoice_id": payment.get("invoice_id", ""),
                "amount": 0,
                "payment": payment.get("amount", 0),
                "balance": 0,  # Will calculate running balance
                "status": payment.get("status", "completed"),
                "due_date": None
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x["date"])
        
        # Calculate running balance
        running_balance = opening_balance
        for txn in transactions:
            running_balance += txn["amount"] - txn["payment"]
            txn["balance"] = round(running_balance, 2)
            # Convert datetime to string for JSON serialization
            txn["date"] = txn["date"].isoformat() if isinstance(txn["date"], datetime) else txn["date"]
            if txn.get("due_date"):
                txn["due_date"] = txn["due_date"].isoformat() if isinstance(txn["due_date"], datetime) else txn["due_date"]
        
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
        # Get all invoices before the date
        invoice_match = {
            "$or": [
                {"customer_id": customer_id},
                {"customer.id": customer_id},
                {"customer.customer_id": customer_id}
            ],
            "date_issued": {"$lt": date}
        }
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        total_invoiced = sum(inv.get("total_amount", 0) for inv in invoices)
        
        # Get all payments before the date
        invoice_ids = [str(inv.get("_id") or inv.get("invoice_id")) for inv in invoices]
        payment_match = {
            "$or": [
                {"customer_id": customer_id},
                {"invoice_id": {"$in": invoice_ids}}
            ],
            "timestamp": {"$lt": date},
            "status": "completed"
        }
        
        payments = await self.db.transactions.find(payment_match).to_list(length=None)
        total_paid = sum(pay.get("amount", 0) for pay in payments)
        
        return total_invoiced - total_paid
    
    async def _calculate_aging(self, customer_id: str) -> Dict[str, float]:
        """Calculate aging buckets for customer"""
        now = datetime.now()
        
        # Get all outstanding invoices
        invoice_match = {
            "$or": [
                {"customer_id": customer_id},
                {"customer.id": customer_id},
                {"customer.customer_id": customer_id}
            ],
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
            outstanding = invoice.get("total_amount", 0) - invoice.get("amount_paid", 0)
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
        """Get list of all customers with their outstanding balances"""
        customers = await self.db.customers.find({}).to_list(length=None)
        
        result = []
        for customer in customers:
            customer_id = str(customer.get("_id", "")) or customer.get("customer_id", "")
            
            # Get outstanding balance
            invoice_match = {
                "$or": [
                    {"customer_id": customer_id},
                    {"customer.id": customer_id},
                    {"customer.customer_id": customer_id}
                ],
                "status": {"$nin": ["paid", "cancelled", "refunded"]}
            }
            
            invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
            outstanding = sum(inv.get("total_amount", 0) - inv.get("amount_paid", 0) for inv in invoices)
            
            result.append({
                "id": customer_id,
                "name": customer.get("name", "Unknown"),
                "email": customer.get("email"),
                "phone": customer.get("phone_number") or customer.get("phone"),
                "outstanding_balance": round(outstanding, 2),
                "invoice_count": len(invoices)
            })
        
        # Sort by outstanding balance descending
        result.sort(key=lambda x: x["outstanding_balance"], reverse=True)
        
        return result
