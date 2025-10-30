"""
Automation API Router
Handles scheduled reports, email delivery, templates, and real-time updates
"""
from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
from database.mongodb import get_database, Database
from .scheduled_reports import ScheduledReportsService, ReportSchedule
from .email_service import EmailDeliveryService, EmailMessage
from .templates_service import ReportTemplatesService, ReportTemplate
from .realtime_service import RealtimeDashboardService, connection_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation", tags=["Automation"])


# ==================== SCHEDULED REPORTS ENDPOINTS ====================

@router.post("/schedules")
async def create_schedule(
    schedule: ReportSchedule,
    db: Database = Depends(get_database)
):
    """
    Create a new report schedule
    
    Schedule a report to be generated and sent automatically:
    - Daily: Every day at specified time
    - Weekly: Every week on specified day
    - Monthly: Every month on specified day
    
    The report will be generated and emailed to recipients automatically.
    """
    try:
        service = ScheduledReportsService(db)
        result = await service.create_schedule(schedule)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create schedule'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules")
async def get_schedules(
    enabled_only: bool = Query(False, description="Only return enabled schedules"),
    db: Database = Depends(get_database)
):
    """
    Get all report schedules
    
    Returns list of all configured report schedules with:
    - Schedule configuration
    - Next run time
    - Last run time and count
    - Enabled/disabled status
    """
    try:
        service = ScheduledReportsService(db)
        schedules = await service.get_schedules(enabled_only=enabled_only)
        
        return {
            "schedules": schedules,
            "total": len(schedules)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules/{schedule_id}")
async def get_schedule(
    schedule_id: str,
    db: Database = Depends(get_database)
):
    """Get a specific schedule by ID"""
    try:
        service = ScheduledReportsService(db)
        schedule = await service.get_schedule(schedule_id)
        
        if schedule:
            return schedule
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    updates: dict,
    db: Database = Depends(get_database)
):
    """Update a schedule"""
    try:
        service = ScheduledReportsService(db)
        result = await service.update_schedule(schedule_id, updates)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to update schedule'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: Database = Depends(get_database)
):
    """Delete a schedule"""
    try:
        service = ScheduledReportsService(db)
        result = await service.delete_schedule(schedule_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get('error', 'Schedule not found'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: str,
    enabled: bool = Query(..., description="Enable or disable the schedule"),
    db: Database = Depends(get_database)
):
    """Enable or disable a schedule"""
    try:
        service = ScheduledReportsService(db)
        result = await service.toggle_schedule(schedule_id, enabled)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to toggle schedule'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules/summary/stats")
async def get_schedule_summary(db: Database = Depends(get_database)):
    """
    Get summary statistics for all schedules
    
    Returns:
    - Total schedules
    - Enabled/disabled counts
    - Schedules by frequency
    - Recent runs
    """
    try:
        service = ScheduledReportsService(db)
        summary = await service.get_schedule_summary()
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EMAIL DELIVERY ENDPOINTS ====================

@router.post("/email/send")
async def send_email(message: EmailMessage):
    """
    Send an email
    
    Send a custom email with optional attachments.
    Requires SMTP configuration in environment variables:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASSWORD
    - FROM_EMAIL
    """
    try:
        service = EmailDeliveryService()
        
        if not service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Email service not configured. Please set SMTP environment variables."
            )
        
        result = await service.send_email(message)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to send email'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/test")
async def send_test_email(
    recipient: str = Query(..., description="Email address to send test to")
):
    """
    Send a test email to verify configuration
    
    Sends a simple test email to verify SMTP settings are correct.
    """
    try:
        service = EmailDeliveryService()
        
        if not service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Email service not configured. Please set SMTP environment variables."
            )
        
        result = await service.send_test_email(recipient)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to send test email'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/config")
async def get_email_config():
    """
    Get email configuration status
    
    Returns whether email service is properly configured.
    """
    try:
        service = EmailDeliveryService()
        
        return {
            "configured": service.is_configured(),
            "smtp_host": service.config.smtp_host,
            "smtp_port": service.config.smtp_port,
            "from_email": service.config.from_email,
            "from_name": service.config.from_name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORT TEMPLATES ENDPOINTS ====================

@router.post("/templates")
async def create_template(
    template: ReportTemplate,
    db: Database = Depends(get_database)
):
    """
    Create a new report template
    
    Create a custom report template with:
    - Custom sections and fields
    - Layout configuration
    - Filter options
    - Export format settings
    """
    try:
        service = ReportTemplatesService(db)
        result = await service.create_template(template)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create template'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    public_only: bool = Query(False, description="Only return public templates"),
    db: Database = Depends(get_database)
):
    """
    Get all report templates
    
    Returns list of available report templates filtered by:
    - Category (financial, receivables, analytics, custom)
    - Public/private status
    """
    try:
        service = ReportTemplatesService(db)
        templates = await service.get_templates(category=category, public_only=public_only)
        
        return {
            "templates": templates,
            "total": len(templates)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    db: Database = Depends(get_database)
):
    """Get a specific template by ID"""
    try:
        service = ReportTemplatesService(db)
        template = await service.get_template(template_id)
        
        if template:
            return template
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    updates: dict,
    db: Database = Depends(get_database)
):
    """Update a template"""
    try:
        service = ReportTemplatesService(db)
        result = await service.update_template(template_id, updates)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to update template'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    db: Database = Depends(get_database)
):
    """Delete a template"""
    try:
        service = ReportTemplatesService(db)
        result = await service.delete_template(template_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to delete template'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/duplicate")
async def duplicate_template(
    template_id: str,
    new_name: str = Query(..., description="Name for the new template"),
    db: Database = Depends(get_database)
):
    """
    Duplicate an existing template
    
    Creates a copy of an existing template with a new name.
    """
    try:
        service = ReportTemplatesService(db)
        result = await service.duplicate_template(template_id, new_name)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to duplicate template'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/categories/list")
async def get_template_categories(db: Database = Depends(get_database)):
    """Get list of available template categories"""
    try:
        service = ReportTemplatesService(db)
        categories = await service.get_template_categories()
        
        return {
            "categories": categories
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/seed/defaults")
async def seed_default_templates(db: Database = Depends(get_database)):
    """
    Seed default report templates
    
    Creates default templates if they don't exist:
    - Income Statement
    - Cash Flow Statement
    - AR Aging Report
    """
    try:
        service = ReportTemplatesService(db)
        result = await service.seed_default_templates()
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REAL-TIME DASHBOARD ENDPOINTS ====================

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Connect to receive live updates for:
    - Dashboard metrics
    - New transactions
    - Report completions
    - System alerts
    
    Parameters:
    - client_id: Unique identifier for the client
    """
    await connection_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Echo back for heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        connection_manager.disconnect(websocket, client_id)


@router.get("/realtime/stats")
async def get_realtime_stats():
    """
    Get real-time connection statistics
    
    Returns:
    - Total active connections
    - Number of unique clients
    - List of connected client IDs
    """
    try:
        stats = connection_manager.get_stats()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/realtime/broadcast")
async def broadcast_message(message: dict):
    """
    Broadcast a message to all connected clients
    
    Send a custom message to all active WebSocket connections.
    Useful for system-wide notifications.
    """
    try:
        await connection_manager.broadcast(message)
        
        return {
            "success": True,
            "message": "Broadcast sent",
            "recipients": connection_manager.get_connection_count()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime
