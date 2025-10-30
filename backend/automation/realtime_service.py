"""
Real-time Dashboard Service
Handles WebSocket connections for live dashboard updates
"""
from typing import Dict, Any, List, Set, Optional
from fastapi import WebSocket
from datetime import datetime
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept a new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await websocket.accept()
        
        async with self._lock:
            if client_id not in self.active_connections:
                self.active_connections[client_id] = set()
            self.active_connections[client_id].add(websocket)
        
        logger.info(f"Client {client_id} connected. Total connections: {self.get_connection_count()}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "message": "Connected to Fin Guard real-time dashboard",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """
        Remove a WebSocket connection
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total connections: {self.get_connection_count()}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send a message to a specific client
        
        Args:
            message: Message to send
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients
        
        Args:
            message: Message to broadcast
        """
        disconnected = []
        
        for client_id, connections in self.active_connections.items():
            for connection in connections.copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                    disconnected.append((connection, client_id))
        
        # Clean up disconnected clients
        for connection, client_id in disconnected:
            self.disconnect(connection, client_id)
    
    async def broadcast_to_client(self, client_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections for a specific client
        
        Args:
            client_id: Client identifier
            message: Message to send
        """
        if client_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[client_id].copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, client_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_client_count(self) -> int:
        """Get total number of unique clients"""
        return len(self.active_connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": self.get_connection_count(),
            "unique_clients": self.get_client_count(),
            "clients": list(self.active_connections.keys())
        }


class RealtimeDashboardService:
    """Service for real-time dashboard updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.update_interval = 5  # seconds
    
    async def send_dashboard_update(self, data: Dict[str, Any]):
        """
        Send a dashboard update to all connected clients
        
        Args:
            data: Dashboard data to send
        """
        message = {
            "type": "dashboard_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast(message)
    
    async def send_metric_update(self, metric_name: str, value: Any):
        """
        Send a single metric update
        
        Args:
            metric_name: Name of the metric
            value: New metric value
        """
        message = {
            "type": "metric_update",
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast(message)
    
    async def send_alert(self, alert_type: str, message: str, severity: str = "info"):
        """
        Send an alert to all connected clients
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (info, warning, error)
        """
        alert = {
            "type": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast(alert)
    
    async def send_transaction_notification(self, transaction: Dict[str, Any]):
        """
        Send notification about a new transaction
        
        Args:
            transaction: Transaction data
        """
        notification = {
            "type": "new_transaction",
            "transaction": transaction,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast(notification)
    
    async def send_report_completion(self, report_type: str, report_id: str, client_id: Optional[str] = None):
        """
        Notify about report completion
        
        Args:
            report_type: Type of report
            report_id: Report identifier
            client_id: Optional specific client to notify
        """
        notification = {
            "type": "report_complete",
            "report_type": report_type,
            "report_id": report_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if client_id:
            await self.manager.broadcast_to_client(client_id, notification)
        else:
            await self.manager.broadcast(notification)
    
    async def start_live_metrics(self, db):
        """
        Start sending live metric updates
        
        Args:
            db: Database connection
        """
        logger.info("Starting live metrics updates")
        
        while True:
            try:
                if self.manager.get_connection_count() > 0:
                    # Fetch latest metrics
                    metrics = await self._get_live_metrics(db)
                    
                    # Send updates
                    await self.send_dashboard_update(metrics)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in live metrics update: {str(e)}")
                await asyncio.sleep(self.update_interval)
    
    async def _get_live_metrics(self, db) -> Dict[str, Any]:
        """
        Fetch live metrics from database
        
        Args:
            db: Database connection
            
        Returns:
            Dictionary of metrics
        """
        try:
            from datetime import datetime, timedelta
            
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get today's revenue
            revenue_pipeline = [
                {
                    "$match": {
                        "issue_date": {"$gte": today_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$total_amount"}
                    }
                }
            ]
            
            revenue_result = await db.invoices.aggregate(revenue_pipeline).to_list(length=1)
            today_revenue = revenue_result[0]['total'] if revenue_result else 0
            
            # Get today's transactions
            transactions_count = await db.transactions.count_documents({
                "transaction_date": {"$gte": today_start}
            })
            
            # Get pending invoices count
            pending_invoices = await db.invoices.count_documents({
                "status": {"$in": ["pending", "overdue"]}
            })
            
            # Get total customers
            total_customers = await db.customers.count_documents({})
            
            return {
                "today_revenue": today_revenue,
                "today_transactions": transactions_count,
                "pending_invoices": pending_invoices,
                "total_customers": total_customers,
                "last_update": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching live metrics: {str(e)}")
            return {
                "error": str(e),
                "last_update": datetime.utcnow().isoformat()
            }


# Global connection manager instance
connection_manager = ConnectionManager()
