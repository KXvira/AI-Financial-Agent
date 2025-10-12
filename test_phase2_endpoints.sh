#!/bin/bash

echo "=========================================="
echo "Testing Phase 2 Endpoints"
echo "=========================================="
echo ""

# Test 1: Get customer list
echo "1. Testing /reports/customers endpoint..."
curl -s http://localhost:8000/reports/customers | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

# Test 2: Test reconciliation summary
echo "2. Testing /reports/reconciliation/summary endpoint..."
curl -s "http://localhost:8000/reports/reconciliation/summary?days=30" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 3: Test reconciliation report
echo "3. Testing /reports/reconciliation endpoint..."
curl -s "http://localhost:8000/reports/reconciliation?start_date=2025-01-01&end_date=2025-10-12" | python3 -m json.tool | head -40
echo ""
echo "---"
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="
