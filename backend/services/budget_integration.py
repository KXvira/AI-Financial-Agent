"""
Budget Integration Utilities
Helper functions to integrate budget tracking with expense/receipt creation
"""
import logging
from datetime import date, datetime
from typing import Optional, Dict, Any
from backend.services.budget_service import BudgetService

logger = logging.getLogger("financial-agent.budget.integration")


async def sync_expense_with_budgets(
    category: str,
    amount: float,
    transaction_date: Optional[date] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sync an expense with budget tracking
    
    This function should be called whenever:
    - A new expense is created
    - A receipt is uploaded
    - An expense amount is modified
    
    Args:
        category: Expense category (e.g., "Marketing", "Salaries")
        amount: Expense amount
        transaction_date: Date of the transaction
        user_id: Optional user ID for multi-user systems
        
    Returns:
        Dictionary with budget update results and any alerts
    """
    try:
        budget_service = BudgetService()
        
        result = await budget_service.process_expense_transaction(
            category=category,
            amount=amount,
            transaction_date=transaction_date or date.today(),
            user_id=user_id
        )
        
        # Log if any budgets were affected
        if result.get("updated_budgets", 0) > 0:
            logger.info(
                f"Expense synced: {category} ${amount:.2f} - "
                f"Updated {result['updated_budgets']} budget(s)"
            )
            
            # Log alerts if any
            if result.get("alerts"):
                for alert in result["alerts"]:
                    logger.warning(
                        f"Budget alert: {alert.get('category')} - {alert.get('message')}"
                    )
        else:
            logger.debug(
                f"No active budgets found for category: {category}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error syncing expense with budgets: {str(e)}")
        return {
            "updated_budgets": 0,
            "budget_ids": [],
            "alerts": [],
            "error": str(e)
        }


def extract_category_from_receipt(receipt_data: Dict[str, Any]) -> str:
    """
    Extract a meaningful category from receipt data
    
    Args:
        receipt_data: Receipt dictionary with OCR or manual data
        
    Returns:
        Category string
    """
    # Priority 1: Check customer name (often used as category for expenses)
    if receipt_data.get("customer"):
        customer_name = receipt_data["customer"].get("name")
        if customer_name and customer_name != "Walk-in Customer":
            return customer_name
    
    # Priority 2: Try OCR data
    if receipt_data.get("ocr_data"):
        ocr_data = receipt_data["ocr_data"]
        extracted = ocr_data.get("extracted_data", {})
        
        # Try merchant category if available
        if extracted.get("category"):
            return extracted["category"]
        
        # Try merchant name as category
        if extracted.get("merchant_name"):
            return extracted["merchant_name"]
    
    # Priority 3: Try line items
    if receipt_data.get("line_items") and len(receipt_data["line_items"]) > 0:
        first_item = receipt_data["line_items"][0]
        if first_item.get("category"):
            return first_item["category"]
    
    # Default category
    return "Uncategorized"


def extract_amount_from_receipt(receipt_data: Dict[str, Any]) -> float:
    """
    Extract total amount from receipt data
    
    Args:
        receipt_data: Receipt dictionary
        
    Returns:
        Total amount as float
    """
    amount = 0.0
    
    # Priority 1: OCR extracted data
    if receipt_data.get("ocr_data"):
        amount = receipt_data["ocr_data"]["extracted_data"].get("total_amount", 0)
    
    # Priority 2: Tax breakdown
    elif receipt_data.get("tax_breakdown"):
        tax_breakdown = receipt_data["tax_breakdown"]
        amount = tax_breakdown.get("subtotal", 0) + tax_breakdown.get("vat_amount", 0)
    
    # Priority 3: Line items sum
    elif receipt_data.get("line_items"):
        amount = sum(item.get("total", 0) for item in receipt_data["line_items"])
    
    return float(amount)


def extract_date_from_receipt(receipt_data: Dict[str, Any]) -> date:
    """
    Extract transaction date from receipt data
    
    Args:
        receipt_data: Receipt dictionary
        
    Returns:
        Transaction date
    """
    # Try OCR extracted date
    if receipt_data.get("ocr_data"):
        date_str = receipt_data["ocr_data"]["extracted_data"].get("date")
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except:
                pass
    
    # Try created_at
    if receipt_data.get("created_at"):
        created_at = receipt_data["created_at"]
        if isinstance(created_at, datetime):
            return created_at.date()
        elif isinstance(created_at, str):
            try:
                return datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
            except:
                pass
    
    # Default to today
    return date.today()
