#!/bin/bash
# Test Email Service API

echo "======================================"
echo "Testing Email Service API"
echo "======================================"
echo ""

# Test 1: Check email configuration
echo "1. Testing email configuration endpoint..."
response=$(curl -s http://localhost:8000/api/email/test)
echo "Response: $response"
echo ""

# Test 2: Get email history
echo "2. Testing email history endpoint..."
response=$(curl -s http://localhost:8000/api/email/history)
echo "Response: $response"
echo ""

# Test 3: Health check
echo "3. Testing health check endpoint..."
response=$(curl -s http://localhost:8000/health)
echo "Response: $response"
echo ""

echo "======================================"
echo "Tests Complete!"
echo "======================================"
