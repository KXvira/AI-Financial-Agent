"""
Scheduled Reports Service
Handles automated report generation and scheduling using APScheduler
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class ScheduleConfig(BaseModel):
    """Report schedule configuration"""
    frequency: str = Field(..., description="daily, weekly, monthly")
    time: str = Field(..., description="Time in HH:MM format (24-hour)")
    day_of_week: Optional[int] = Field(None, description="0-6 for Monday-Sunday (weekly only)")
    day_of_month: Optional[int] = Field(None, description="1-31 (monthly only)")
    timezone: str = Field(default="Africa/Nairobi", description="Timezone for scheduling")


class ReportSchedule(BaseModel):
    """Scheduled report definition"""
    id: Optional[str] = None
    name: str = Field(..., description="Schedule name")
    report_type: str = Field(..., description="Type of report to generate")
    schedule: ScheduleConfig
    recipients: List[str] = Field(..., description="Email addresses to send to")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Report parameters")
    enabled: bool = Field(default=True, description="Whether schedule is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = Field(default=0)


class ScheduledReportsService:
    """Service for managing and executing scheduled reports"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.scheduled_reports
        
    async def create_schedule(self, schedule: ReportSchedule) -> Dict[str, Any]:
        """
        Create a new report schedule
        
        Args:
            schedule: Report schedule configuration
            
        Returns:
            Created schedule with ID
        """
        try:
            # Calculate next run time
            next_run = self._calculate_next_run(schedule.schedule)
            schedule.next_run = next_run
            
            # Insert into database
            schedule_dict = schedule.dict(exclude={'id'})
            result = await self.collection.insert_one(schedule_dict)
            
            schedule_dict['id'] = str(result.inserted_id)
            schedule_dict['_id'] = str(result.inserted_id)
            
            logger.info(f"Created schedule: {schedule.name} (ID: {result.inserted_id})")
            
            return {
                "success": True,
                "schedule": schedule_dict,
                "message": "Schedule created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_schedules(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all report schedules
        
        Args:
            enabled_only: If True, return only enabled schedules
            
        Returns:
            List of schedules
        """
        try:
            query = {"enabled": True} if enabled_only else {}
            
            cursor = self.collection.find(query).sort("created_at", -1)
            schedules = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for schedule in schedules:
                schedule['id'] = str(schedule.pop('_id'))
            
            return schedules
            
        except Exception as e:
            logger.error(f"Error fetching schedules: {str(e)}")
            return []
    
    async def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific schedule by ID"""
        try:
            from bson import ObjectId
            
            schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
            
            if schedule:
                schedule['id'] = str(schedule.pop('_id'))
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error fetching schedule {schedule_id}: {str(e)}")
            return None
    
    async def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a schedule
        
        Args:
            schedule_id: Schedule ID
            updates: Fields to update
            
        Returns:
            Success status and updated schedule
        """
        try:
            from bson import ObjectId
            
            # Recalculate next run if schedule changed
            if 'schedule' in updates:
                next_run = self._calculate_next_run(ScheduleConfig(**updates['schedule']))
                updates['next_run'] = next_run
            
            result = await self.collection.update_one(
                {"_id": ObjectId(schedule_id)},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                updated_schedule = await self.get_schedule(schedule_id)
                return {
                    "success": True,
                    "schedule": updated_schedule,
                    "message": "Schedule updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Schedule not found or no changes made"
                }
                
        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete a schedule"""
        try:
            from bson import ObjectId
            
            result = await self.collection.delete_one({"_id": ObjectId(schedule_id)})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Schedule deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Schedule not found"
                }
                
        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def toggle_schedule(self, schedule_id: str, enabled: bool) -> Dict[str, Any]:
        """Enable or disable a schedule"""
        return await self.update_schedule(schedule_id, {"enabled": enabled})
    
    async def mark_schedule_run(self, schedule_id: str) -> None:
        """Mark a schedule as having been run"""
        try:
            from bson import ObjectId
            
            now = datetime.utcnow()
            schedule = await self.get_schedule(schedule_id)
            
            if schedule:
                next_run = self._calculate_next_run(ScheduleConfig(**schedule['schedule']))
                
                await self.collection.update_one(
                    {"_id": ObjectId(schedule_id)},
                    {
                        "$set": {
                            "last_run": now,
                            "next_run": next_run
                        },
                        "$inc": {"run_count": 1}
                    }
                )
                
        except Exception as e:
            logger.error(f"Error marking schedule run: {str(e)}")
    
    async def get_due_schedules(self) -> List[Dict[str, Any]]:
        """Get schedules that are due to run"""
        try:
            now = datetime.utcnow()
            
            cursor = self.collection.find({
                "enabled": True,
                "next_run": {"$lte": now}
            })
            
            schedules = await cursor.to_list(length=None)
            
            for schedule in schedules:
                schedule['id'] = str(schedule.pop('_id'))
            
            return schedules
            
        except Exception as e:
            logger.error(f"Error fetching due schedules: {str(e)}")
            return []
    
    def _calculate_next_run(self, schedule: ScheduleConfig) -> datetime:
        """
        Calculate the next run time for a schedule
        
        Args:
            schedule: Schedule configuration
            
        Returns:
            Next run datetime
        """
        now = datetime.utcnow()
        time_parts = schedule.time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if schedule.frequency == 'daily':
            # Next occurrence at the specified time
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule.frequency == 'weekly':
            # Next occurrence on the specified day of week
            days_ahead = schedule.day_of_week - now.weekday()
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += timedelta(weeks=1)
        
        elif schedule.frequency == 'monthly':
            # Next occurrence on the specified day of month
            next_run = now.replace(day=schedule.day_of_month, hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_run <= now:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
        
        else:
            # Default to tomorrow at the specified time
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
        
        return next_run
    
    async def get_schedule_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all schedules"""
        try:
            total = await self.collection.count_documents({})
            enabled = await self.collection.count_documents({"enabled": True})
            disabled = total - enabled
            
            # Get schedules by frequency
            pipeline = [
                {"$group": {
                    "_id": "$schedule.frequency",
                    "count": {"$sum": 1}
                }}
            ]
            
            frequency_counts = {}
            async for doc in self.collection.aggregate(pipeline):
                frequency_counts[doc['_id']] = doc['count']
            
            # Get recent runs
            recent_runs = await self.collection.find(
                {"last_run": {"$ne": None}}
            ).sort("last_run", -1).limit(5).to_list(length=5)
            
            for run in recent_runs:
                run['id'] = str(run.pop('_id'))
            
            return {
                "total_schedules": total,
                "enabled": enabled,
                "disabled": disabled,
                "by_frequency": frequency_counts,
                "recent_runs": recent_runs
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule summary: {str(e)}")
            return {
                "total_schedules": 0,
                "enabled": 0,
                "disabled": 0,
                "by_frequency": {},
                "recent_runs": []
            }
