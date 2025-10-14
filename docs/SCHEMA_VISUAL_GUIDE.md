# MongoDB Schema Transformation - Visual Guide

## 🎨 Before & After Visualization

### Current Schema (Denormalized)

```
┌─────────────────────────────────────────────────────────┐
│                    invoices (4,868)                      │
├─────────────────────────────────────────────────────────┤
│ invoice_number: "INV-2025-10-0001"                      │
│                                                          │
│ ┌─────────────────────────────────────────────────┐    │
│ │ customer: {                    ❌ EMBEDDED      │    │
│ │   name: "Acme Corp",                            │    │
│ │   email: "acme@example.com",                    │    │
│ │   phone: "254712345678",                        │    │
│ │   address: "123 Main St",                       │    │
│ │   city: "Nairobi"                               │    │
│ │ }                                                │    │
│ └─────────────────────────────────────────────────┘    │
│                                                          │
│ ┌─────────────────────────────────────────────────┐    │
│ │ items: [                       ❌ EMBEDDED      │    │
│ │   {                                             │    │
│ │     description: "Office Supplies",             │    │
│ │     quantity: 5,                                │    │
│ │     unit_price: 1000,                           │    │
│ │     amount: 5000                                │    │
│ │   },                                            │    │
│ │   {                                             │    │
│ │     description: "IT Services",                 │    │
│ │     quantity: 1,                                │    │
│ │     unit_price: 800,                            │    │
│ │     amount: 800                                 │    │
│ │   }                                             │    │
│ │ ]                                                │    │
│ └─────────────────────────────────────────────────┘    │
│                                                          │
│ total: 5800                                             │
│ status: "paid"                                          │
│ created_at: 2025-10-14                                  │
└─────────────────────────────────────────────────────────┘

PROBLEMS:
❌ Customer data duplicated in every invoice
❌ Can't update customer email once (must update N invoices)
❌ Can't query "which invoices have Product X?"
❌ No product catalog
❌ Data inconsistency risk
```

---

### Normalized Schema (After Migration)

```
┌──────────────────────────────┐
│   customers (245)            │  ✅ NEW - Single source of truth
├──────────────────────────────┤
│ _id: ObjectId("...")         │
│ customer_id: "CUST-0001"     │
│ name: "Acme Corp"            │
│ email: "acme@example.com"    │  ← Update once, affects all invoices
│ phone: "254712345678"        │
│ address: {                   │
│   street: "123 Main St",     │
│   city: "Nairobi"            │
│ }                            │
│ status: "active"             │
│ created_at: 2025-01-15       │
└──────────────────────────────┘
         ▲
         │ References
         │
┌──────────────────────────────┐
│   invoices (4,868)           │  ✅ NORMALIZED
├──────────────────────────────┤
│ _id: ObjectId("...")         │
│ invoice_number: "INV-0001"   │
│ customer_id: ObjectId("...") │  ← Reference (not embedded)
│ date_issued: 2025-10-14      │
│ total: 5800                  │
│ amount_paid: 5800            │
│ balance: 0                   │
│ status: "paid"               │
│ created_by: ObjectId("...")  │  ← Audit trail
│ sent_by: ObjectId("...")     │
└──────────────────────────────┘
         ▲
         │ References
         │
┌──────────────────────────────┐
│   invoice_items (12,456)     │  ✅ NEW - Separated for analytics
├──────────────────────────────┤
│ _id: ObjectId("...")         │
│ invoice_id: ObjectId("...")  │  ← Reference to invoice
│ product_id: ObjectId("...")  │  ← Reference to product catalog
│ line_number: 1               │
│ description: "Office Sup..."  │
│ quantity: 5                  │
│ unit_price: 1000             │
│ total: 5000                  │
│ product_snapshot: {          │  ← Historical accuracy
│   name: "Office Supplies",   │
│   standard_price: 1000       │
│ }                            │
└──────────────────────────────┘
         │
         │ References
         ▼
┌──────────────────────────────┐
│   products (50)              │  ✅ NEW - Product catalog
├──────────────────────────────┤
│ _id: ObjectId("...")         │
│ product_id: "PROD-0001"      │
│ name: "Office Supplies"      │
│ description: "..."           │
│ unit_price: 1000             │  ← Standard pricing
│ tax_rate: 0.16               │
│ category: "office_supplies"  │
│ status: "active"             │
└──────────────────────────────┘

BENEFITS:
✅ Customer updated once, reflected everywhere
✅ Can query: "All invoices for Customer X"
✅ Can analyze: "Top selling products"
✅ Product catalog for consistent pricing
✅ Historical accuracy maintained
```

