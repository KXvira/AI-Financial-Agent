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
        
        # Get transactions
        txn_match = {
            "timestamp": {"$gte": start, "$lte": end},
            "status": "completed"  # Only completed transactions
        }
        
        if status:
            txn_match["reconciliation_status"] = status
        
        transactions = await self.db.transactions.find(txn_match).to_list(length=None)
        
        # Get invoices
        invoice_match = {
            "date_issued": {"$gte": start, "$lte": end}
        }
        
        invoices = await self.db.invoices.find(invoice_match).to_list(length=None)
        
        # Categorize transactions
        matched_txns = []
        unmatched_txns = []
        partial_txns = []
        needs_review_txns = []
        
        total_matched_amount = 0
        total_unmatched_amount = 0
        total_partial_amount = 0
        
        for txn in transactions:
            reconciliation_status = txn.get("reconciliation_status", "unmatched")
            amount = txn.get("amount", 0)
            
            txn_data = {
                "id": str(txn.get("_id", "")),
                "date": txn.get("timestamp").isoformat() if isinstance(txn.get("timestamp"), datetime) else txn.get("timestamp"),
                "reference": txn.get("mpesa_receipt_number") or txn.get("reference", "Unknown"),
                "amount": amount,
                "phone": txn.get("phone_number"),
                "description": txn.get("description", ""),
                "invoice_id": txn.get("invoice_id"),
                "invoice_number": txn.get("invoice_number"),
                "customer_name": txn.get("customer_name"),
                "reconciliation_status": reconciliation_status,
                "confidence_score": txn.get("confidence_score"),
                "needs_review": txn.get("needs_review", False),
                "review_reason": txn.get("review_reason")
            }
            
            if reconciliation_status == "matched":
                matched_txns.append(txn_data)
                total_matched_amount += amount
            elif reconciliation_status == "partial_match" or reconciliation_status == "partial":
                partial_txns.append(txn_data)
                total_partial_amount += amount
            elif reconciliation_status == "needs_review":
                needs_review_txns.append(txn_data)
            else:
                unmatched_txns.append(txn_data)
                total_unmatched_amount += amount
        
        # Get unmatched invoices (invoices without payments)
        unmatched_invoices = []
        for invoice in invoices:
            status = invoice.get("status", "")
            if status not in ["paid", "cancelled", "refunded"]:
                outstanding = invoice.get("total_amount", 0) - invoice.get("amount_paid", 0)
                if outstanding > 0:
                    unmatched_invoices.append({
                        "id": str(invoice.get("_id", "")),
                        "invoice_number": invoice.get("invoice_number", "Unknown"),
                        "date": invoice.get("date_issued").isoformat() if isinstance(invoice.get("date_issued"), datetime) else invoice.get("date_issued"),
                        "customer_name": invoice.get("customer_name") or invoice.get("customer", {}).get("name", "Unknown"),
                        "total_amount": invoice.get("total_amount", 0),
                        "amount_paid": invoice.get("amount_paid", 0),
                        "outstanding": outstanding,
                        "due_date": invoice.get("due_date").isoformat() if invoice.get("due_date") and isinstance(invoice.get("due_date"), datetime) else invoice.get("due_date"),
                        "status": status
                    })
        
        # Calculate statistics
        total_transactions = len(transactions)
        matched_count = len(matched_txns)
        unmatched_count = len(unmatched_txns)
        partial_count = len(partial_txns)
        needs_review_count = len(needs_review_txns)
        
        match_rate = (matched_count / total_transactions * 100) if total_transactions > 0 else 0
        
        # Get reconciliation issues
        issues = await self._identify_reconciliation_issues(
            transactions, 
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
        transactions: List[Dict[str, Any]],
        invoices: List[Dict[str, Any]],
        unmatched_txns: List[Dict[str, Any]],
        unmatched_invoices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify common reconciliation issues"""
        issues = []
        
        # Issue 1: Duplicate payments
        payment_refs = {}
        for txn in transactions:
            ref = txn.get("mpesa_receipt_number") or txn.get("reference")
            if ref in payment_refs:
                issues.append({
                    "type": "duplicate_payment",
                    "severity": "high",
                    "description": f"Duplicate payment reference: {ref}",
                    "reference": ref,
                    "transactions": [str(txn.get("_id")), str(payment_refs[ref].get("_id"))]
                })
            else:
                payment_refs[ref] = txn
        
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
