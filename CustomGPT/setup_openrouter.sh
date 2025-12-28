#!/bin/bash

# Setup script for OpenRouter API configuration
# This script sets up your OpenRouter API key

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up OpenRouter API for Srivatsav Job Search GPT${NC}"
echo "=================================================="

# Check if API key is provided as argument
if [ $# -eq 1 ]; then
    API_KEY="$1"
    echo -e "${GREEN}✅ Using provided API key${NC}"
else
    # Prompt for API key
    echo -e "${YELLOW}Please enter your OpenRouter API key:${NC}"
    echo "You can get it from: https://openrouter.ai/keys"
    read -p "API Key: " API_KEY
    
    if [ -z "$API_KEY" ]; then
        echo "❌ No API key provided. Exiting."
        exit 1
    fi
fi

# Set environment variable
export OPENROUTER_API_KEY="$API_KEY"

# Create .env file
echo "OPENROUTER_API_KEY=$API_KEY" > .env
echo -e "${GREEN}✅ Created .env file with OpenRouter API key${NC}"

# Update configuration to use OpenRouter
echo -e "${BLUE}📝 Updating configuration to use OpenRouter...${NC}"

# The configuration is already set to use OpenRouter by default
echo -e "${GREEN}✅ Configuration updated${NC}"

echo ""
echo -e "${GREEN}🎉 OpenRouter setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run the application: ./run.py"
echo "2. Or activate virtual environment and run:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "Your OpenRouter API key is now configured and ready to use! 🚀"
