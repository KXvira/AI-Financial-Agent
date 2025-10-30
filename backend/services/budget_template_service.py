"""
Budget Template Service - Business logic for budget templates
"""
import logging
from backend.models.budget_template import BudgetTemplate, BudgetTemplateCreate, BudgetTemplateUpdate
from backend.database.mongodb import Database
from typing import List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger("financial-agent.budget_template")


class BudgetTemplateService:
    """Service for managing budget templates"""
    
    def __init__(self):
        self.db = Database.get_instance()
        self.collection = self.db.db["budget_templates"]
        logger.info("BudgetTemplateService initialized")
    
    async def create_template(self, template_data: BudgetTemplateCreate, user_id: Optional[str] = None) -> BudgetTemplate:
        """Create a new budget template"""
        template_dict = template_data.model_dump()
        template_dict["id"] = str(uuid.uuid4())
        template_dict["created_by"] = user_id
        template_dict["is_default"] = False
        template_dict["created_at"] = datetime.utcnow()
        template_dict["updated_at"] = datetime.utcnow()
        
        await self.collection.insert_one(template_dict)
        return BudgetTemplate(**template_dict)
    
    async def get_templates(self, user_id: Optional[str] = None, include_defaults: bool = True) -> List[BudgetTemplate]:
        """Get all templates (user's + default templates)"""
        query = {}
        if include_defaults and user_id:
            query = {"$or": [{"created_by": user_id}, {"is_default": True}]}
        elif user_id:
            query = {"created_by": user_id}
        elif include_defaults:
            query = {"is_default": True}
        
        templates = []
        async for template in self.collection.find(query):
            template["_id"] = str(template["_id"])
            templates.append(BudgetTemplate(**template))
        
        return templates
    
    async def get_template(self, template_id: str) -> Optional[BudgetTemplate]:
        """Get a specific template by ID"""
        template = await self.collection.find_one({"id": template_id})
        if template:
            template["_id"] = str(template["_id"])
            return BudgetTemplate(**template)
        return None
    
    async def update_template(self, template_id: str, update_data: BudgetTemplateUpdate) -> Optional[BudgetTemplate]:
        """Update a template"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return await self.get_template(template_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"id": template_id},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return BudgetTemplate(**result)
        return None
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template (only non-default templates)"""
        result = await self.collection.delete_one({"id": template_id, "is_default": False})
        return result.deleted_count > 0
    
    async def initialize_default_templates(self):
        """Initialize default budget templates"""
        default_templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "Monthly Marketing",
                "description": "Standard monthly marketing budget for digital campaigns and advertising",
                "category": "Marketing",
                "subcategory": "Digital Advertising",
                "amount": 5000.0,
                "period_type": "monthly",
                "alert_threshold": 80.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Monthly Payroll",
                "description": "Standard monthly payroll budget for employee salaries",
                "category": "Salaries",
                "subcategory": "Employee Payroll",
                "amount": 15000.0,
                "period_type": "monthly",
                "alert_threshold": 90.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Quarterly Operations",
                "description": "Quarterly budget for operational expenses including utilities and supplies",
                "category": "Operations",
                "subcategory": "General Expenses",
                "amount": 10000.0,
                "period_type": "quarterly",
                "alert_threshold": 75.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Monthly Office Supplies",
                "description": "Monthly budget for office supplies and equipment",
                "category": "Office",
                "subcategory": "Supplies",
                "amount": 1000.0,
                "period_type": "monthly",
                "alert_threshold": 70.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Yearly Training & Development",
                "description": "Annual budget for employee training and professional development",
                "category": "Training",
                "subcategory": "Professional Development",
                "amount": 8000.0,
                "period_type": "yearly",
                "alert_threshold": 85.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Monthly Travel",
                "description": "Monthly budget for business travel and related expenses",
                "category": "Travel",
                "subcategory": "Business Travel",
                "amount": 3000.0,
                "period_type": "monthly",
                "alert_threshold": 80.0,
                "is_default": True,
                "created_by": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Check if default templates already exist
        existing_count = await self.collection.count_documents({"is_default": True})
        if existing_count == 0:
            await self.collection.insert_many(default_templates)
            return len(default_templates)
        return 0
