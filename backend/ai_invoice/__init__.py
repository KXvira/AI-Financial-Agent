"""
AI Invoice Generation Module
"""

from backend.ai_invoice.router import router
from backend.ai_invoice.service import AIInvoiceService

__all__ = ["router", "AIInvoiceService"]
