"""
Report Templates Service
Manages custom report templates and layouts
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TemplateField(BaseModel):
    """Template field definition"""
    name: str = Field(..., description="Field name")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Field type: text, number, date, currency, percentage")
    source: str = Field(..., description="Data source: invoices, transactions, customers, etc.")
    aggregation: Optional[str] = Field(None, description="sum, avg, count, min, max")
    format: Optional[str] = Field(None, description="Display format")
    visible: bool = Field(default=True)
    order: int = Field(default=0)


class TemplateSection(BaseModel):
    """Template section definition"""
    name: str = Field(..., description="Section name")
    title: str = Field(..., description="Section title")
    type: str = Field(..., description="metrics, table, chart, text")
    fields: List[TemplateField] = Field(default_factory=list)
    layout: str = Field(default="grid", description="grid, list, chart")
    order: int = Field(default=0)
    visible: bool = Field(default=True)


class ReportTemplate(BaseModel):
    """Report template definition"""
    id: Optional[str] = None
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="financial, receivables, analytics, custom")
    sections: List[TemplateSection] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list, description="Available filters")
    export_formats: List[str] = Field(default=['pdf', 'excel', 'csv'], description="Supported export formats")
    is_default: bool = Field(default=False)
    is_public: bool = Field(default=True, description="Available to all users")
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    use_count: int = Field(default=0)


class ReportTemplatesService:
    """Service for managing report templates"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.report_templates
        
    async def create_template(self, template: ReportTemplate) -> Dict[str, Any]:
        """
        Create a new report template
        
        Args:
            template: Template definition
            
        Returns:
            Created template with ID
        """
        try:
            template_dict = template.dict(exclude={'id'})
            template_dict['created_at'] = datetime.utcnow()
            template_dict['updated_at'] = datetime.utcnow()
            
            result = await self.collection.insert_one(template_dict)
            
            template_dict['id'] = str(result.inserted_id)
            template_dict['_id'] = str(result.inserted_id)
            
            logger.info(f"Created template: {template.name} (ID: {result.inserted_id})")
            
            return {
                "success": True,
                "template": template_dict,
                "message": "Template created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_templates(
        self,
        category: Optional[str] = None,
        public_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get report templates
        
        Args:
            category: Filter by category
            public_only: Only return public templates
            
        Returns:
            List of templates
        """
        try:
            query = {}
            
            if category:
                query['category'] = category
            
            if public_only:
                query['is_public'] = True
            
            cursor = self.collection.find(query).sort("name", 1)
            templates = await cursor.to_list(length=None)
            
            for template in templates:
                template['id'] = str(template.pop('_id'))
            
            return templates
            
        except Exception as e:
            logger.error(f"Error fetching templates: {str(e)}")
            return []
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        try:
            from bson import ObjectId
            
            template = await self.collection.find_one({"_id": ObjectId(template_id)})
            
            if template:
                template['id'] = str(template.pop('_id'))
            
            return template
            
        except Exception as e:
            logger.error(f"Error fetching template {template_id}: {str(e)}")
            return None
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a template
        
        Args:
            template_id: Template ID
            updates: Fields to update
            
        Returns:
            Success status and updated template
        """
        try:
            from bson import ObjectId
            
            updates['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                updated_template = await self.get_template(template_id)
                return {
                    "success": True,
                    "template": updated_template,
                    "message": "Template updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Template not found or no changes made"
                }
                
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a template"""
        try:
            from bson import ObjectId
            
            # Don't delete default templates
            template = await self.get_template(template_id)
            if template and template.get('is_default'):
                return {
                    "success": False,
                    "error": "Cannot delete default template"
                }
            
            result = await self.collection.delete_one({"_id": ObjectId(template_id)})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Template deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Template not found"
                }
                
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def increment_use_count(self, template_id: str) -> None:
        """Increment the use count for a template"""
        try:
            from bson import ObjectId
            
            await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$inc": {"use_count": 1}}
            )
            
        except Exception as e:
            logger.error(f"Error incrementing use count: {str(e)}")
    
    async def duplicate_template(self, template_id: str, new_name: str) -> Dict[str, Any]:
        """
        Duplicate an existing template
        
        Args:
            template_id: Template ID to duplicate
            new_name: Name for the new template
            
        Returns:
            Success status and new template
        """
        try:
            template = await self.get_template(template_id)
            
            if not template:
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            # Create new template from existing
            template.pop('id')
            template.pop('use_count')
            template['name'] = new_name
            template['is_default'] = False
            
            new_template = ReportTemplate(**template)
            return await self.create_template(new_template)
            
        except Exception as e:
            logger.error(f"Error duplicating template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_template_categories(self) -> List[str]:
        """Get list of unique template categories"""
        try:
            categories = await self.collection.distinct("category")
            return sorted(categories)
            
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return []
    
    async def seed_default_templates(self) -> Dict[str, Any]:
        """Create default templates if they don't exist"""
        try:
            # Check if default templates exist
            existing = await self.collection.count_documents({"is_default": True})
            
            if existing > 0:
                return {
                    "success": True,
                    "message": "Default templates already exist"
                }
            
            # Create default templates
            default_templates = self._get_default_templates()
            
            inserted_count = 0
            for template_dict in default_templates:
                result = await self.collection.insert_one(template_dict)
                if result.inserted_id:
                    inserted_count += 1
            
            return {
                "success": True,
                "message": f"Created {inserted_count} default templates"
            }
            
        except Exception as e:
            logger.error(f"Error seeding default templates: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_default_templates(self) -> List[Dict[str, Any]]:
        """Get default template definitions"""
        return [
            {
                "name": "Income Statement",
                "description": "Standard Profit & Loss statement",
                "category": "financial",
                "sections": [
                    {
                        "name": "revenue",
                        "title": "Revenue",
                        "type": "metrics",
                        "fields": [
                            {
                                "name": "total_revenue",
                                "label": "Total Revenue",
                                "type": "currency",
                                "source": "invoices",
                                "aggregation": "sum",
                                "visible": True,
                                "order": 1
                            }
                        ],
                        "layout": "grid",
                        "order": 1,
                        "visible": True
                    }
                ],
                "filters": ["date_range", "customer"],
                "export_formats": ["pdf", "excel", "csv"],
                "is_default": True,
                "is_public": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "use_count": 0
            },
            {
                "name": "Cash Flow Statement",
                "description": "Cash inflows and outflows",
                "category": "financial",
                "sections": [],
                "filters": ["date_range"],
                "export_formats": ["pdf", "excel"],
                "is_default": True,
                "is_public": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "use_count": 0
            },
            {
                "name": "AR Aging Report",
                "description": "Accounts Receivable aging analysis",
                "category": "receivables",
                "sections": [],
                "filters": ["customer", "aging_period"],
                "export_formats": ["pdf", "excel", "csv"],
                "is_default": True,
                "is_public": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "use_count": 0
            }
        ]
