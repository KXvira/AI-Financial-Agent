"""
Reconciliation Report Service
Generates reports on payment reconciliation status and unmatched transactions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.mongodb import Database

class ReconciliationReportService:
    """Service for generating reconciliation reports"""
    
    def __init__(self, db: Database):
        self.db = db
        
    async def generate_reconciliation_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None  # matched, unmatched, partial, needs_review
    ) -> Dict[str, Any]:
        """
        Generate reconciliation report showing payment matching status
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            status: Filter by reconciliation status
            
        Returns:
            Reconciliation report with matched/unmatched transactions
        """
        # Parse dates
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
            
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            # Default to last 30 days
            start = end - timedelta(days=30)
        
        # Format dates as strings for comparison (payments use string dates)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        
        # Get payments (not transactions) - this is the correct collection
        payment_match = {
            "payment_date": {"$gte": start_str, "$lte": end_str},
            "status": {"$in": ["completed", "pending"]}  # Include both completed and pending
        }
        
        # Note: We don't have reconciliation_status field, we use ai_matched and match_status instead
        if status:
            if status == "matched":
                payment_match["ai_matched"] = True
                payment_match["match_status"] = "correct"
            elif status == "unmatched":
                payment_match["ai_matched"] = False
        
        payments = await self.db.payments.find(payment_match).to_list(length=None)
        
        # Get invoices for the period - use issue_date not date_issued
        invoice_match = {
            "issue_date": {"$gte": start_str, "$lte": end_str}
        }
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        # Categorize payments based on AI matching results
        matched_txns = []
        unmatched_txns = []
        partial_txns = []
        needs_review_txns = []
        
        total_matched_amount = 0
        total_unmatched_amount = 0
        total_partial_amount = 0
        
        for payment in payments:
            # Use payment fields instead of transaction fields
            ai_matched = payment.get("ai_matched", False)
            match_status = payment.get("match_status", "unmatched")
            amount = payment.get("amount", 0)
            confidence = payment.get("match_confidence", 0)
            
            # Get customer name from payment or lookup
            customer_name = None
            if payment.get("customer_id"):
                customer = await self.db.customers.find_one({"customer_id": payment.get("customer_id")})
                if customer:
                    customer_name = customer.get("name")
            
            # Get invoice number if linked
            invoice_number = None
            if payment.get("invoice_id"):
                invoice = await self.db.invoices.find_one({"invoice_id": payment.get("invoice_id")})
                if invoice:
                    invoice_number = invoice.get("invoice_number")
            
            payment_data = {
                "id": str(payment.get("_id", "")),
                "date": payment.get("payment_date", ""),  # Already a string
                "reference": payment.get("transaction_reference", "Unknown"),
                "amount": amount,
                "payment_method": payment.get("payment_method", ""),
                "description": payment.get("notes", ""),
                "invoice_id": payment.get("invoice_id"),
                "invoice_number": invoice_number,
                "customer_name": customer_name,
                "reconciliation_status": match_status,
                "confidence_score": confidence,
                "needs_review": confidence < 0.7 if ai_matched else False,
                "review_reason": "Low confidence match" if (ai_matched and confidence < 0.7) else None
            }
            
            if ai_matched and match_status == "correct":
                matched_txns.append(payment_data)
                total_matched_amount += amount
            elif match_status == "partial_match" or match_status == "partial":
                partial_txns.append(payment_data)
                total_partial_amount += amount
            elif ai_matched and confidence < 0.7:
                needs_review_txns.append(payment_data)
            else:
                unmatched_txns.append(payment_data)
                total_unmatched_amount += amount
        
        # Get unmatched invoices (invoices without payments)
        unmatched_invoices = []
        for invoice in invoices:
            status = invoice.get("status", "")
            if status not in ["paid", "cancelled", "refunded"]:
                outstanding = invoice.get("total_amount", 0) - invoice.get("amount_paid", 0)
                if outstanding > 0:
                    # Get customer name
                    customer_name = "Unknown"
                    if invoice.get("customer_id"):
                        customer = await self.db.customers.find_one({"customer_id": invoice.get("customer_id")})
                        if customer:
                            customer_name = customer.get("name", "Unknown")
                    
                    unmatched_invoices.append({
                        "id": str(invoice.get("_id", "")),
                        "invoice_number": invoice.get("invoice_number", "Unknown"),
                        "date": invoice.get("issue_date", ""),  # Already a string
                        "customer_name": customer_name,
                        "total_amount": invoice.get("total_amount", 0),
                        "amount_paid": invoice.get("amount_paid", 0),
                        "outstanding": outstanding,
                        "due_date": invoice.get("due_date", ""),  # Already a string
                        "status": status
                    })
        
        # Calculate statistics
        total_transactions = len(payments)  # Changed from transactions to payments
        matched_count = len(matched_txns)
        unmatched_count = len(unmatched_txns)
        partial_count = len(partial_txns)
        needs_review_count = len(needs_review_txns)
        
        match_rate = (matched_count / total_transactions * 100) if total_transactions > 0 else 0
        
        # Get reconciliation issues
        issues = await self._identify_reconciliation_issues(
            payments,  # Changed from transactions to payments
            invoices, 
            unmatched_txns,
            unmatched_invoices
        )
        
        return {
            "report_period": {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "days": (end - start).days
            },
            "summary": {
                "total_transactions": total_transactions,
                "matched_count": matched_count,
                "unmatched_count": unmatched_count,
                "partial_count": partial_count,
                "needs_review_count": needs_review_count,
                "match_rate": round(match_rate, 2),
                "total_matched_amount": round(total_matched_amount, 2),
                "total_unmatched_amount": round(total_unmatched_amount, 2),
                "total_partial_amount": round(total_partial_amount, 2),
                "unmatched_invoices": len(unmatched_invoices),
                "total_outstanding": round(sum(inv["outstanding"] for inv in unmatched_invoices), 2)
            },
            "transactions": {
                "matched": matched_txns,
                "unmatched": unmatched_txns,
                "partial": partial_txns,
                "needs_review": needs_review_txns
            },
            "unmatched_invoices": unmatched_invoices,
            "issues": issues,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _identify_reconciliation_issues(
        self,
        payments: List[Dict[str, Any]],  # Changed from transactions
        invoices: List[Dict[str, Any]],
        unmatched_txns: List[Dict[str, Any]],
        unmatched_invoices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify common reconciliation issues"""
        issues = []
        
        # Issue 1: Duplicate payments
        payment_refs = {}
        for payment in payments:  # Changed from txn to payment
            ref = payment.get("transaction_reference", "")
            if ref and ref in payment_refs:
                issues.append({
                    "type": "duplicate_payment",
                    "severity": "high",
                    "description": f"Duplicate payment reference: {ref}",
                    "reference": ref,
                    "transactions": [str(payment.get("_id")), str(payment_refs[ref].get("_id"))]
                })
            elif ref:
                payment_refs[ref] = payment
        
        # Issue 2: Large unmatched amounts
        large_unmatched = [txn for txn in unmatched_txns if txn["amount"] > 10000]
        if large_unmatched:
            issues.append({
                "type": "large_unmatched_payment",
                "severity": "high",
                "description": f"{len(large_unmatched)} unmatched payments over KES 10,000",
                "count": len(large_unmatched),
                "total_amount": round(sum(txn["amount"] for txn in large_unmatched), 2),
                "transactions": [txn["id"] for txn in large_unmatched]
            })
        
        # Issue 3: Old unmatched transactions
        now = datetime.now()
        old_unmatched = []
        for txn in unmatched_txns:
            txn_date_str = txn.get("date")
            if txn_date_str:
                if isinstance(txn_date_str, str):
                    txn_date = datetime.fromisoformat(txn_date_str.replace('Z', '+00:00'))
                else:
                    txn_date = txn_date_str
                days_old = (now - txn_date).days
                if days_old > 30:
                    old_unmatched.append(txn)
        
        if old_unmatched:
            issues.append({
                "type": "old_unmatched_transactions",
                "severity": "medium",
                "description": f"{len(old_unmatched)} unmatched transactions older than 30 days",
                "count": len(old_unmatched),
                "total_amount": round(sum(txn["amount"] for txn in old_unmatched), 2),
                "transactions": [txn["id"] for txn in old_unmatched]
            })
        
        # Issue 4: Overdue invoices
        overdue_invoices = []
        for inv in unmatched_invoices:
            due_date = inv.get("due_date")
            if due_date:
                if isinstance(due_date, str):
                    due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                if due_date < now:
                    overdue_invoices.append(inv)
        
        if overdue_invoices:
            issues.append({
                "type": "overdue_invoices",
                "severity": "high",
                "description": f"{len(overdue_invoices)} overdue invoices with no payments",
                "count": len(overdue_invoices),
                "total_amount": round(sum(inv["outstanding"] for inv in overdue_invoices), 2),
                "invoices": [inv["id"] for inv in overdue_invoices]
            })
        
        # Issue 5: Amount mismatches (partial payments that might need review)
        amount_mismatches = []
        for inv in invoices:
            total = inv.get("total_amount", 0)
            paid = inv.get("amount_paid", 0)
            if 0 < paid < total:
                diff = total - paid
                # Check if there's an unmatched payment close to this amount
                for txn in unmatched_txns:
                    if abs(txn["amount"] - diff) < 10:  # Within KES 10
                        amount_mismatches.append({
                            "invoice_id": str(inv.get("_id")),
                            "invoice_number": inv.get("invoice_number"),
                            "transaction_id": txn["id"],
                            "reference": txn["reference"],
                            "expected": diff,
                            "actual": txn["amount"],
                            "difference": abs(txn["amount"] - diff)
                        })
        
        if amount_mismatches:
            issues.append({
                "type": "potential_amount_mismatch",
                "severity": "medium",
                "description": f"{len(amount_mismatches)} potential amount mismatches requiring review",
                "count": len(amount_mismatches),
                "matches": amount_mismatches
            })
        
        return issues
    
    async def get_reconciliation_summary(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get high-level reconciliation summary for dashboard"""
        end = datetime.now()
        start = end - timedelta(days=days)
        
        # Get all completed transactions
        transactions = await self.db.transactions.find({
            "timestamp": {"$gte": start, "$lte": end},
            "status": "completed"
        }).to_list(length=None)
        
        # Count by status
        status_counts = {
            "matched": 0,
            "unmatched": 0,
            "partial": 0,
            "needs_review": 0
        }
        
        status_amounts = {
            "matched": 0,
            "unmatched": 0,
            "partial": 0,
            "needs_review": 0
        }
        
        for txn in transactions:
            status = txn.get("reconciliation_status", "unmatched")
            amount = txn.get("amount", 0)
            
            if status in status_counts:
                status_counts[status] += 1
                status_amounts[status] += amount
            elif status == "partial_match":
                status_counts["partial"] += 1
                status_amounts["partial"] += amount
            else:
                status_counts["unmatched"] += 1
                status_amounts["unmatched"] += amount
        
        total = len(transactions)
        match_rate = (status_counts["matched"] / total * 100) if total > 0 else 0
        
        return {
            "period_days": days,
            "total_transactions": total,
            "status_counts": status_counts,
            "status_amounts": {k: round(v, 2) for k, v in status_amounts.items()},
            "match_rate": round(match_rate, 2),
            "needs_attention": status_counts["needs_review"] + status_counts["unmatched"]
        }
