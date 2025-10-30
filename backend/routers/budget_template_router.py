from fastapi import APIRouter, HTTPException, Depends
from backend.models.budget_template import BudgetTemplate, BudgetTemplateCreate, BudgetTemplateUpdate
from backend.services.budget_template_service import BudgetTemplateService
from typing import List

router = APIRouter(prefix="/api/budget-templates", tags=["Budget Templates"])

# Initialize service
template_service = BudgetTemplateService()

@router.post("", response_model=BudgetTemplate, status_code=201)
async def create_template(template: BudgetTemplateCreate):
    """Create a new budget template"""
    try:
        return await template_service.create_template(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@router.get("", response_model=List[BudgetTemplate])
async def get_templates(include_defaults: bool = True):
    """Get all budget templates (user's + defaults)"""
    try:
        return await template_service.get_templates(include_defaults=include_defaults)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@router.get("/{template_id}", response_model=BudgetTemplate)
async def get_template(template_id: str):
    """Get a specific budget template"""
    template = await template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=BudgetTemplate)
async def update_template(template_id: str, update_data: BudgetTemplateUpdate):
    """Update a budget template"""
    template = await template_service.update_template(template_id, update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a budget template (only non-default templates)"""
    success = await template_service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or cannot delete default template")
    return {"message": "Template deleted successfully"}

@router.post("/initialize-defaults")
async def initialize_defaults():
    """Initialize default budget templates"""
    count = await template_service.initialize_default_templates()
    return {"message": f"Initialized {count} default templates"}
