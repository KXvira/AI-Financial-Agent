# MongoDB Database Normalization Guide

## Overview

This guide walks you through normalizing your MongoDB database schema to improve data integrity, reduce redundancy, and enforce better relationships between collections.

## 📚 Documentation

- **Full Analysis**: [`docs/MONGODB_NORMALIZATION_ANALYSIS.md`](../docs/MONGODB_NORMALIZATION_ANALYSIS.md)
- **Migration Script**: [`scripts/normalize_database.py`](normalize_database.py)
- **Verification Script**: [`scripts/verify_normalization.py`](verify_normalization.py)

## 🎯 What This Normalization Achieves

### Before (Denormalized)
```javascript
// Invoice with embedded customer
{
  invoice_number: "INV-001",
  customer: {
    name: "Acme Corp",
    email: "acme@example.com",
    phone: "254712345678"
  },
  items: [
    { description: "Item 1", amount: 1000 }
  ]
}
```

### After (Normalized)
```javascript
// Customer (separate collection)
{
  _id: ObjectId("..."),
  customer_id: "CUST-0001",
  name: "Acme Corp",
  email: "acme@example.com",
  phone: "254712345678"
}

// Invoice (references customer)
{
  invoice_number: "INV-001",
  customer_id: ObjectId("..."),  // Reference
  total: 1000
}

// Invoice Items (separate collection)
{
  invoice_id: ObjectId("..."),  // Reference
  description: "Item 1",
  amount: 1000
}
```

## 🚀 Quick Start

### Step 1: Backup Your Database

**CRITICAL**: Always backup before running migration!

```bash
# MongoDB Atlas backup (automatic)
# Or manual backup:
mongodump --uri="your_mongo_uri" --out=backup_$(date +%Y%m%d)
```

### Step 2: Review the Analysis

Read the full analysis document:
```bash
cat docs/MONGODB_NORMALIZATION_ANALYSIS.md
```

### Step 3: Dry Run Migration

Preview changes without modifying the database:
```bash
python scripts/normalize_database.py --dry-run
```

Example output:
```
====================================================================
  DATABASE NORMALIZATION MIGRATION
====================================================================

⚠️  DRY RUN MODE - No changes will be committed

📊 Step 1: Creating indexes...
   [DRY RUN] Would create indexes

👥 Step 2: Normalizing customers...
   Found 1,234 invoices with embedded customer data
   ✅ Created 156 customers
   ✅ Updated 1,234 invoices

🧾 Step 3: Normalizing invoice items...
   ✅ Created 4,567 invoice items

💰 Step 4: Normalizing payments...
   ✅ Created 2,345 unified payment records
```

### Step 4: Run Migration

Execute the actual migration:
```bash
python scripts/normalize_database.py
```

You'll be prompted to confirm:
```
🚀 LIVE MODE - Database will be modified

Type 'yes' to continue: yes
```

### Step 5: Verify Results

Check data integrity after migration:
```bash
python scripts/verify_normalization.py
```

Example output:
```
====================================================================
  VERIFICATION RESULTS
====================================================================

✅ All checks passed! Database normalization is successful.

Collection counts:
   customers                     : 156
   invoices                      : 1,234
   invoice_items                 : 4,567
   payments                      : 2,345
   payment_gateway_data          : 1,890
```

## 📋 What Gets Changed

### Collections Modified

1. **customers** (NEW)
   - Extracted from invoice embedded data
   - Each unique customer gets one record

2. **invoices**
   - `customer` object → `customer_id` reference
   - `items` array removed

3. **invoice_items** (NEW)
   - Separated from invoices
   - One record per line item

4. **payments** (NEW)
   - Unified from `transactions` (type: payment) and `mpesa_payments`
   - Clear references to invoices and customers

5. **payment_gateway_data** (NEW)
   - Gateway-specific data separated
   - References payment records

6. **audit_logs** (NEW)
   - Migration tracking
   - Future user activity tracking

### Fields Removed

From **invoices**:
- ❌ `customer` (embedded object)
- ❌ `items` (array)

### Fields Added

To **invoices**:
- ✅ `customer_id` (ObjectId reference)
- ✅ `created_by` (ObjectId reference)
- ✅ `sent_by` (ObjectId reference)

## 🔍 Validation Checks

The verification script checks:

- ✅ All invoices have valid customer references
- ✅ No orphaned invoice items
- ✅ Payment references are valid
- ✅ No remaining embedded data
- ✅ Required indexes exist
- ✅ Data consistency (totals match)

## 🛠️ Rollback Plan

If issues occur, you can rollback:

### Option 1: Restore from Backup
```bash
mongorestore --uri="your_mongo_uri" backup_20251014
```

### Option 2: Manual Rollback
The migration doesn't delete old collections, only creates new ones and modifies existing ones. You can:
1. Drop new collections: `invoice_items`, `payments`, `payment_gateway_data`
2. Restore `customer` and `items` fields to invoices from backup

## 🔧 Troubleshooting

### Issue: "DuplicateKeyError on customer email"

