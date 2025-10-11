"""
Customer service - Business logic for customer management
"""
from typing import List, Optional, Dict
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from .models import (
    Customer, CustomerCreate, CustomerUpdate,
    CustomerListItem, CustomerStats, CustomerFinancialSummary
)


class CustomerService:
    """Service for customer operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.customers = db.customers
        self.invoices = db.invoices
        self.transactions = db.transactions
    
    async def get_customers(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> tuple[List[CustomerListItem], int]:
        """
        Get list of customers with filters
        
        Returns:
            tuple: (customers list, total count)
        """
        # Build query
        query = {}
        
        if status:
            query["status"] = status
        
        if payment_status:
            query["payment_status"] = payment_status
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"customer_id": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await self.customers.count_documents(query)
        
        # Build sort
        sort_direction = 1 if sort_order == "asc" else -1
        sort_field = sort_by
        
        # Get customers
        cursor = self.customers.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        customers_data = await cursor.to_list(length=limit)
        
        # Convert to list items
        customers = []
        for data in customers_data:
            customers.append(CustomerListItem(
                customer_id=data["customer_id"],
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                total_invoices=data.get("total_invoices", 0),
                outstanding_balance=data.get("outstanding_balance", 0.0),
                payment_status=data.get("payment_status", "good"),
                status=data.get("status", "active"),
                last_invoice_date=data.get("last_invoice_date")
            ))
        
        return customers, total
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get a single customer by ID"""
        data = await self.customers.find_one({"customer_id": customer_id})
        
        if not data:
            return None
        
        # Remove MongoDB _id
        data.pop("_id", None)
        
        return Customer(**data)
    
    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        # Generate customer ID
        last_customer = await self.customers.find_one(
            {},
            sort=[("customer_id", -1)]
        )
        
        if last_customer:
            last_id = int(last_customer["customer_id"].split("-")[1])
            new_id = f"CUST-{last_id + 1:04d}"
        else:
            new_id = "CUST-0001"
        
        # Create customer document
        customer_doc = customer_data.model_dump()
        customer_doc.update({
            "customer_id": new_id,
            "status": "active",
            "payment_status": "good",
            "total_invoices": 0,
            "total_billed": 0.0,
            "total_paid": 0.0,
            "outstanding_balance": 0.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_invoice_date": None
        })
        
        # Insert into database
        result = await self.customers.insert_one(customer_doc)
        
        # Return created customer
        customer_doc.pop("_id", None)
        return Customer(**customer_doc)
    
    async def update_customer(
        self,
        customer_id: str,
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update an existing customer"""
        # Get update data (only non-None fields)
        update_data = customer_data.model_dump(exclude_unset=True)
        
        if not update_data:
            # No fields to update
            return await self.get_customer(customer_id)
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now()
        
        # Update customer
        result = await self.customers.update_one(
            {"customer_id": customer_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        # Return updated customer
        return await self.get_customer(customer_id)
    
    async def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer (soft delete by setting status to inactive)
        """
        result = await self.customers.update_one(
            {"customer_id": customer_id},
            {
                "$set": {
                    "status": "inactive",
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def get_customer_financial_summary(
        self,
        customer_id: str
    ) -> Optional[CustomerFinancialSummary]:
        """Get detailed financial summary for a customer"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        # Get all invoices for this customer
        invoices = await self.invoices.find(
            {"customer_id": customer_id}
        ).to_list(length=None)
        
        # Calculate payment days
        payment_days = []
        for invoice in invoices:
            if invoice.get("status") == "paid" and invoice.get("paid_date"):
                issue_date = invoice.get("issue_date")
                paid_date = invoice.get("paid_date")
                
                if issue_date and paid_date:
                    if isinstance(issue_date, str):
                        issue_date = datetime.fromisoformat(issue_date)
                    if isinstance(paid_date, str):
                        paid_date = datetime.fromisoformat(paid_date)
                    
                    days = (paid_date - issue_date).days
                    if days >= 0:
                        payment_days.append(days)
        
        avg_payment_days = sum(payment_days) / len(payment_days) if payment_days else None
        
        # Calculate payment score (0-100)
        payment_score = None
        if avg_payment_days is not None:
            # Perfect score at 0 days, decreasing to 0 at 90 days
            payment_score = max(0, min(100, 100 - (avg_payment_days / 90 * 100)))
        
        return CustomerFinancialSummary(
            total_invoices=customer.total_invoices,
            total_billed=customer.total_billed,
            total_paid=customer.total_paid,
            outstanding_balance=customer.outstanding_balance,
            average_payment_days=round(avg_payment_days, 1) if avg_payment_days else None,
            payment_score=round(payment_score, 1) if payment_score else None
        )
    
    async def get_customer_stats(self) -> CustomerStats:
        """Get overall customer statistics"""
        # Get all customers
        all_customers = await self.customers.find().to_list(length=None)
        
        total_customers = len(all_customers)
        active_customers = sum(1 for c in all_customers if c.get("status") == "active")
        inactive_customers = total_customers - active_customers
        
        total_outstanding = sum(c.get("outstanding_balance", 0) for c in all_customers)
        customers_with_overdue = sum(
            1 for c in all_customers 
            if c.get("payment_status") in ["warning", "overdue"]
        )
        
        avg_outstanding = total_outstanding / total_customers if total_customers > 0 else 0
        
        # Get top 5 customers by total billed
        top_customers = sorted(
            all_customers,
            key=lambda c: c.get("total_billed", 0),
            reverse=True
        )[:5]
        
        top_customers_list = [
            {
                "customer_id": c["customer_id"],
                "name": c["name"],
                "total_billed": c.get("total_billed", 0),
                "total_paid": c.get("total_paid", 0),
                "outstanding_balance": c.get("outstanding_balance", 0)
            }
            for c in top_customers
        ]
        
        return CustomerStats(
            total_customers=total_customers,
            active_customers=active_customers,
            inactive_customers=inactive_customers,
            total_outstanding=round(total_outstanding, 2),
            customers_with_overdue=customers_with_overdue,
            average_outstanding=round(avg_outstanding, 2),
            top_customers=top_customers_list
        )
    
    async def refresh_customer_financials(self, customer_id: str) -> bool:
        """
        Recalculate and update customer financial summary from invoices
        """
        # Get all invoices for this customer
        invoices = await self.invoices.find(
            {"customer_id": customer_id}
        ).to_list(length=None)
        
        if not invoices:
            return False
        
        # Calculate totals
        total_invoices = len(invoices)
        total_billed = sum(inv.get("amount", 0) for inv in invoices)
        total_paid = sum(
            inv.get("amount", 0) 
            for inv in invoices 
            if inv.get("status") == "paid"
        )
        outstanding = total_billed - total_paid
        
        # Determine payment status
        if outstanding == 0:
            payment_status = "good"
        elif outstanding < total_billed * 0.2:
            payment_status = "good"
        elif outstanding < total_billed * 0.5:
            payment_status = "warning"
        else:
            payment_status = "overdue"
        
        # Get last invoice date
        invoice_dates = [inv.get("issue_date") or inv.get("created_at") for inv in invoices]
        invoice_dates = [d for d in invoice_dates if d]
        last_invoice_date = max(invoice_dates) if invoice_dates else None
        
        # Update customer
        result = await self.customers.update_one(
            {"customer_id": customer_id},
            {
                "$set": {
                    "total_invoices": total_invoices,
                    "total_billed": round(total_billed, 2),
                    "total_paid": round(total_paid, 2),
                    "outstanding_balance": round(outstanding, 2),
                    "payment_status": payment_status,
                    "last_invoice_date": last_invoice_date,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
