"""
Dashboard Service - Compute Real Statistics
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import (
    DashboardStats, DashboardData, RecentPayment, 
    RecentTransaction
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for computing dashboard statistics"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.invoices = db.invoices
        self.transactions = db.transactions
        self.receipts = db.receipts
    
    async def get_dashboard_stats(
        self, 
        user_id: Optional[str] = None,
        period_days: int = 30
    ) -> DashboardData:
        """
        Get complete dashboard statistics
        
        Args:
            user_id: User ID (optional - if None, returns stats for all users)
            period_days: Number of days for current period (default: 30)
        
        Returns:
            DashboardData with computed statistics
        """
        try:
            # Calculate date ranges
            now = datetime.utcnow()
            current_period_start = now - timedelta(days=period_days)
            previous_period_start = current_period_start - timedelta(days=period_days)
            
            # Get current period stats
            current_stats = await self._calculate_period_stats(
                user_id, 
                current_period_start, 
                now
            )
            
            # Get previous period stats for comparison
            previous_stats = await self._calculate_period_stats(
                user_id,
                previous_period_start,
                current_period_start
            )
            
            # Calculate percentage changes
            invoices_change = self._calculate_change_percent(
                current_stats['invoices_total'],
                previous_stats['invoices_total']
            )
            
            payments_change = self._calculate_change_percent(
                current_stats['payments_total'],
                previous_stats['payments_total']
            )
            
            outstanding_change = self._calculate_change_percent(
                current_stats['outstanding'],
                previous_stats['outstanding']
            )
            
            cash_flow_change = self._calculate_change_percent(
                current_stats['daily_cash_flow'],
                previous_stats['daily_cash_flow']
            )
            
            expenses_change = self._calculate_change_percent(
                current_stats['expenses_total'],
                previous_stats['expenses_total']
            )
            
            # Build statistics
            statistics = DashboardStats(
                total_invoices=current_stats['invoices_total'],
                total_invoices_count=current_stats['invoices_count'],
                invoices_change_percent=invoices_change,
                payments_received=current_stats['payments_total'],
                payments_count=current_stats['payments_count'],
                payments_change_percent=payments_change,
                outstanding_balance=current_stats['outstanding'],
                outstanding_change_percent=outstanding_change,
                daily_cash_flow=current_stats['daily_cash_flow'],
                cash_flow_change_percent=cash_flow_change,
                period_start=current_period_start,
                period_end=now
            )
            
            # Get recent payments
            recent_payments = await self._get_recent_payments(user_id, limit=5)
            
            # Get recent transactions
            recent_transactions = await self._get_recent_transactions(user_id, limit=10)
            
            return DashboardData(
                statistics=statistics,
                recent_payments=recent_payments,
                recent_transactions=recent_transactions,
                total_expenses=current_stats['expenses_total'],
                expenses_change_percent=expenses_change
            )
            
        except Exception as e:
            logger.error(f"Error computing dashboard stats: {str(e)}")
            # Return empty stats on error
            return DashboardData(
                statistics=DashboardStats(),
                recent_payments=[],
                recent_transactions=[]
            )
    
    async def _calculate_period_stats(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Calculate statistics for a specific period"""
        
        # Base query filter
        date_filter = {
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Add user filter only if user_id is provided
        user_filter = {"user_id": user_id} if user_id else {}
        
        # Get invoices stats
        invoices_pipeline = [
            {"$match": {**user_filter, **date_filter}},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }}
        ]
        
        invoices_result = await self.invoices.aggregate(invoices_pipeline).to_list(None)
        invoices_total = invoices_result[0]['total'] if invoices_result else 0.0
        invoices_count = invoices_result[0]['count'] if invoices_result else 0
        
        # Get payments stats (from transactions with type='payment')
        payments_pipeline = [
            {"$match": {
                **user_filter,
                "type": "payment",
                "status": {"$in": ["completed", "success"]},
                **date_filter
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }}
        ]
        
        payments_result = await self.transactions.aggregate(payments_pipeline).to_list(None)
        payments_total = payments_result[0]['total'] if payments_result else 0.0
        payments_count = payments_result[0]['count'] if payments_result else 0
        
        # Get expenses stats (from receipts)
        expenses_pipeline = [
            {"$match": {
                **user_filter,
                "ocr_data.extracted_data.total_amount": {"$exists": True},
                **date_filter
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$ocr_data.extracted_data.total_amount"}
            }}
        ]
        
        expenses_result = await self.receipts.aggregate(expenses_pipeline).to_list(None)
        expenses_total = expenses_result[0]['total'] if expenses_result else 0.0
        
        # Calculate outstanding balance
        outstanding = invoices_total - payments_total
        
        # Calculate daily cash flow
        period_days = max((end_date - start_date).days, 1)
        daily_cash_flow = (payments_total - expenses_total) / period_days
        
        return {
            'invoices_total': invoices_total,
            'invoices_count': invoices_count,
            'payments_total': payments_total,
            'payments_count': payments_count,
            'expenses_total': expenses_total,
            'outstanding': outstanding,
            'daily_cash_flow': daily_cash_flow
        }
    
    def _calculate_change_percent(
        self, 
        current: float, 
        previous: float
    ) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        change = ((current - previous) / previous) * 100
        return round(change, 1)
    
    async def _get_recent_payments(
        self,
        user_id: Optional[str],
        limit: int = 5
    ) -> List[RecentPayment]:
        """Get recent payments"""
        try:
            query = {
                "type": "payment",
                "status": {"$in": ["completed", "success"]}
            }
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.transactions.find(query).sort("created_at", -1).limit(limit)
            
            payments = []
            async for doc in cursor:
                payments.append(RecentPayment(
                    reference=doc.get('transaction_id', doc.get('_id')),
                    client=doc.get('customer_name', doc.get('description', 'Unknown')),
                    amount=doc.get('amount', 0.0),
                    currency=doc.get('currency', 'KES'),
                    date=doc.get('created_at', datetime.utcnow()),
                    status=doc.get('status', 'completed')
                ))
            
            return payments
            
        except Exception as e:
            logger.error(f"Error fetching recent payments: {str(e)}")
            return []
    
    async def _get_recent_transactions(
        self,
        user_id: Optional[str],
        limit: int = 10
    ) -> List[RecentTransaction]:
        """Get recent transactions"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
                
            cursor = self.transactions.find(query).sort("created_at", -1).limit(limit)
            
            transactions = []
            async for doc in cursor:
                transactions.append(RecentTransaction(
                    id=str(doc.get('_id')),
                    type=doc.get('type', 'transaction'),
                    description=doc.get('description', 'Transaction'),
                    amount=doc.get('amount', 0.0),
                    currency=doc.get('currency', 'KES'),
                    date=doc.get('created_at', datetime.utcnow()),
                    status=doc.get('status', 'completed')
                ))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {str(e)}")
            return []
