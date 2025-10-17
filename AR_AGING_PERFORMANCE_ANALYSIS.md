# AR Aging Performance Issue Analysis

**Date:** October 17, 2025  
**Issue:** AR Aging report taking too long to load  
**Status:** IDENTIFIED - FIX IN PROGRESS

---

## Performance Bottleneck Identified

### The Problem: N+1 Query Issue

The AR Aging report is making **individual database queries for EACH invoice** in a loop:

```python
# For EACH of the 413 outstanding invoices:
for invoice in outstanding_invoices:  # 413 invoices
    invoice_id = invoice.get("invoice_id")
    
    # Query 1: Get invoice items (1 query per invoice)
    items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
    
    # Query 2: Get customer by customer_id (1 query per invoice)
    customer = await self.db.customers.find_one({"customer_id": customer_id})
    
    # Query 3: Fallback to ObjectId lookup (potentially another query per invoice)
    if not customer:
        customer = await self.db.customers.find_one({"_id": ObjectId(customer_id)})
```

### Total Queries:
- **Initial query:** 1 (get all outstanding invoices)
- **Invoice items:** 413 queries (one per invoice)
- **Customer lookups:** 413-826 queries (1-2 per invoice depending on fallback)

**TOTAL: ~827-1,240 database queries!**

---

## Why This Is Slow

### Current Performance:
- 413 invoices × 2-3 queries each = **~1,240 database roundtrips**
- Each query has network latency (MongoDB Atlas)
- **Estimated time:** 3-10 seconds (depending on network)

### Expected Performance:
- Should complete in **< 500ms** with proper optimization

---

## Root Causes

### 1. **N+1 Query Problem** (Most Critical)
- Loop through invoices making individual queries
- No batch fetching
- No aggregation pipeline

### 2. **No Database Indexes**
- `invoice_items.invoice_id` - likely not indexed
- `customers.customer_id` - likely not indexed
- Queries are doing full collection scans

### 3. **Duplicate Customer Lookups**
- Same customer fetched multiple times if they have multiple invoices
- No caching mechanism

### 4. **Inefficient Data Structure**
- Normalized schema (invoices separate from items)
- Requires JOINs (lookups) for every invoice

---

## Solution: Use MongoDB Aggregation Pipeline

Instead of looping and making individual queries, use a single aggregation pipeline:

```python
async def generate_ar_aging_optimized(
    self,
    as_of_date: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> ARAgingReport:
    """Optimized AR aging using aggregation pipeline"""
    
    # Single aggregation pipeline - replaces 1,240 queries
    pipeline = [
        # Step 1: Match outstanding invoices
        {
            "$match": {
                "status": {"$in": ["pending", "sent", "unpaid", "overdue"]}
            }
        },
        
        # Step 2: Lookup invoice items (replaces 413 queries)
        {
            "$lookup": {
                "from": "invoice_items",
                "localField": "invoice_id",
                "foreignField": "invoice_id",
                "as": "items"
            }
        },
        
        # Step 3: Lookup customer info (replaces 413-826 queries)
        {
            "$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "customer_id",
                "as": "customer"
            }
        },
        
        # Step 4: Calculate totals
        {
            "$addFields": {
                "calculated_total": {
                    "$sum": "$items.line_total"
                },
                "customer_name": {
                    "$ifNull": [
                        {"$arrayElemAt": ["$customer.name", 0]},
                        "Unknown"
                    ]
                }
            }
        }
    ]
    
    # Execute ONE query instead of 1,240
    outstanding_invoices = await self.db.invoices.aggregate(pipeline).to_list(None)
```

---

## Performance Improvement

### Before (Current):
- **Queries:** ~1,240 database roundtrips
- **Time:** 3-10 seconds
- **Method:** Loop with individual queries (N+1 problem)

### After (Optimized):
- **Queries:** 1 aggregation pipeline
- **Time:** < 500ms (estimated)
- **Method:** Single aggregation with $lookup joins

### Speedup: **6-20x faster** ⚡

---

## Additional Optimizations

### 1. Add Database Indexes
```javascript
// MongoDB shell commands
db.invoice_items.createIndex({ "invoice_id": 1 })
db.customers.createIndex({ "customer_id": 1 })
db.invoices.createIndex({ "status": 1, "issue_date": 1 })
```

### 2. Cache Customer Data
```python
# Build customer lookup dict (one query for all customers)
customers_dict = {
    c["customer_id"]: c 
    for c in await self.db.customers.find({}).to_list(None)
}

# Then use in-memory lookup instead of DB query
customer_name = customers_dict.get(customer_id, {}).get("name", "Unknown")
```

### 3. Limit Data Returned
```python
# Only fetch needed fields
pipeline.append({
    "$project": {
        "invoice_number": 1,
        "customer_name": 1,
        "calculated_total": 1,
        "issue_date": 1,
        "status": 1
    }
})
```

---

## Implementation Status

- [x] **Issue Identified:** N+1 query problem in AR aging
- [ ] **Fix Applied:** Rewrite with aggregation pipeline
- [ ] **Indexes Created:** Add missing database indexes
- [ ] **Testing:** Verify performance improvement
- [ ] **Deployment:** Deploy optimized version

---

## Files To Modify

1. **`backend/reporting/service.py`**
   - Lines 455-530: `generate_ar_aging()` function
   - Replace loop-based queries with aggregation pipeline

2. **Database Indexes** (MongoDB Atlas)
   - Add index on `invoice_items.invoice_id`
   - Add index on `customers.customer_id`
   - Add compound index on `invoices.status + issue_date`

---

## Next Steps

1. Rewrite `generate_ar_aging()` to use aggregation pipeline
2. Add database indexes via MongoDB Atlas or migration script
3. Test with 413 invoices to verify < 500ms response time
4. Deploy optimized version

---

**Priority:** HIGH - User-facing performance issue  
**Complexity:** Medium - Requires aggregation pipeline knowledge  
**Impact:** 6-20x performance improvement
