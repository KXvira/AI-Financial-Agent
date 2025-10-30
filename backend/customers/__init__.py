"""
Customer management module initialization
"""

from .router import router
from .models import Customer, CustomerCreate, CustomerUpdate
from .service import CustomerService

__all__ = [
    'router',
    'Customer',
    'CustomerCreate',
    'CustomerUpdate',
    'CustomerService'
]
