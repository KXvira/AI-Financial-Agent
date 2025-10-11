"""
MongoDB database connection and operations
"""
import os
import motor.motor_asyncio
from pymongo import ReturnDocument
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import json
import uuid

logger = logging.getLogger("financial-agent.database")

class DatabaseConfig:
    """MongoDB configuration"""
    
    def __init__(self):
        # Load from environment or use defaults
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = os.environ.get("MONGO_DB", "financial_agent")
        
        # Collections
        self.transactions_collection = "transactions"
        self.invoices_collection = "invoices"
        self.customers_collection = "customers"
        self.reconciliation_collection = "reconciliation_logs"
        self.analytics_collection = "analytics"

class Database:
    """Database operations using Motor for async MongoDB access"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.config.mongo_uri)
        self.db = self.client[self.config.database_name]
        
        # Collection objects
        self.transactions = self.db[self.config.transactions_collection]
        self.invoices = self.db[self.config.invoices_collection]
        self.customers = self.db[self.config.customers_collection]
        self.reconciliation = self.db[self.config.reconciliation_collection]
        self.analytics = self.db[self.config.analytics_collection]
        
        logger.info(f"Connected to MongoDB: {self.config.mongo_uri}")
    
    async def store_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Store a transaction in the database
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Transaction ID
        """
        # Generate ID if not present
        if "_id" not in transaction_data and "id" not in transaction_data:
            transaction_data["_id"] = str(uuid.uuid4())
        elif "id" in transaction_data and "_id" not in transaction_data:
            transaction_data["_id"] = transaction_data.pop("id")
            
        # Ensure timestamps are datetime objects
        for timestamp_field in ["request_timestamp", "completion_timestamp"]:
            if timestamp_field in transaction_data and isinstance(transaction_data[timestamp_field], str):
                transaction_data[timestamp_field] = datetime.fromisoformat(transaction_data[timestamp_field])
        
        # Store the transaction
        result = await self.transactions.insert_one(transaction_data)
        logger.info(f"Stored transaction: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    async def update_transaction(self, transaction_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a transaction in the database
        
        Args:
            transaction_id: Transaction ID
            update_data: Update data
            
        Returns:
            Updated transaction
        """
        # Update the transaction
        result = await self.transactions.find_one_and_update(
            {"_id": transaction_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            logger.info(f"Updated transaction: {transaction_id}")
            return result
        else:
            logger.error(f"Transaction not found: {transaction_id}")
            return None
    
    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get a transaction by ID
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction data
        """
        result = await self.transactions.find_one({"_id": transaction_id})
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            return result
        else:
            logger.error(f"Transaction not found: {transaction_id}")
            return None
    
    async def get_transactions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get transactions by status
        
        Args:
            status: Transaction status
            
        Returns:
            List of transactions
        """
        cursor = self.transactions.find({"status": status})
        results = []
        
        async for doc in cursor:
            # Convert ObjectId to string for id field
            if "_id" in doc:
                doc["id"] = str(doc.pop("_id"))
            
            results.append(doc)
            
        return results
    
    async def get_unreconciled_transactions(self) -> List[Dict[str, Any]]:
        """
        Get transactions pending reconciliation
        
        Returns:
            List of unreconciled transactions
        """
        cursor = self.transactions.find({
            "status": "completed",
            "reconciliation_status": "pending"
        })
        
        results = []
        
        async for doc in cursor:
            # Convert ObjectId to string for id field
            if "_id" in doc:
                doc["id"] = str(doc.pop("_id"))
            
            results.append(doc)
            
        return results
    
    async def store_invoice(self, invoice_data: Dict[str, Any]) -> str:
        """
        Store an invoice in the database
        
        Args:
            invoice_data: Invoice data
            
        Returns:
            Invoice ID
        """
        # Generate ID if not present
        if "_id" not in invoice_data and "id" not in invoice_data:
            invoice_data["_id"] = str(uuid.uuid4())
        elif "id" in invoice_data and "_id" not in invoice_data:
            invoice_data["_id"] = invoice_data.pop("id")
            
        # Ensure timestamps are datetime objects
        for timestamp_field in ["date_issued", "due_date", "created_at", "updated_at"]:
            if timestamp_field in invoice_data and isinstance(invoice_data[timestamp_field], str):
                invoice_data[timestamp_field] = datetime.fromisoformat(invoice_data[timestamp_field])
        
        # Store the invoice
        result = await self.invoices.insert_one(invoice_data)
        logger.info(f"Stored invoice: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    async def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an invoice in the database
        
        Args:
            invoice_id: Invoice ID
            update_data: Update data
            
        Returns:
            Updated invoice
        """
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.now()
        
        # Update the invoice
        result = await self.invoices.find_one_and_update(
            {"_id": invoice_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            logger.info(f"Updated invoice: {invoice_id}")
            return result
        else:
            logger.error(f"Invoice not found: {invoice_id}")
            return None
    
    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get an invoice by ID
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Invoice data
        """
        result = await self.invoices.find_one({"_id": invoice_id})
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            return result
        else:
            logger.error(f"Invoice not found: {invoice_id}")
            return None
    
    async def get_pending_invoices(self) -> List[Dict[str, Any]]:
        """
        Get pending invoices (sent but not paid)
        
        Returns:
            List of pending invoices
        """
        cursor = self.invoices.find({
            "status": {"$in": ["sent", "overdue"]}
        })
        
        results = []
        
        async for doc in cursor:
            # Convert ObjectId to string for id field
            if "_id" in doc:
                doc["id"] = str(doc.pop("_id"))
            
            results.append(doc)
            
        return results
    
    async def store_reconciliation_log(self, log_data: Dict[str, Any]) -> str:
        """
        Store a reconciliation log
        
        Args:
            log_data: Reconciliation log data
            
        Returns:
            Log ID
        """
        # Generate ID if not present
        if "_id" not in log_data and "id" not in log_data:
            log_data["_id"] = str(uuid.uuid4())
        elif "id" in log_data and "_id" not in log_data:
            log_data["_id"] = log_data.pop("id")
            
        # Add timestamp if not present
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.now()
            
        # Store the log
        result = await self.reconciliation.insert_one(log_data)
        logger.info(f"Stored reconciliation log: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    async def create_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Generic method to create a document in any collection
        
        Args:
            collection_name: Name of the collection
            document: Document data
            
        Returns:
            Document ID
        """
        # Generate ID if not present
        if "_id" not in document and "id" not in document:
            document["_id"] = str(uuid.uuid4())
        elif "id" in document and "_id" not in document:
            document["_id"] = document.pop("id")
            
        # Get collection
        collection = self.db[collection_name]
        
        # Insert document
        result = await collection.insert_one(document)
        logger.info(f"Created document in {collection_name}: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    async def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generic method to find one document in any collection
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            
        Returns:
            Document data or None
        """
        collection = self.db[collection_name]
        result = await collection.find_one(query)
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            return result
        else:
            return None
    
    def find(self, collection_name: str, query: Dict[str, Any]):
        """
        Generic method to find multiple documents in any collection
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            
        Returns:
            Async cursor
        """
        collection = self.db[collection_name]
        return collection.find(query)
    
    async def update_document(self, collection_name: str, document_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generic method to update a document in any collection
        
        Args:
            collection_name: Name of the collection
            document_id: Document ID
            update_data: Update data
            
        Returns:
            Updated document
        """
        collection = self.db[collection_name]
        
        result = await collection.find_one_and_update(
            {"_id": document_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            # Convert ObjectId to string for id field
            if "_id" in result:
                result["id"] = str(result.pop("_id"))
            
            logger.info(f"Updated document in {collection_name}: {document_id}")
            return result
        else:
            logger.error(f"Document not found in {collection_name}: {document_id}")
            return None
    
    async def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
            