#!/usr/bin/env python3
"""
Extract unique customers from invoices and create customer documents
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Dict, List

# MongoDB connection
MONGO_URI = "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
DATABASE_NAME = "financial_agent"

async def extract_customers():
    """Extract unique customers from invoices collection"""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    print("🔍 Analyzing invoices to extract customers...")
    print("=" * 60)
    
    # Get all invoices
    invoices = await db.invoices.find().to_list(length=None)
    print(f"📊 Found {len(invoices)} invoices")
    
    # Group by customer
    customer_data = {}
    
    for invoice in invoices:
        customer_name = invoice.get('customer_name', 'Unknown')
        
        if customer_name not in customer_data:
            customer_data[customer_name] = {
                'invoices': [],
                'total_billed': 0,
                'total_paid': 0,
                'emails': set(),
                'phones': set()
            }
        
        # Collect invoice data
        customer_data[customer_name]['invoices'].append(invoice)
        amount = invoice.get('amount', 0)
        customer_data[customer_name]['total_billed'] += amount
        
        if invoice.get('status') == 'paid':
            customer_data[customer_name]['total_paid'] += amount
        
        # Collect contact info if available
        if invoice.get('customer_email'):
            customer_data[customer_name]['emails'].add(invoice['customer_email'])
        if invoice.get('customer_phone'):
            customer_data[customer_name]['phones'].add(invoice['customer_phone'])
    
    print(f"\n✅ Found {len(customer_data)} unique customers")
    print("\nCustomer Summary:")
    print("-" * 60)
    
    customers_to_create = []
    
    for idx, (name, data) in enumerate(sorted(customer_data.items()), 1):
        customer_id = f"CUST-{idx:04d}"
        
        invoice_count = len(data['invoices'])
        total_billed = data['total_billed']
        total_paid = data['total_paid']
        outstanding = total_billed - total_paid
        
        # Get most recent invoice date
        invoice_dates = [inv.get('issue_date') or inv.get('created_at') for inv in data['invoices']]
        invoice_dates = [d for d in invoice_dates if d]
        last_invoice_date = max(invoice_dates) if invoice_dates else datetime.now()
        
        # Determine payment status
        if outstanding == 0:
            payment_status = "good"
        elif outstanding < total_billed * 0.2:  # Less than 20% outstanding
            payment_status = "good"
        elif outstanding < total_billed * 0.5:  # Less than 50% outstanding
            payment_status = "warning"
        else:
            payment_status = "overdue"
        
        # Get primary contact info
        primary_email = list(data['emails'])[0] if data['emails'] else f"{name.lower().replace(' ', '.')}@company.com"
        primary_phone = list(data['phones'])[0] if data['phones'] else "254722000000"
        
        # Create customer document
        customer_doc = {
            "customer_id": customer_id,
            "name": name,
            "email": primary_email,
            "phone": primary_phone,
            "secondary_email": list(data['emails'])[1] if len(data['emails']) > 1 else None,
            "secondary_phone": list(data['phones'])[1] if len(data['phones']) > 1 else None,
            
            # Address (default values - can be updated later)
            "address": {
                "street": "",
                "city": "Nairobi",
                "postal_code": "00100",
                "country": "Kenya"
            },
            
            # Business info
            "business_type": "general",
            "tax_id": None,
            
            # Financial summary
            "total_invoices": invoice_count,
            "total_billed": round(total_billed, 2),
            "total_paid": round(total_paid, 2),
            "outstanding_balance": round(outstanding, 2),
            
            # Payment settings
            "preferred_payment_method": "mpesa",
            "payment_terms": "net_30",
            "credit_limit": None,
            
            # Status
            "status": "active",
            "payment_status": payment_status,
            "auto_send_invoices": False,
            "send_reminders": True,
            
            # Metadata
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_invoice_date": last_invoice_date,
            
            # AI preferences
            "ai_preferences": {
                "invoice_template": "professional",
                "language": "english",
                "include_tax": True,
                "default_currency": "KES"
            },
            
            # Notes
            "notes": f"Automatically created from {invoice_count} existing invoices",
            "tags": []
        }
        
        customers_to_create.append(customer_doc)
        
        # Print summary
        status_emoji = {
            "good": "🟢",
            "warning": "🟡",
            "overdue": "🔴"
        }
        
        print(f"{idx}. {customer_id} - {name}")
        print(f"   📧 {primary_email}")
        print(f"   📱 {primary_phone}")
        print(f"   📄 {invoice_count} invoices | KES {total_billed:,.2f} billed")
        print(f"   💰 KES {total_paid:,.2f} paid | KES {outstanding:,.2f} outstanding")
        print(f"   {status_emoji[payment_status]} {payment_status.upper()}")
        print()
    
    # Ask for confirmation
    print("=" * 60)
    print(f"\n📝 Ready to create {len(customers_to_create)} customer records")
    
    # Check if customers collection already has data
    existing_count = await db.customers.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Warning: {existing_count} customers already exist in database")
        response = input("Do you want to replace them? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled")
            client.close()
            return
        
        # Delete existing customers
        result = await db.customers.delete_many({})
        print(f"🗑️  Deleted {result.deleted_count} existing customers")
    
    # Insert customers
    print("\n💾 Creating customer records...")
    result = await db.customers.insert_many(customers_to_create)
    print(f"✅ Successfully created {len(result.inserted_ids)} customers!")
    
    # Update invoices with customer_id
    print("\n🔗 Linking invoices to customers...")
    updated_count = 0
    
    for customer in customers_to_create:
        result = await db.invoices.update_many(
            {"customer_name": customer['name']},
            {"$set": {"customer_id": customer['customer_id']}}
        )
        updated_count += result.modified_count
    
    print(f"✅ Updated {updated_count} invoices with customer_id")
    
    print("\n" + "=" * 60)
    print("🎉 Customer extraction complete!")
    print(f"✅ {len(customers_to_create)} customers created")
    print(f"✅ {updated_count} invoices linked")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(extract_customers())
