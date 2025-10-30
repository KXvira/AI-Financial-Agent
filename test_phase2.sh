#!/bin/bash
# Phase 2 Feature Testing Script
# Tests all new features systematically

echo "🧪 PHASE 2 FEATURE TESTING SUITE"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url")
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        if [ ! -z "$expected" ]; then
            echo "$response" | head -n-1 | python3 -m json.tool | head -5
        fi
    else
        echo -e "${RED}❌ FAIL (Status: $status_code)${NC}"
        ((FAILED++))
    fi
    echo ""
}

# Test results function
print_summary() {
    echo ""
    echo "=================================="
    echo "📊 TEST RESULTS SUMMARY"
    echo "=================================="
    echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
    echo -e "❌ Failed: ${RED}$FAILED${NC}"
    echo -e "📈 Total:  $((PASSED + FAILED))"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Check output above.${NC}"
    fi
}

echo "🔧 Phase 1: Backend API Tests"
echo "--------------------------------"

# Test existing endpoints
test_endpoint "Dashboard Metrics" "http://localhost:8000/api/reports/dashboard-metrics" "yes"
test_endpoint "Income Statement" "http://localhost:8000/api/reports/income-statement?start_date=2024-01-01&end_date=2024-12-31" "yes"
test_endpoint "Cash Flow" "http://localhost:8000/api/reports/cash-flow?start_date=2024-01-01&end_date=2024-12-31" "yes"
test_endpoint "AR Aging" "http://localhost:8000/api/reports/ar-aging" "yes"

echo ""
echo "🆕 Phase 2: New Trend Analysis Endpoints"
echo "--------------------------------"

# Test new trend endpoints
test_endpoint "Revenue Trends (6 months)" "http://localhost:8000/api/reports/trends/revenue?months=6" "yes"
test_endpoint "Expense Trends (6 months)" "http://localhost:8000/api/reports/trends/expenses?months=6" "yes"
test_endpoint "Month-over-Month Comparison" "http://localhost:8000/api/reports/comparison/mom" "yes"
test_endpoint "Year-over-Year Comparison" "http://localhost:8000/api/reports/comparison/yoy" "yes"

echo ""
echo "🎨 Phase 3: Frontend Pages"
echo "--------------------------------"

# Test frontend pages
test_endpoint "Reports Hub" "http://localhost:3000/reports"
test_endpoint "Income Statement Page" "http://localhost:3000/reports/income-statement"
test_endpoint "Cash Flow Page" "http://localhost:3000/reports/cash-flow"
test_endpoint "AR Aging Page" "http://localhost:3000/reports/ar-aging"
test_endpoint "Dashboard Page" "http://localhost:3000/reports/dashboard"
test_endpoint "Trends Page (NEW)" "http://localhost:3000/reports/trends"

# Print summary
print_summary

echo ""
echo "=================================="
echo "📋 MANUAL TESTING CHECKLIST"
echo "=================================="
echo ""
echo "Open these URLs in your browser for visual testing:"
echo ""
echo "1. 📊 Reports Hub:"
echo "   http://localhost:3000/reports"
echo ""
echo "2. 💰 Income Statement (with charts):"
echo "   http://localhost:3000/reports/income-statement"
echo "   ✓ Check: 3 charts display"
echo "   ✓ Check: Export buttons work (Excel, PDF, CSV)"
echo ""
echo "3. 💵 Cash Flow (with charts):"
echo "   http://localhost:3000/reports/cash-flow"
echo "   ✓ Check: 3 charts display (Waterfall, Comparison, Categories)"
echo "   ✓ Check: Export buttons work"
echo ""
echo "4. 📅 AR Aging (with charts):"
echo "   http://localhost:3000/reports/ar-aging"
echo "   ✓ Check: 2 charts display (Aging Distribution, Top Customers)"
echo "   ✓ Check: Export buttons work"
echo ""
echo "5. 📈 Dashboard (with charts):"
echo "   http://localhost:3000/reports/dashboard"
echo "   ✓ Check: 4 charts display"
echo "   ✓ Check: Export buttons work"
echo ""
echo "6. 📊 Trends Analysis (NEW):"
echo "   http://localhost:3000/reports/trends"
echo "   ✓ Check: Revenue trend chart displays"
echo "   ✓ Check: Expense trend chart displays"
echo "   ✓ Check: MoM comparison card shows"
echo "   ✓ Check: YoY comparison card shows"
echo "   ✓ Check: Period selector works (3, 6, 12, 24 months)"
echo ""
echo "=================================="
echo "🎯 FEATURE CHECKLIST"
echo "=================================="
echo ""
echo "Charts (13 total):"
echo "  [ ] Income Statement: 3 charts"
echo "  [ ] Cash Flow: 3 charts"
echo "  [ ] AR Aging: 2 charts"
echo "  [ ] Dashboard: 4 charts"
echo "  [ ] Trends: 2 line charts"
echo ""
echo "Export Functionality (4 formats per report):"
echo "  [ ] Excel exports work"
echo "  [ ] PDF exports work"
echo "  [ ] CSV exports work"
echo "  [ ] Print works"
echo ""
echo "Advanced Filtering:"
echo "  [ ] Date presets work (This Month, Last Month, etc.)"
echo "  [ ] Custom date range works"
echo "  [ ] Clear all button works"
echo "  [ ] Collapsible UI works"
echo ""
echo "Trend Analysis:"
echo "  [ ] Revenue trends display"
echo "  [ ] Expense trends display"
echo "  [ ] Period selector changes data"
echo "  [ ] MoM comparison accurate"
echo "  [ ] YoY comparison accurate"
echo ""
echo "=================================="
echo "🚀 Quick Access Links"
echo "=================================="
echo ""
echo "Backend API Documentation:"
echo "  http://localhost:8000/docs"
echo ""
echo "Backend Health Check:"
echo "  http://localhost:8000/health"
echo ""
echo "Frontend Reports:"
echo "  http://localhost:3000/reports"
echo ""
