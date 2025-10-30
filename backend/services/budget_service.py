"""
Budget Service - Business logic for budget management
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from backend.models.budget import (
    Budget, BudgetCreate, BudgetUpdate, BudgetSummary,
    BudgetAnalytics, BudgetAlert, BudgetStatus, AlertLevel, PeriodType
)
from backend.database.mongodb import Database
from backend.services.budget_notification_service import BudgetNotificationService
import os

logger = logging.getLogger("financial-agent.budget")


class BudgetService:
    """Service for managing budgets"""
    
    def __init__(self):
        self.db = Database.get_instance()
        self.budgets_collection = self.db.db["budgets"]
        self.expenses_collection = self.db.db["expenses"]
        self.notification_service = BudgetNotificationService()
        self.alert_email = os.getenv("BUDGET_ALERT_EMAIL", "admin@example.com")
        logger.info("BudgetService initialized")
    
    async def create_budget(self, budget_data: BudgetCreate) -> Budget:
        """
        Create a new budget
        
        Args:
            budget_data: Budget creation data
            
        Returns:
            Created budget
        """
        try:
            # Create budget document
            budget_dict = budget_data.dict()
            budget_dict["actual_spent"] = 0.0
            budget_dict["status"] = BudgetStatus.ACTIVE
            budget_dict["alert_level"] = AlertLevel.NONE
            budget_dict["created_at"] = datetime.now()
            budget_dict["updated_at"] = datetime.now()
            
            # Convert dates to ISO format strings for MongoDB
            if isinstance(budget_dict.get("start_date"), date):
                budget_dict["start_date"] = budget_dict["start_date"].isoformat()
            if isinstance(budget_dict.get("end_date"), date):
                budget_dict["end_date"] = budget_dict["end_date"].isoformat()
            
            # Generate ID
            budget_dict["id"] = f"budget_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            budget_dict["_id"] = budget_dict["id"]
            
            # Insert into database
            await self.budgets_collection.insert_one(budget_dict)
            
            # Calculate initial actual spent from existing expenses
            await self._recalculate_budget_spent(budget_dict["id"])
            
            # Fetch and return the created budget
            budget = await self.get_budget(budget_dict["id"])
            
            logger.info(f"Created budget: {budget.id} for category {budget.category}")
            return budget
            
        except Exception as e:
            logger.error(f"Error creating budget: {str(e)}")
            raise
    
    async def get_budget(self, budget_id: str) -> Optional[Budget]:
        """
        Get a budget by ID
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Budget or None if not found
        """
        try:
            budget_doc = await self.budgets_collection.find_one({"_id": budget_id})
            
            if not budget_doc:
                return None
            
            # Convert dates
            if isinstance(budget_doc.get("start_date"), str):
                budget_doc["start_date"] = date.fromisoformat(budget_doc["start_date"])
            if isinstance(budget_doc.get("end_date"), str):
                budget_doc["end_date"] = date.fromisoformat(budget_doc["end_date"])
            
            budget = Budget(**budget_doc)
            budget.update_alert_level()
            
            return budget
            
        except Exception as e:
            logger.error(f"Error getting budget {budget_id}: {str(e)}")
            raise
    
    async def list_budgets(
        self,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[BudgetStatus] = None,
        period_type: Optional[PeriodType] = None,
        active_only: bool = False
    ) -> List[Budget]:
        """
        List budgets with optional filters
        
        Args:
            user_id: Filter by user ID
            category: Filter by category
            status: Filter by status
            period_type: Filter by period type
            active_only: Only return active budgets
            
        Returns:
            List of budgets
        """
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            
            if category:
                query["category"] = category
            
            if status:
                query["status"] = status
            
            if period_type:
                query["period_type"] = period_type
            
            if active_only:
                today = date.today().isoformat()
                query["start_date"] = {"$lte": today}
                query["end_date"] = {"$gte": today}
                query["status"] = BudgetStatus.ACTIVE
            
            cursor = self.budgets_collection.find(query).sort("created_at", -1)
            budgets = []
            
            async for budget_doc in cursor:
                # Convert dates
                if isinstance(budget_doc.get("start_date"), str):
                    budget_doc["start_date"] = date.fromisoformat(budget_doc["start_date"])
                if isinstance(budget_doc.get("end_date"), str):
                    budget_doc["end_date"] = date.fromisoformat(budget_doc["end_date"])
                
                budget = Budget(**budget_doc)
                budget.update_alert_level()
                budgets.append(budget)
            
            logger.info(f"Listed {len(budgets)} budgets")
            return budgets
            
        except Exception as e:
            logger.error(f"Error listing budgets: {str(e)}")
            raise
    
    async def update_budget(self, budget_id: str, update_data: BudgetUpdate) -> Optional[Budget]:
        """
        Update a budget
        
        Args:
            budget_id: Budget ID
            update_data: Update data
            
        Returns:
            Updated budget or None if not found
        """
        try:
            # Get existing budget
            existing_budget = await self.get_budget(budget_id)
            if not existing_budget:
                return None
            
            # Prepare update
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.now()
            
            # Update in database
            await self.budgets_collection.update_one(
                {"_id": budget_id},
                {"$set": update_dict}
            )
            
            # Fetch and return updated budget
            updated_budget = await self.get_budget(budget_id)
            
            logger.info(f"Updated budget: {budget_id}")
            return updated_budget
            
        except Exception as e:
            logger.error(f"Error updating budget {budget_id}: {str(e)}")
            raise
    
    async def delete_budget(self, budget_id: str) -> bool:
        """
        Delete a budget
        
        Args:
            budget_id: Budget ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.budgets_collection.delete_one({"_id": budget_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted budget: {budget_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting budget {budget_id}: {str(e)}")
            raise
    
    async def update_budget_spent(self, category: str, amount: float, transaction_date: date) -> List[str]:
        """
        Update actual spent for budgets matching the category and date range
        
        Args:
            category: Expense category
            amount: Amount to add
            transaction_date: Transaction date
            
        Returns:
            List of updated budget IDs
        """
        try:
            # Find matching budgets
            query = {
                "category": category,
                "status": BudgetStatus.ACTIVE,
                "start_date": {"$lte": transaction_date.isoformat()},
                "end_date": {"$gte": transaction_date.isoformat()}
            }
            
            updated_ids = []
            cursor = self.budgets_collection.find(query)
            
            async for budget_doc in cursor:
                # Update actual_spent
                new_spent = budget_doc.get("actual_spent", 0) + amount
                
                await self.budgets_collection.update_one(
                    {"_id": budget_doc["_id"]},
                    {
                        "$set": {
                            "actual_spent": round(new_spent, 2),
                            "updated_at": datetime.now()
                        }
                    }
                )
                
                updated_ids.append(budget_doc["_id"])
                
                # Check for alerts
                budget = await self.get_budget(budget_doc["_id"])
                if budget:
                    await self._check_budget_alerts(budget)
            
            logger.info(f"Updated {len(updated_ids)} budgets for category {category}")
            return updated_ids
            
        except Exception as e:
            logger.error(f"Error updating budget spent: {str(e)}")
            raise
    
    async def process_expense_transaction(
        self, 
        category: str, 
        amount: float, 
        transaction_date: Optional[date] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an expense transaction and update related budgets
        
        This method is called when a new expense is created to automatically
        update matching budgets.
        
        Args:
            category: Expense category
            amount: Expense amount
            transaction_date: Transaction date (defaults to today)
            user_id: Optional user ID
            
        Returns:
            Dictionary with update results and alerts
        """
        try:
            if transaction_date is None:
                transaction_date = date.today()
            
            # Update matching budgets
            updated_budget_ids = await self.update_budget_spent(category, amount, transaction_date)
            
            # Collect alerts for budgets that need attention
            alerts = []
            for budget_id in updated_budget_ids:
                budget = await self.get_budget(budget_id)
                if budget:
                    alert = await self._check_budget_alerts(budget)
                    if alert:
                        alerts.append(alert.dict())
            
            result = {
                "updated_budgets": len(updated_budget_ids),
                "budget_ids": updated_budget_ids,
                "alerts": alerts,
                "category": category,
                "amount": amount,
                "date": transaction_date.isoformat()
            }
            
            logger.info(f"Processed expense transaction: {category} ${amount:.2f} - Updated {len(updated_budget_ids)} budgets")
            return result
            
        except Exception as e:
            logger.error(f"Error processing expense transaction: {str(e)}")
            return {
                "updated_budgets": 0,
                "budget_ids": [],
                "alerts": [],
                "error": str(e)
            }
    
    async def get_budget_summary(self, user_id: Optional[str] = None) -> BudgetSummary:
        """
        Get budget summary statistics
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            Budget summary
        """
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            budgets = await self.list_budgets(user_id=user_id)
            
            summary = BudgetSummary()
            summary.total_budgets = len(budgets)
            
            by_category = {}
            by_period = {}
            
            for budget in budgets:
                # Totals
                summary.total_budgeted += budget.amount
                summary.total_spent += budget.actual_spent
                summary.total_remaining += budget.remaining_amount
                
                # Count by status
                if budget.is_exceeded:
                    summary.budgets_exceeded += 1
                elif budget.alert_level == AlertLevel.CRITICAL:
                    summary.budgets_critical += 1
                elif budget.alert_level == AlertLevel.WARNING:
                    summary.budgets_warning += 1
                else:
                    summary.budgets_on_track += 1
                
                # By category
                if budget.category not in by_category:
                    by_category[budget.category] = {
                        "budgeted": 0.0,
                        "spent": 0.0,
                        "remaining": 0.0
                    }
                by_category[budget.category]["budgeted"] += budget.amount
                by_category[budget.category]["spent"] += budget.actual_spent
                by_category[budget.category]["remaining"] += budget.remaining_amount
                
                # By period
                if budget.period_type not in by_period:
                    by_period[budget.period_type] = {
                        "budgeted": 0.0,
                        "spent": 0.0,
                        "remaining": 0.0
                    }
                by_period[budget.period_type]["budgeted"] += budget.amount
                by_period[budget.period_type]["spent"] += budget.actual_spent
                by_period[budget.period_type]["remaining"] += budget.remaining_amount
            
            if summary.total_budgets > 0:
                summary.average_utilization = round(
                    (summary.total_spent / summary.total_budgeted * 100) if summary.total_budgeted > 0 else 0,
                    2
                )
            
            summary.by_category = by_category
            summary.by_period = by_period
            
            logger.info(f"Generated budget summary: {summary.total_budgets} budgets")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating budget summary: {str(e)}")
            raise
    
    async def get_budget_analytics(self, budget_id: str) -> Optional[BudgetAnalytics]:
        """
        Get detailed analytics for a budget
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Budget analytics or None
        """
        try:
            budget = await self.get_budget(budget_id)
            if not budget:
                return None
            
            # Calculate spending rate
            days_elapsed = (date.today() - budget.start_date).days
            if days_elapsed <= 0:
                days_elapsed = 1
            
            spending_rate = budget.actual_spent / days_elapsed if days_elapsed > 0 else 0
            
            # Project end balance
            total_days = (budget.end_date - budget.start_date).days
            projected_spend = spending_rate * total_days
            projected_end_balance = budget.amount - projected_spend
            
            # Days until exceeded
            days_until_exceeded = None
            if spending_rate > 0 and budget.remaining_amount > 0:
                days_until_exceeded = int(budget.remaining_amount / spending_rate)
            
            # Determine trend
            if spending_rate > (budget.amount / total_days):
                trend = "increasing"
            elif spending_rate < (budget.amount / total_days) * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Risk level
            if budget.utilization_percentage >= 100:
                risk_level = "high"
            elif budget.utilization_percentage >= budget.alert_threshold:
                risk_level = "high"
            elif budget.utilization_percentage >= 50:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Recommendation
            if projected_end_balance < 0:
                recommendation = f"Warning: At current spending rate, you'll exceed budget by ${abs(projected_end_balance):.2f}. Consider reducing spending."
            elif budget.utilization_percentage > 90:
                recommendation = "Budget nearly exhausted. Monitor closely and avoid non-essential expenses."
            elif budget.utilization_percentage > 70:
                recommendation = "On track but approaching limit. Review upcoming expenses."
            else:
                recommendation = "Budget is on track. Continue monitoring spending patterns."
            
            analytics = BudgetAnalytics(
                budget_id=budget.id,
                category=budget.category,
                period_type=budget.period_type,
                utilization_percentage=budget.utilization_percentage,
                utilization_trend=trend,
                spending_rate=round(spending_rate, 2),
                projected_end_balance=round(projected_end_balance, 2),
                days_until_exceeded=days_until_exceeded,
                recommendation=recommendation,
                risk_level=risk_level
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics for budget {budget_id}: {str(e)}")
            raise
    
    async def get_categories(self, user_id: Optional[str] = None) -> List[str]:
        """
        Get list of unique budget categories
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            List of category names
        """
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            categories = await self.budgets_collection.distinct("category", query)
            return sorted(categories)
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise
    
    async def _recalculate_budget_spent(self, budget_id: str) -> float:
        """
        Recalculate actual_spent from expenses for a budget
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Recalculated amount
        """
        try:
            budget = await self.get_budget(budget_id)
            if not budget:
                return 0.0
            
            # Query expenses matching this budget
            query = {
                "category": budget.category,
                "date": {
                    "$gte": budget.start_date.isoformat(),
                    "$lte": budget.end_date.isoformat()
                }
            }
            
            if budget.subcategory:
                query["subcategory"] = budget.subcategory
            
            total = 0.0
            cursor = self.expenses_collection.find(query)
            
            async for expense in cursor:
                total += expense.get("amount", 0)
            
            # Update budget
            await self.budgets_collection.update_one(
                {"_id": budget_id},
                {"$set": {"actual_spent": round(total, 2), "updated_at": datetime.now()}}
            )
            
            logger.info(f"Recalculated budget {budget_id} spent: ${total:.2f}")
            return total
            
        except Exception as e:
            logger.error(f"Error recalculating budget spent: {str(e)}")
            raise
    
    async def _check_budget_alerts(self, budget: Budget) -> Optional[BudgetAlert]:
        """
        Check if budget requires alert and send notification email
        
        Args:
            budget: Budget to check
            
        Returns:
            BudgetAlert if alert should be triggered, None otherwise
        """
        try:
            # Store previous alert level
            previous_alert_level = budget.alert_level
            
            # Update alert level based on current utilization
            alert_level = budget.update_alert_level()
            
            if alert_level == AlertLevel.NONE:
                return None
            
            # Create alert message
            if alert_level == AlertLevel.EXCEEDED:
                message = f"Budget exceeded! Spent ${budget.actual_spent:.2f} of ${budget.amount:.2f} ({budget.utilization_percentage:.1f}%)"
            elif alert_level == AlertLevel.CRITICAL:
                message = f"Budget critical! {budget.utilization_percentage:.1f}% used. Only ${budget.remaining_amount:.2f} remaining."
            else:  # WARNING
                message = f"Budget warning: {budget.utilization_percentage:.1f}% used. ${budget.remaining_amount:.2f} remaining."
            
            alert = BudgetAlert(
                budget_id=budget.id,
                category=budget.category,
                alert_level=alert_level,
                current_utilization=budget.utilization_percentage,
                amount_spent=budget.actual_spent,
                amount_remaining=budget.remaining_amount,
                message=message
            )
            
            logger.warning(f"Budget alert triggered: {message}")
            
            # Send email notification if alert level changed or is critical/exceeded
            should_send_email = (
                previous_alert_level != alert_level or 
                alert_level in [AlertLevel.CRITICAL, AlertLevel.EXCEEDED]
            )
            
            if should_send_email:
                try:
                    await self.notification_service.send_budget_alert(
                        budget=budget,
                        recipient_email=self.alert_email,
                        recipient_name="Budget Administrator"
                    )
                    logger.info(f"Budget alert email sent for {budget.category}")
                except Exception as email_error:
                    logger.error(f"Failed to send budget alert email: {str(email_error)}")
                    # Don't fail the whole operation if email fails
            
            return alert
            
        except Exception as e:
            logger.error(f"Error checking budget alerts: {str(e)}")
            return None