---

## 🔄 Data Flow Comparison

### Before (Denormalized)

```
User Action: Update customer email

┌──────────────────────────────────────────────────────┐
│ 1. Find all invoices for customer                   │
│    db.invoices.find({ "customer.email": "old@..." }) │
│                                                       │
│ 2. Update EACH invoice (4,868 updates!)              │
│    for invoice in invoices:                          │
│      db.invoices.update_one(                         │
│        {"_id": invoice._id},                         │
│        {"$set": {"customer.email": "new@..."}}       │
│      )                                               │
│                                                       │
│ ⏱️  Time: ~30 seconds for 4,868 invoices            │
│ 💾 Writes: 4,868 document updates                   │
│ ⚠️  Risk: Partial update if error occurs           │
└──────────────────────────────────────────────────────┘
```

### After (Normalized)

```
User Action: Update customer email

┌──────────────────────────────────────────────────────┐
│ 1. Update customer record (SINGLE UPDATE!)           │
│    db.customers.update_one(                          │
│      {"customer_id": "CUST-0001"},                   │
│      {"$set": {"email": "new@..."}}                  │
│    )                                                 │
│                                                       │
│ ✅ All invoices automatically reference new email   │
│    (via customer_id reference)                       │
│                                                       │
│ ⏱️  Time: < 1 second                                 │
│ 💾 Writes: 1 document update                        │
│ ✅ Atomic: All or nothing                           │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Collection Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    NORMALIZED DATABASE SCHEMA                     │
└──────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │     users       │
                    ├─────────────────┤
                    │ email           │
                    │ password_hash   │
                    │ role            │
                    └─────────────────┘
                            │
                            │ created_by
                            ▼
                    ┌─────────────────┐
          ┌────────▶│   customers     │◀────────┐
          │         ├─────────────────┤         │
          │         │ customer_id     │         │
          │         │ name            │         │
          │         │ email           │         │
          │         │ phone           │         │
          │         │ address         │         │
          │         └─────────────────┘         │
          │                 │                   │
          │                 │ customer_id       │
          │                 ▼                   │
          │         ┌─────────────────┐         │ customer_id
          │         │    invoices     │         │
          │         ├─────────────────┤         │
          │         │ invoice_number  │         │
          │         │ customer_id     │─────────┘
          │         │ total           │
          │         │ status          │
          │         └─────────────────┘
          │                 │
          │                 │ invoice_id
          │                 ▼
          │         ┌─────────────────┐
          │         │ invoice_items   │
          │         ├─────────────────┤         ┌─────────────────┐
          │         │ invoice_id      │         │    products     │
          │         │ product_id      │────────▶├─────────────────┤
          │         │ description     │         │ product_id      │
          │         │ quantity        │         │ name            │
          │         │ unit_price      │         │ unit_price      │
          │         │ total           │         │ category        │
          │         └─────────────────┘         └─────────────────┘
          │                 ▲
          │                 │ invoice_id
          │                 │
          │         ┌─────────────────┐
          │         │    payments     │
          │         ├─────────────────┤
          │         │ payment_id      │
          │         │ invoice_id      │─────────┘
          │         │ customer_id     │──────────┐
          │         │ amount          │          │
          │         │ gateway         │          │
          │         │ status          │          │
          │         └─────────────────┘          │
          │                 │                    │
          │                 │ payment_id         │
          │                 ▼                    ▼
          │         ┌─────────────────┐  ┌─────────────────┐
          │         │ gateway_data    │  │    receipts     │
          │         ├─────────────────┤  ├─────────────────┤
          │         │ payment_id      │  │ receipt_number  │
          │         │ gateway         │  │ payment_id      │
          │         │ gateway_data    │  │ invoice_id      │
          │         │ raw_request     │  │ customer_id     │─┘
          │         └─────────────────┘  │ amount          │
          │                              │ pdf_url         │
          │                              └─────────────────┘
          │
          │         ┌─────────────────┐
          └─────────│  audit_logs     │
                    ├─────────────────┤
                    │ user_id         │
                    │ action          │
                    │ resource_type   │
                    │ resource_id     │
                    │ changes         │
                    │ timestamp       │
                    └─────────────────┘

Legend:
─────▶  References (foreign key)
════▶  Embeds (nested document)
```