**Solution**: Some invoices have different customers with the same email. Check and fix:
```python
# Find duplicate emails
db.invoices.aggregate([
  { $group: { _id: "$customer.email", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

### Issue: "Orphaned invoice items found"

**Solution**: Invoice was deleted but items remain. Clean up:
```bash
python scripts/verify_normalization.py
# Review orphaned items
# Delete if needed
```

### Issue: "Invoice totals don't match item totals"

**Solution**: Recalculate invoice totals:
```python
# Run recalculation script
python scripts/recalculate_invoice_totals.py
```

## 📊 Performance Impact

### Query Performance

**Before (embedded)**:
```javascript
// Single query - fast
db.invoices.findOne({ invoice_number: "INV-001" })
```

**After (normalized)**:
```javascript
// Requires $lookup - slightly slower
db.invoices.aggregate([
  { $match: { invoice_number: "INV-001" } },
  { $lookup: { from: "customers", localField: "customer_id", foreignField: "_id", as: "customer" } },
  { $lookup: { from: "invoice_items", localField: "_id", foreignField: "invoice_id", as: "items" } }
])
```

**Mitigation**:
- Indexes on `customer_id`, `invoice_id` fields
- Caching for frequently accessed data
- Aggregation pipelines optimized by MongoDB

### Benefits

✅ **Update Performance**: Updating customer email updates once, not N times  
✅ **Storage**: Less redundant data = smaller database  
✅ **Queries**: Can query products across all invoices  
✅ **Integrity**: Single source of truth prevents inconsistencies

## 🎓 Next Steps After Migration

### 1. Update Application Code

Example using Mongoose:
```javascript
// Before
const invoice = await Invoice.findOne({ invoice_number: "INV-001" });
const customerName = invoice.customer.name;

// After
const invoice = await Invoice.findOne({ invoice_number: "INV-001" })
  .populate('customer_id');
const customerName = invoice.customer_id.name;
```

### 2. Update API Endpoints

Ensure all endpoints use `$lookup` or `.populate()` to fetch related data.

### 3. Create Helper Functions

```javascript
// Helper to get invoice with all related data
async function getInvoiceWithDetails(invoiceNumber) {
  return await Invoice.findOne({ invoice_number: invoiceNumber })
    .populate('customer_id')
    .populate({
      path: 'items',
      options: { sort: { line_number: 1 } }
    })
    .exec();
}
```

### 4. Implement Referential Integrity

```javascript
// Prevent deleting customer with invoices
async function deleteCustomer(customerId) {
  const invoiceCount = await Invoice.countDocuments({ customer_id: customerId });
  if (invoiceCount > 0) {
    throw new Error('Cannot delete customer with existing invoices');
  }
  await Customer.deleteOne({ _id: customerId });
}
```

### 5. Use Transactions for Multi-Document Operations

```javascript
const session = await mongoose.startSession();
session.startTransaction();

try {
  // Create invoice
  const invoice = await Invoice.create([invoiceData], { session });
  
  // Create invoice items
  const items = invoiceItems.map(item => ({
    ...item,
    invoice_id: invoice[0]._id
  }));
  await InvoiceItem.insertMany(items, { session });
  
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## 📖 Reference Documentation

### Schema Validation Example

```javascript
db.createCollection("invoices", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["invoice_number", "customer_id", "total"],
      properties: {
        invoice_number: {
          bsonType: "string",
          pattern: "^INV-[0-9]{4}-[0-9]{2}-[0-9]{4}$"
        },
        customer_id: {
          bsonType: "objectId"
        },
        total: {
          bsonType: "double",
          minimum: 0
        }
      }
    }
  }
})
```

### Aggregation Examples

See [`docs/MONGODB_NORMALIZATION_ANALYSIS.md`](../docs/MONGODB_NORMALIZATION_ANALYSIS.md) Section 8 for:
- Get invoice with customer details
- Get customer with invoice summary
- Get payment with full details
- Product sales analysis

## 🆘 Support

### Common Questions

**Q: Will this break my existing application?**  
A: If your app reads `invoice.customer.name`, it will break. Update to `invoice.customer_id.name` (after populating).

**Q: Can I rollback after migration?**  
A: Yes, restore from backup. The migration doesn't delete data, only restructures it.

**Q: How long does migration take?**  
A: Depends on data size. For 10,000 invoices: ~5-10 minutes. Test with --dry-run first.

**Q: Do I need to update all code immediately?**  
A: For new schema, yes. You can temporarily support both by keeping old fields until transition complete.

### Getting Help

1. Review error messages from verification script
2. Check logs in `audit_logs` collection
3. Consult [`docs/MONGODB_NORMALIZATION_ANALYSIS.md`](../docs/MONGODB_NORMALIZATION_ANALYSIS.md)
4. Create an issue with error details

## 📝 Checklist

- [ ] Backup database
- [ ] Review normalization analysis document
- [ ] Run dry-run migration
- [ ] Review dry-run output
- [ ] Run actual migration
- [ ] Run verification script
- [ ] Update application code
- [ ] Test in development environment
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Remove old denormalized fields (after verification)

## 🎉 Success Criteria

After migration, you should have:

✅ Separate `customers` collection  
✅ Separate `invoice_items` collection  
✅ Unified `payments` collection  
✅ No embedded customer/items in invoices  
✅ All verification checks passing  
✅ Updated application code  
✅ Proper indexes on reference fields  

---

**Last Updated**: October 14, 2025  
**Version**: 1.0  
**Author**: GitHub Copilot
