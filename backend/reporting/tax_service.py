"""
Tax calculation and reporting service
Handles VAT calculations, compliance checks, and tax reporting
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from .tax_models import (
    VATReport, VATTransaction, VATSummaryByRate,
    TaxPeriod, ScheduledReport, EmailTemplate
)


class TaxService:
    """Service for tax calculations and VAT reporting"""
    
    # Kenya VAT rates (configurable per country)
    STANDARD_VAT_RATE = 16.0  # Kenya standard VAT rate
    REDUCED_VAT_RATES = [0.0, 8.0]  # Zero-rated and reduced rate
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.invoices = db.invoices
        self.transactions = db.transactions
        
    async def generate_vat_report(
        self,
        start_date: str,
        end_date: str,
        include_transactions: bool = True
    ) -> VATReport:
        """
        Generate comprehensive VAT report for a period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            include_transactions: Whether to include detailed transactions
            
        Returns:
            VATReport with all VAT calculations
        """
        # Fetch invoices (output VAT - sales)
        invoices = await self.invoices.find({
            "invoice_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": {"$in": ["paid", "partially_paid"]}
        }).to_list(None)
        
        # Fetch transactions (input VAT - purchases)
        transactions = await self.transactions.find({
            "date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "type": {"$in": ["expense", "purchase"]}
        }).to_list(None)
        
        # Calculate output VAT (from sales/invoices)
        output_vat = self._calculate_output_vat(invoices, include_transactions)
        
        # Calculate input VAT (from purchases/expenses)
        input_vat = self._calculate_input_vat(transactions, include_transactions)
        
        # Calculate net position
        net_vat = output_vat['total'] - input_vat['total']
        net_payable = max(0, net_vat)
        net_refundable = abs(min(0, net_vat))
        
        # Determine compliance status and filing deadline
        compliance = self._check_compliance(start_date, end_date)
        
        return VATReport(
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now().isoformat(),
            output_vat_total=output_vat['total'],
            output_taxable_amount=output_vat['taxable_amount'],
            output_transaction_count=output_vat['count'],
            output_by_rate=output_vat['by_rate'],
            input_vat_total=input_vat['total'],
            input_taxable_amount=input_vat['taxable_amount'],
            input_transaction_count=input_vat['count'],
            input_by_rate=input_vat['by_rate'],
            net_vat_payable=net_payable,
            net_vat_refundable=net_refundable,
            output_transactions=output_vat.get('transactions', []),
            input_transactions=input_vat.get('transactions', []),
            compliance_status=compliance['status'],
            filing_deadline=compliance.get('deadline'),
            penalties_applicable=compliance.get('penalties', False)
        )
    
    def _calculate_output_vat(
        self,
        invoices: List[Dict],
        include_transactions: bool = False
    ) -> Dict:
        """Calculate VAT from sales (output VAT)"""
        total_vat = 0.0
        total_taxable = 0.0
        by_rate = {}
        transactions = []
        
        for invoice in invoices:
            # Calculate VAT for this invoice
            amount = float(invoice.get('amount_paid', invoice.get('total_amount', 0)))
            vat_rate = self._determine_vat_rate(invoice)
            
            # Calculate taxable amount and VAT
            taxable_amount = amount / (1 + vat_rate / 100)
            vat_amount = amount - taxable_amount
            
            total_vat += vat_amount
            total_taxable += taxable_amount
            
            # Group by rate
            rate_key = str(vat_rate)
            if rate_key not in by_rate:
                by_rate[rate_key] = {
                    'rate': vat_rate,
                    'taxable_amount': 0.0,
                    'vat_amount': 0.0,
                    'count': 0
                }
            by_rate[rate_key]['taxable_amount'] += taxable_amount
            by_rate[rate_key]['vat_amount'] += vat_amount
            by_rate[rate_key]['count'] += 1
            
            # Store detailed transaction if requested
            if include_transactions:
                transactions.append(VATTransaction(
                    transaction_id=str(invoice.get('_id', '')),
                    date=invoice.get('invoice_date', ''),
                    description=f"Invoice {invoice.get('invoice_number', 'N/A')} - {invoice.get('customer_name', 'Unknown')}",
                    amount=taxable_amount,
                    vat_amount=vat_amount,
                    vat_rate=vat_rate,
                    type='output',
                    category=invoice.get('category', 'sales')
                ))
        
        # Convert by_rate dict to list of VATSummaryByRate
        rate_summaries = [
            VATSummaryByRate(
                rate=data['rate'],
                taxable_amount=data['taxable_amount'],
                vat_amount=data['vat_amount'],
                transaction_count=data['count']
            )
            for data in by_rate.values()
        ]
        
        return {
            'total': total_vat,
            'taxable_amount': total_taxable,
            'count': len(invoices),
            'by_rate': rate_summaries,
            'transactions': transactions if include_transactions else []
        }
    
    def _calculate_input_vat(
        self,
        transactions: List[Dict],
        include_transactions: bool = False
    ) -> Dict:
        """Calculate VAT from purchases (input VAT - claimable)"""
        total_vat = 0.0
        total_taxable = 0.0
        by_rate = {}
        transaction_list = []
        
        for txn in transactions:
            # Calculate VAT for this transaction
            amount = float(txn.get('amount', 0))
            vat_rate = self._determine_vat_rate(txn)
            
            # Calculate taxable amount and VAT
            taxable_amount = amount / (1 + vat_rate / 100)
            vat_amount = amount - taxable_amount
            
            total_vat += vat_amount
            total_taxable += taxable_amount
            
            # Group by rate
            rate_key = str(vat_rate)
            if rate_key not in by_rate:
                by_rate[rate_key] = {
                    'rate': vat_rate,
                    'taxable_amount': 0.0,
                    'vat_amount': 0.0,
                    'count': 0
                }
            by_rate[rate_key]['taxable_amount'] += taxable_amount
            by_rate[rate_key]['vat_amount'] += vat_amount
            by_rate[rate_key]['count'] += 1
            
            # Store detailed transaction if requested
            if include_transactions:
                transaction_list.append(VATTransaction(
                    transaction_id=str(txn.get('_id', '')),
                    date=txn.get('date', ''),
                    description=txn.get('description', 'Purchase'),
                    amount=taxable_amount,
                    vat_amount=vat_amount,
                    vat_rate=vat_rate,
                    type='input',
                    category=txn.get('category', 'expense')
                ))
        
        # Convert by_rate dict to list
        rate_summaries = [
            VATSummaryByRate(
                rate=data['rate'],
                taxable_amount=data['taxable_amount'],
                vat_amount=data['vat_amount'],
                transaction_count=data['count']
            )
            for data in by_rate.values()
        ]
        
        return {
            'total': total_vat,
            'taxable_amount': total_taxable,
            'count': len(transactions),
            'by_rate': rate_summaries,
            'transactions': transaction_list if include_transactions else []
        }
    
    def _determine_vat_rate(self, document: Dict) -> float:
        """
        Determine VAT rate from document
        Can be enhanced with category-based logic
        """
        # Check if VAT rate is explicitly set
        if 'vat_rate' in document:
            return float(document['vat_rate'])
        
        # Check category for zero-rated items (exports, basic goods)
        category = document.get('category', '').lower()
        if category in ['export', 'medical', 'education', 'basic_food']:
            return 0.0
        
        # Default to standard rate
        return self.STANDARD_VAT_RATE
    
    def _check_compliance(self, start_date: str, end_date: str) -> Dict:
        """
        Check tax compliance status
        In Kenya, VAT is filed monthly by 20th of following month
        """
        try:
            end = datetime.fromisoformat(end_date)
            today = datetime.now()
            
            # Calculate filing deadline (20th of month after period end)
            if end.month == 12:
                deadline = datetime(end.year + 1, 1, 20)
            else:
                deadline = datetime(end.year, end.month + 1, 20)
            
            # Check if overdue
            if today > deadline:
                return {
                    'status': 'overdue',
                    'deadline': deadline.strftime('%Y-%m-%d'),
                    'penalties': True
                }
            
            # Check if approaching deadline (within 5 days)
            days_until_deadline = (deadline - today).days
            if days_until_deadline <= 5:
                return {
                    'status': 'warning',
                    'deadline': deadline.strftime('%Y-%m-%d'),
                    'penalties': False
                }
            
            return {
                'status': 'compliant',
                'deadline': deadline.strftime('%Y-%m-%d'),
                'penalties': False
            }
        except:
            return {
                'status': 'unknown',
                'deadline': None,
                'penalties': False
            }
    
    async def get_tax_periods(self, year: int) -> List[TaxPeriod]:
        """Get tax periods for a year (monthly for Kenya VAT)"""
        periods = []
        
        for month in range(1, 13):
            # Start date is first day of month
            start = datetime(year, month, 1)
            
            # End date is last day of month
            if month == 12:
                end = datetime(year, 12, 31)
            else:
                end = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Filing deadline is 20th of next month
            if month == 12:
                deadline = datetime(year + 1, 1, 20)
            else:
                deadline = datetime(year, month + 1, 20)
            
            # Determine status
            today = datetime.now()
            if today < end:
                status = 'open'
            elif today > deadline:
                status = 'overdue'
            else:
                status = 'open'
            
            periods.append(TaxPeriod(
                period_type='monthly',
                start_date=start.strftime('%Y-%m-%d'),
                end_date=end.strftime('%Y-%m-%d'),
                filing_deadline=deadline.strftime('%Y-%m-%d'),
                status=status
            ))
        
        return periods
    
    async def export_vat_report_for_filing(
        self,
        vat_report: VATReport
    ) -> Dict:
        """
        Format VAT report for tax authority filing
        Returns structured data ready for KRA iTax portal or similar
        """
        return {
            'filing_period': {
                'start': vat_report.period_start,
                'end': vat_report.period_end
            },
            'output_vat': {
                'total_sales': vat_report.output_taxable_amount,
                'vat_collected': vat_report.output_vat_total,
                'breakdown_by_rate': [
                    {
                        'rate': item.rate,
                        'taxable_sales': item.taxable_amount,
                        'vat_amount': item.vat_amount
                    }
                    for item in vat_report.output_by_rate
                ]
            },
            'input_vat': {
                'total_purchases': vat_report.input_taxable_amount,
                'vat_claimable': vat_report.input_vat_total,
                'breakdown_by_rate': [
                    {
                        'rate': item.rate,
                        'taxable_purchases': item.taxable_amount,
                        'vat_amount': item.vat_amount
                    }
                    for item in vat_report.input_by_rate
                ]
            },
            'net_position': {
                'net_vat_payable': vat_report.net_vat_payable,
                'net_vat_refundable': vat_report.net_vat_refundable,
                'payment_due': vat_report.net_vat_payable > 0
            },
            'compliance': {
                'status': vat_report.compliance_status,
                'filing_deadline': vat_report.filing_deadline,
                'penalties_applicable': vat_report.penalties_applicable
            },
            'generated_at': vat_report.generated_at
        }
