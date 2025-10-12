"""
Data models for Tax Reports
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class VATTransaction(BaseModel):
    """Individual VAT transaction"""
    transaction_id: str
    date: str
    description: str
    amount: float
    vat_amount: float
    vat_rate: float
    type: str  # 'input' or 'output'
    category: str


class VATSummaryByRate(BaseModel):
    """VAT summary for a specific rate"""
    rate: float
    taxable_amount: float
    vat_amount: float
    transaction_count: int


class VATReport(BaseModel):
    """Complete VAT/Tax Report"""
    report_type: str = "tax_report"
    report_name: str = "VAT Summary Report"
    period_start: str
    period_end: str
    generated_at: str
    currency: str = "KES"
    
    # Output VAT (Sales)
    output_vat_total: float
    output_taxable_amount: float
    output_transaction_count: int
    output_by_rate: List[VATSummaryByRate]
    
    # Input VAT (Purchases)
    input_vat_total: float
    input_taxable_amount: float
    input_transaction_count: int
    input_by_rate: List[VATSummaryByRate]
    
    # Net VAT Position
    net_vat_payable: float  # If positive, owe to tax authority
    net_vat_refundable: float  # If negative, tax authority owes you
    
    # Detailed transactions
    output_transactions: List[VATTransaction] = []
    input_transactions: List[VATTransaction] = []
    
    # Compliance metrics
    compliance_status: str  # 'compliant', 'warning', 'overdue'
    filing_deadline: Optional[str] = None
    penalties_applicable: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "tax_report",
                "report_name": "VAT Summary Report",
                "period_start": "2024-01-01",
                "period_end": "2024-03-31",
                "generated_at": "2024-04-01T10:00:00",
                "currency": "KES",
                "output_vat_total": 640000.00,
                "output_taxable_amount": 4000000.00,
                "output_transaction_count": 50,
                "input_vat_total": 240000.00,
                "input_taxable_amount": 1500000.00,
                "input_transaction_count": 30,
                "net_vat_payable": 400000.00,
                "net_vat_refundable": 0.00,
                "compliance_status": "compliant",
                "filing_deadline": "2024-04-20",
                "penalties_applicable": False
            }
        }


class TaxPeriod(BaseModel):
    """Tax period configuration"""
    period_type: str  # 'monthly', 'quarterly', 'annual'
    start_date: str
    end_date: str
    filing_deadline: str
    status: str  # 'open', 'filed', 'overdue'


class ScheduledReport(BaseModel):
    """Scheduled report configuration"""
    schedule_id: str
    report_type: str
    report_name: str
    frequency: str  # 'daily', 'weekly', 'monthly', 'quarterly'
    schedule_time: str  # HH:MM format
    recipients: List[str]
    parameters: Dict[str, any] = {}
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_id": "sched_001",
                "report_type": "income_statement",
                "report_name": "Monthly P&L Report",
                "frequency": "monthly",
                "schedule_time": "09:00",
                "recipients": ["cfo@company.com", "accounting@company.com"],
                "parameters": {"auto_date_range": True},
                "enabled": True,
                "last_run": "2024-10-01T09:00:00",
                "next_run": "2024-11-01T09:00:00",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class EmailTemplate(BaseModel):
    """Email template for report delivery"""
    template_id: str
    template_name: str
    subject: str
    body_html: str
    body_text: str
    attachments_enabled: bool = True
    variables: List[str] = []  # Available variables like {report_name}, {period}
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "tmpl_001",
                "template_name": "Monthly Report Email",
                "subject": "{report_name} for {period}",
                "body_html": "<h1>Monthly Report</h1><p>Please find attached...</p>",
                "body_text": "Monthly Report - Please find attached...",
                "attachments_enabled": True,
                "variables": ["report_name", "period", "recipient_name"]
            }
        }
