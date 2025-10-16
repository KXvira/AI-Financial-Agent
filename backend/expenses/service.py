"""
Expense Service - Business logic for expense management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from database.mongodb import Database
from .models import ExpenseData, ExpenseSummary, ExpenseStats

logger = logging.getLogger("financial-agent.expenses")


class ExpenseService:
    """Service for managing expenses from receipts"""
    
    def __init__(self, db: Database):
        self.db = db
        self.receipts = db.db["receipts"]
    
    async def get_expense_summary(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> ExpenseSummary:
        """
        Get expense summary from receipts collection
        
        Queries for:
        1. Expense-type receipts (receipt_type: "expense")
        2. OCR-scanned receipts with expense data
        3. Refund receipts (also expenses)
        """
        try:
            # Default to last 12 months if no dates provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            # Get current month start
            month_start = datetime(end_date.year, end_date.month, 1)
            
            logger.info(f"Fetching expenses from {start_date} to {end_date}")
            
            # Query filters for different expense types
            date_filter = {
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            month_filter = {
                "created_at": {"$gte": month_start, "$lte": end_date}
            }
            
            # Get all expense receipts (combining expense type and OCR receipts with expense data)
            expense_match = {
                "$or": [
                    {"receipt_type": "expense"},
                    {"receipt_type": "refund"},
                    {"ocr_data.extracted_data.total_amount": {"$exists": True}}
                ],
                **date_filter
            }
            
            logger.info(f"Querying expenses with filter: {expense_match}")
            
            all_expenses = await self.receipts.find(expense_match).to_list(None)
            
            logger.info(f"Raw query returned {len(all_expenses)} receipts")
            
            # Calculate totals
            total_expenses = 0.0
            monthly_total = 0.0
            category_summary = {}
            recent_expenses = []
            
            for receipt in all_expenses:
                # Determine amount - check OCR data first as it's most common
                amount = 0.0
                
                # Priority 1: OCR extracted data (most reliable)
                if receipt.get("ocr_data"):
                    amount = receipt["ocr_data"]["extracted_data"].get("total_amount", 0)
                
                # Priority 2: Tax breakdown (for manual receipts)
                elif receipt.get("tax_breakdown"):
                    tax_breakdown = receipt["tax_breakdown"]
                    amount = tax_breakdown.get("subtotal", 0) + tax_breakdown.get("vat_amount", 0)
                
                # Priority 3: Line items (for itemized receipts)
                elif receipt.get("line_items"):
                    line_items = receipt["line_items"]
                    amount = sum(item.get("total", 0) for item in line_items)
                
                if amount > 0:
                    total_expenses += amount
                    
                    # Check if in current month
                    created_at = receipt.get("created_at", datetime.utcnow())
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    if created_at >= month_start:
                        monthly_total += amount
                    
                    # Category summary
                    category = "Uncategorized"
                    if receipt.get("ocr_data"):
                        # Try to get category from OCR data
                        category = receipt["ocr_data"]["extracted_data"].get("merchant_name", "Uncategorized")
                    elif receipt.get("line_items") and len(receipt["line_items"]) > 0:
                        # Use first line item description as category
                        category = receipt["line_items"][0].get("description", "Uncategorized")
                    
                    category_summary[category] = category_summary.get(category, 0) + amount
                    
                    # Add to recent expenses (for list display)
                    vendor = "Unknown"
                    if receipt.get("ocr_data"):
                        vendor = receipt["ocr_data"]["extracted_data"].get("merchant_name", "Unknown")
                    elif receipt.get("customer"):
                        vendor = receipt["customer"].get("name", "Unknown")
                    
                    recent_expenses.append({
                        "id": str(receipt.get("_id", "")),
                        "date": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
                        "vendor": vendor,
                        "amount": amount,
                        "category": category,
                        "status": receipt.get("status", "generated"),
                        "receipt_number": receipt.get("receipt_number", ""),
                        "payment_method": receipt.get("payment_method", ""),
                        "description": receipt.get("line_items", [{}])[0].get("description", "") if receipt.get("line_items") else ""
                    })
            
            # Sort recent expenses by date (newest first)
            recent_expenses.sort(key=lambda x: x["date"], reverse=True)
            recent_expenses = recent_expenses[:limit]
            
            # Convert to ExpenseData objects
            expense_data_list = [ExpenseData(**exp) for exp in recent_expenses]
            
            logger.info(f"Found {len(all_expenses)} expense receipts, total: KES {total_expenses:,.2f}")
            
            return ExpenseSummary(
                totalExpenses=round(total_expenses, 2),
                totalReceipts=len(all_expenses),
                monthlyTotal=round(monthly_total, 2),
                categorySummary={k: round(v, 2) for k, v in category_summary.items()},
                recentExpenses=expense_data_list
            )
            
        except Exception as e:
            logger.error(f"Error fetching expense summary: {str(e)}", exc_info=True)
            # Return empty summary on error
            return ExpenseSummary(
                totalExpenses=0.0,
                totalReceipts=0,
                monthlyTotal=0.0,
                categorySummary={},
                recentExpenses=[]
            )
    
    async def get_expense_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ExpenseStats:
        """Get detailed expense statistics"""
        try:
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            date_filter = {
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            # Build aggregation pipeline for expense receipts
            expense_pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"receipt_type": "expense"},
                            {"receipt_type": "refund"},
                            {"ocr_data.extracted_data.total_amount": {"$exists": True}}
                        ],
                        **date_filter
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": {
                            "$cond": [
                                {"$gt": ["$ocr_data.extracted_data.total_amount", 0]},
                                "$ocr_data.extracted_data.total_amount",
                                {"$add": ["$tax_breakdown.subtotal", "$tax_breakdown.vat_amount"]}
                            ]
                        }},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = await self.receipts.aggregate(expense_pipeline).to_list(None)
            
            total_amount = result[0]["total"] if result and result[0].get("total") else 0.0
            total_count = result[0]["count"] if result and result[0].get("count") else 0
            
            return ExpenseStats(
                total_amount=round(total_amount, 2),
                total_count=total_count,
                by_category={},
                by_payment_method={},
                average_expense=round(total_amount / total_count, 2) if total_count > 0 else 0.0,
                period_start=start_date,
                period_end=end_date
            )
            
        except Exception as e:
            logger.error(f"Error fetching expense stats: {str(e)}", exc_info=True)
            return ExpenseStats(
                total_amount=0.0,
                total_count=0,
                by_category={},
                by_payment_method={},
                average_expense=0.0,
                period_start=start_date or datetime.utcnow(),
                period_end=end_date or datetime.utcnow()
            )
