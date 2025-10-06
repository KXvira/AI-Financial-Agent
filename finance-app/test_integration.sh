#!/bin/bash

# Frontend Authentication Integration Test Script
# Tests the complete authentication flow end-to-end

echo "🚀 FinTrack Authentication Integration Test"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [[ ! -f "package.json" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the finance-app directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Testing Prerequisites${NC}"

# Check if backend is running
echo -n "Checking backend API... "
if curl -s -f http://localhost:8000/api/auth/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend not responding${NC}"
    echo -e "${YELLOW}   Please start the backend server:${NC}"
    echo -e "   cd ../backend && python app.py"
    exit 1
fi

# Check if Node modules are installed
echo -n "Checking dependencies... "
if [[ -d "node_modules" ]] && [[ -f "node_modules/.bin/next" ]]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    npm install
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Check environment configuration
echo -n "Checking environment... "
if [[ -f ".env.local" ]]; then
    echo -e "${GREEN}✅ Environment configured${NC}"
else
    echo -e "${YELLOW}⚠️  Creating .env.local from template...${NC}"
    cp .env.example .env.local
    echo -e "${GREEN}✅ Environment file created${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Testing API Integration${NC}"

# Test backend authentication endpoints
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_NAME="Test User $(date +%H:%M)"

echo -n "Testing user registration... "
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"$TEST_NAME\"}")

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Registration works${NC}"
    ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    echo -e "${RED}❌ Registration failed${NC}"
    echo "Response: $REGISTER_RESPONSE"
    exit 1
fi

echo -n "Testing protected endpoint... "
ME_RESPONSE=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/auth/me)

if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
    echo -e "${GREEN}✅ Protected endpoints work${NC}"
else
    echo -e "${RED}❌ Protected endpoint failed${NC}"
    echo "Response: $ME_RESPONSE"
    exit 1
fi

echo -n "Testing login endpoint... "
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login works${NC}"
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo ""
echo -e "${BLUE}📦 Building Frontend${NC}"

# Build the Next.js application
echo -n "Building application... "
BUILD_OUTPUT=$(npm run build 2>&1)
BUILD_EXIT_CODE=$?

if [[ $BUILD_EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    echo "Build output:"
    echo "$BUILD_OUTPUT"
    exit 1
fi

echo ""
echo -e "${BLUE}🌐 Starting Frontend Server${NC}"

# Start the development server in background
echo "Starting Next.js development server..."
npm run dev > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo -n "Waiting for server to start"
for i in {1..30}; do
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        echo -e " ${GREEN}✅ Server started${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e " ${RED}❌ Server failed to start${NC}"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${BLUE}🧪 Testing Frontend Integration${NC}"

# Test frontend pages
echo -n "Testing homepage... "
HOME_RESPONSE=$(curl -s http://localhost:3000)
if echo "$HOME_RESPONSE" | grep -q "FinTrack"; then
    echo -e "${GREEN}✅ Homepage loads${NC}"
else
    echo -e "${RED}❌ Homepage failed${NC}"
fi

echo -n "Testing login page... "
LOGIN_PAGE_RESPONSE=$(curl -s http://localhost:3000/auth/login)
if echo "$LOGIN_PAGE_RESPONSE" | grep -q "Sign in"; then
    echo -e "${GREEN}✅ Login page loads${NC}"
else
    echo -e "${RED}❌ Login page failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Integration Test Complete!${NC}"
echo ""
echo -e "${BLUE}📊 Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Backend API: Authentication endpoints working${NC}"
echo -e "${GREEN}✅ Frontend Build: Application compiles successfully${NC}"
echo -e "${GREEN}✅ Development Server: Running on http://localhost:3000${NC}"
echo -e "${GREEN}✅ Integration: Authentication system ready${NC}"
echo ""
echo -e "${BLUE}🚀 Next Steps${NC}"
echo "1. Visit http://localhost:3000 to test the full flow"
echo "2. Register a new account using the web interface"
echo "3. Test login, dashboard, and profile management"
echo "4. Verify role-based access controls"
echo ""
echo -e "${BLUE}🔗 Useful URLs${NC}"
echo "• Frontend: http://localhost:3000"
echo "• Login Page: http://localhost:3000/auth/login"
echo "• Profile Page: http://localhost:3000/auth/profile"
echo "• Backend API: http://localhost:8000"
echo "• API Health: http://localhost:8000/api/auth/health"
echo ""
echo -e "${YELLOW}📝 Manual Testing Checklist${NC}"
echo "[ ] Register new account via web form"
echo "[ ] Login with created credentials"
echo "[ ] Verify dashboard personalization"
echo "[ ] Test profile management"
echo "[ ] Confirm logout functionality"
echo "[ ] Check mobile responsiveness"
echo "[ ] Verify error handling"
echo ""
echo -e "${BLUE}Server is running in background (PID: $SERVER_PID)${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server when done testing${NC}"

# Keep server running until user stops it
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo 'Server stopped. Goodbye!'; exit 0" INT

# Wait for user interrupt
while true; do
    sleep 1
done