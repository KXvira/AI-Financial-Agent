#!/bin/bash

# Comprehensive Audit Verification Runner
# Runs both backend and frontend verification scripts

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     FULL-STACK AUDIT VERIFICATION SUITE                         ║"
echo "║     Testing Backend, Database, and Frontend Integration         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend is not running on port 8000"
    echo "   Please start backend with: cd backend && uvicorn main:app --reload"
    exit 1
fi

# Check if frontend is running
echo "🔍 Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on port 3000"
else
    echo "⚠️  Frontend is not running on port 3000"
    echo "   Frontend tests will be skipped"
    echo "   Start frontend with: cd finance-app && npm run dev"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PART 1: Backend & Database Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run Python backend verification
if command -v python3 &> /dev/null; then
    echo "🚀 Running backend verification script..."
    python3 verify_audit.py --base-url http://localhost:8000
    BACKEND_EXIT=$?
else
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PART 2: Frontend Integration Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run Node frontend verification
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    if command -v node &> /dev/null; then
        echo "🚀 Running frontend verification script..."
        node verify_frontend.js
        FRONTEND_EXIT=$?
    else
        echo "❌ Node.js not found. Please install Node.js 18+"
        FRONTEND_EXIT=1
    fi
else
    echo "⚠️  Skipping frontend tests (frontend not running)"
    FRONTEND_EXIT=0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VERIFICATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
if [ $BACKEND_EXIT -eq 0 ]; then
    echo "✅ Backend verification: PASSED"
else
    echo "❌ Backend verification: FAILED"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ Frontend verification: PASSED"
else
    echo "❌ Frontend verification: FAILED"
fi

echo ""
echo "📊 Detailed reports saved:"
echo "   - Backend: audit_report_*.json"
echo "   - Frontend: frontend_audit_report_*.json"
echo ""

# Exit with error if any test failed
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    exit 1
fi

exit 0
