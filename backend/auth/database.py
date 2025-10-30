"""
Database connection service for authentication
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger("financial-agent.auth.database")

class AuthDatabaseService:
    """Database service specifically for authentication operations"""
    
    _instance: Optional['AuthDatabaseService'] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            self.database_name = os.getenv("MONGO_DB", "financial_agent")
            self.client: Optional[AsyncIOMotorClient] = None
            self.initialized = True
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self._db is None:
            await self.connect()
        return self._db
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            if self.client is None:
                logger.info(f"Connecting to MongoDB: {self.mongo_uri}")
                self.client = AsyncIOMotorClient(self.mongo_uri)
                self._db = self.client[self.database_name]
                
                # Test connection
                await self._db.command("ping")
                logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self._db = None
            logger.info("Disconnected from MongoDB")
    
    async def get_users_collection(self):
        """Get users collection"""
        db = await self.get_database()
        return db.users
    
    async def get_audit_logs_collection(self):
        """Get audit logs collection"""
        db = await self.get_database()
        return db.auth_audit_logs

# Global instance
auth_db_service = AuthDatabaseService()