---

## 🎯 Query Examples

### Example 1: Get Invoice with Customer Details

**Before (Simple):**
```javascript
// Single query - customer is embedded
const invoice = await db.invoices.findOne({
  invoice_number: "INV-0001"
});

console.log(invoice.customer.name);  // Direct access
console.log(invoice.items);          // Direct access
```

**After (With $lookup):**
```javascript
// Aggregation pipeline - join collections
const invoice = await db.invoices.aggregate([
  { $match: { invoice_number: "INV-0001" } },
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $lookup: {
      from: "invoice_items",
      localField: "_id",
      foreignField: "invoice_id",
      as: "items"
    }
  }
]).next();

console.log(invoice.customer.name);  // Same access pattern
console.log(invoice.items);          // Same access pattern
```

**Or use helper function:**
```python
from backend.models.normalized_models import get_invoice_with_details

invoice = await get_invoice_with_details(db, invoice_id)
print(invoice["customer"]["name"])
```

---

### Example 2: Find All Invoices for a Customer

**Before (Slow):**
```javascript
// Must match embedded object
const invoices = await db.invoices.find({
  "customer.email": "acme@example.com"
}).toArray();

// ⚠️ No index on customer.email (can't create efficiently)
// ⚠️ Slow for large datasets
```

**After (Fast):**
```javascript
// Get customer first
const customer = await db.customers.findOne({
  email: "acme@example.com"
});

// Then find invoices by reference
const invoices = await db.invoices.find({
  customer_id: customer._id
}).toArray();

// ✅ Index on customer_id makes this fast
// ✅ Can use explain() to verify index usage
```

---

### Example 3: Product Sales Analysis (NEW!)

**Before:**
```javascript
// ❌ IMPOSSIBLE - products only exist as strings in invoice items
// Can't query: "Which invoices included Office Supplies?"
```

**After:**
```javascript
// ✅ POSSIBLE - products are references
const product = await db.products.findOne({
  name: "Office Supplies"
});

// Find all invoice items for this product
const items = await db.invoice_items.find({
  product_id: product._id
}).toArray();

// Get unique invoices
const invoiceIds = [...new Set(items.map(i => i.invoice_id))];

// Aggregate sales
const totalSales = items.reduce((sum, item) => sum + item.total, 0);
const totalQuantity = items.reduce((sum, item) => sum + item.quantity, 0);

console.log(`Product: ${product.name}`);
console.log(`Total sales: KES ${totalSales:,.2f}`);
console.log(`Total quantity sold: ${totalQuantity}`);
console.log(`Number of invoices: ${invoiceIds.length}`);
```

---

## 📈 Performance Comparison

### Update Customer Email

| Metric | Before (Denormalized) | After (Normalized) |
|--------|----------------------|-------------------|
| Documents Updated | 4,868 invoices | 1 customer |
| Write Operations | 4,868 | 1 |
| Time | ~30 seconds | < 1 second |
| Risk | Partial update | Atomic |

### Query All Invoices for Customer

| Metric | Before | After |
|--------|--------|-------|
| Query | Slow (no index on embedded field) | Fast (indexed reference) |
| Scalability | Degrades with data size | Maintains performance |

### Product Analytics

| Metric | Before | After |
|--------|--------|-------|
| Capability | ❌ Not possible | ✅ Fully supported |
| Query Speed | N/A | Fast (indexed) |

---

## 🎓 Key Takeaways

### Normalization Benefits

1. **Data Integrity** ✅
   - Single source of truth
   - No duplicate data
   - Referential integrity

2. **Maintainability** ✅
   - Update once, reflect everywhere
   - Clear relationships
   - Easier to understand

3. **Query Capabilities** ✅
   - New query possibilities (product analytics)
   - Better indexes
   - Faster filtered queries

4. **Scalability** ✅
   - Smaller database size
   - Better performance at scale
   - Easier to optimize

### Trade-offs

1. **Query Complexity** ⚠️
   - Need $lookup for joins
   - Slightly slower for simple reads
   - More complex aggregation pipelines

2. **Application Changes** ⚠️
   - Code updates required
   - Testing needed
   - Migration effort

**Verdict:** Benefits far outweigh trade-offs for a growing application! 🚀

---

**Visual Guide Version:** 1.0  
**Date:** October 14, 2025  
**Status:** ✅ Ready for Implementation
