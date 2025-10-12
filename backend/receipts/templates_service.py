"""
Receipt Template Service

Manages receipt templates for customization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId

from .models import ReceiptTemplate
from backend.database.mongodb import Database


class ReceiptTemplateService:
    """Service for managing receipt templates"""
    
    def __init__(self, db: Database):
        """
        Initialize template service
        
        Args:
            db: Database instance
        """
        self.db = db
        self.templates_collection = db.db["receipt_templates"]
    
    async def create_template(
        self,
        template: ReceiptTemplate,
        user_id: Optional[str] = None
    ) -> ReceiptTemplate:
        """
        Create a new receipt template
        
        Args:
            template: Template data
            user_id: Optional user ID
            
        Returns:
            Created template
        """
        template_dict = template.dict(by_alias=True, exclude={"id"})
        template_dict["created_at"] = datetime.utcnow()
        template_dict["updated_at"] = datetime.utcnow()
        
        result = await self.templates_collection.insert_one(template_dict)
        template.id = str(result.inserted_id)
        
        return template
    
    async def get_template(self, template_id: str) -> Optional[ReceiptTemplate]:
        """
        Get template by ID
        
        Args:
            template_id: Template ID
            
        Returns:
            Template or None if not found
        """
        try:
            result = await self.templates_collection.find_one({"_id": ObjectId(template_id)})
            if result:
                result["_id"] = str(result["_id"])
                return ReceiptTemplate(**result)
            return None
        except Exception as e:
            print(f"Error getting template: {e}")
            return None
    
    async def list_templates(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        List all templates
        
        Args:
            page: Page number
            page_size: Items per page
            is_active: Filter by active status
            
        Returns:
            Dict with templates and pagination info
        """
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get total count
        total = await self.templates_collection.count_documents(query)
        
        # Get templates
        skip = (page - 1) * page_size
        cursor = self.templates_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        
        templates = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            try:
                templates.append(ReceiptTemplate(**doc))
            except Exception as e:
                print(f"Skipping invalid template: {e}")
                continue
        
        return {
            "templates": templates,
            "total": len(templates),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(templates) + page_size - 1) // page_size
        }
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Optional[ReceiptTemplate]:
        """
        Update a template
        
        Args:
            template_id: Template ID
            updates: Fields to update
            user_id: Optional user ID
            
        Returns:
            Updated template or None if not found
        """
        template = await self.get_template(template_id)
        if not template:
            return None
        
        updates["updated_at"] = datetime.utcnow()
        
        await self.templates_collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": updates}
        )
        
        return await self.get_template(template_id)
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete a template (soft delete by marking inactive)
        
        Args:
            template_id: Template ID
            
        Returns:
            True if deleted, False if not found
        """
        template = await self.get_template(template_id)
        if not template:
            return False
        
        # Soft delete by marking as inactive
        await self.templates_collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return True
    
    async def get_default_template(self) -> Optional[ReceiptTemplate]:
        """
        Get the default template
        
        Returns:
            Default template or None if not found
        """
        result = await self.templates_collection.find_one({
            "is_default": True,
            "is_active": True
        })
        
        if result:
            result["_id"] = str(result["_id"])
            return ReceiptTemplate(**result)
        
        return None
    
    async def set_default_template(self, template_id: str) -> Optional[ReceiptTemplate]:
        """
        Set a template as default
        
        Args:
            template_id: Template ID
            
        Returns:
            Updated template or None if not found
        """
        template = await self.get_template(template_id)
        if not template:
            return None
        
        # Remove default from all other templates
        await self.templates_collection.update_many(
            {"is_default": True},
            {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
        )
        
        # Set this template as default
        await self.templates_collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": {"is_default": True, "updated_at": datetime.utcnow()}}
        )
        
        return await self.get_template(template_id)
    
    async def seed_default_templates(self) -> List[ReceiptTemplate]:
        """
        Create default receipt templates if they don't exist
        
        Returns:
            List of created templates
        """
        # Check if any templates exist
        count = await self.templates_collection.count_documents({})
        if count > 0:
            return []
        
        # Create default templates
        templates = [
            ReceiptTemplate(
                name="Default Receipt Template",
                description="Standard receipt template with company branding",
                primary_color="#1a56db",
                secondary_color="#e5e7eb",
                font_family="Helvetica",
                show_logo=True,
                show_qr_code=True,
                show_tax_breakdown=True,
                show_line_items=True,
                footer_text="Thank you for your business!",
                is_default=True,
                is_active=True
            ),
            ReceiptTemplate(
                name="Minimal Receipt Template",
                description="Clean and minimal receipt design",
                primary_color="#374151",
                secondary_color="#f3f4f6",
                font_family="Helvetica",
                show_logo=False,
                show_qr_code=True,
                show_tax_breakdown=True,
                show_line_items=True,
                footer_text="Keep this receipt for your records.",
                is_default=False,
                is_active=True
            ),
            ReceiptTemplate(
                name="Detailed Receipt Template",
                description="Comprehensive receipt with all details",
                primary_color="#059669",
                secondary_color="#d1fae5",
                font_family="Helvetica",
                show_logo=True,
                show_qr_code=True,
                show_tax_breakdown=True,
                show_line_items=True,
                footer_text="Thank you for choosing our services!",
                terms_and_conditions="All sales are final. Refunds available within 30 days.",
                is_default=False,
                is_active=True
            )
        ]
        
        created_templates = []
        for template in templates:
            created = await self.create_template(template)
            created_templates.append(created)
        
        return created_templates
    
    async def duplicate_template(
        self,
        template_id: str,
        new_name: str
    ) -> Optional[ReceiptTemplate]:
        """
        Duplicate an existing template
        
        Args:
            template_id: Template ID to duplicate
            new_name: Name for the duplicated template
            
        Returns:
            New template or None if original not found
        """
        original = await self.get_template(template_id)
        if not original:
            return None
        
        # Create new template with same settings
        new_template = ReceiptTemplate(
            name=new_name,
            description=f"Copy of {original.name}",
            logo_path=original.logo_path,
            primary_color=original.primary_color,
            secondary_color=original.secondary_color,
            font_family=original.font_family,
            show_logo=original.show_logo,
            show_qr_code=original.show_qr_code,
            show_tax_breakdown=original.show_tax_breakdown,
            show_line_items=original.show_line_items,
            business_name=original.business_name,
            business_kra_pin=original.business_kra_pin,
            business_address=original.business_address,
            business_phone=original.business_phone,
            business_email=original.business_email,
            footer_text=original.footer_text,
            terms_and_conditions=original.terms_and_conditions,
            is_default=False,
            is_active=True
        )
        
        return await self.create_template(new_template)
