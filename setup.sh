#!/bin/bash

# Script to set up Python virtual environment for AI-Financial-Agent

# Define colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AI-Financial-Agent Environment Setup Tool   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 is not installed. Please install Python3 first.${NC}"
    exit 1
fi

# Display Python version
echo -e "${BLUE}Using Python version:${NC}"
python3 --version

# Check if venv module is available
python3 -c "import venv" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Python venv module not found. Please install python3-venv package.${NC}"
    echo -e "${YELLOW}For Ubuntu/Debian: sudo apt-get install python3-venv${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created successfully.${NC}"
else
    echo -e "\n${YELLOW}Virtual environment already exists.${NC}"
fi

# Activate the virtual environment and install dependencies
echo -e "\n${BLUE}Activating virtual environment and installing dependencies...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

# Upgrading pip
echo -e "\n${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "\n${BLUE}Installing project dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Check requirements.txt file.${NC}"
    exit 1
fi

# Create a .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${BLUE}Creating .env file template...${NC}"
    cat > .env << EOF
# AI-Financial-Agent Environment Variables

# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB=financial_agent

# M-Pesa API
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret  
MPESA_SHORTCODE=174379
MPESA_PASS_KEY=your-passkey
MPESA_ENV=sandbox
MPESA_CALLBACK_URL=https://your-domain.com/api/mpesa/callback

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_OUTPUT_TOKENS=2048

# Application Settings
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=your-secret-key
EOF
    echo -e "${GREEN}✓ .env template created. Please update with your API keys before running the app.${NC}"
fi

echo -e "\n${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Environment setup completed successfully!  ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "\n${YELLOW}To activate the virtual environment, run:${NC}"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "\n${YELLOW}To run the application:${NC}"
echo -e "  ${BLUE}python backend/app.py${NC}"
echo -e "\n${YELLOW}Remember to update the .env file with your API keys.${NC}"
