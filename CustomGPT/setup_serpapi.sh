#!/bin/bash

# setup_serpapi.sh
# This script helps set up your SerpAPI key for job search functionality.

echo -e "\033[0;34m🔧 Setting up SerpAPI for Job Search\033[0m"
echo "=================================================="

# Check if an API key is provided as an argument
if [ -z "$1" ]; then
    echo -e "\033[0;31m❌ Error: No SerpAPI key provided.\033[0m"
    echo "Usage: ./setup_serpapi.sh <YOUR_SERPAPI_KEY>"
    echo ""
    echo "Get your free API key at: https://serpapi.com/"
    echo "Free tier includes 100 searches per month"
    exit 1
fi

SERPAPI_KEY="$1"
echo -e "\033[0;32m✅ Using provided API key\033[0m"

# Create or update .env file
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    # Update existing key or add new one
    if grep -q "^SERPAPI_KEY=" "$ENV_FILE"; then
        sed -i '' "s/^SERPAPI_KEY=.*/SERPAPI_KEY=$SERPAPI_KEY/" "$ENV_FILE"
    else
        echo "SERPAPI_KEY=$SERPAPI_KEY" >> "$ENV_FILE"
    fi
else
    echo "SERPAPI_KEY=$SERPAPI_KEY" > "$ENV_FILE"
fi
echo -e "\033[0;32m✅ Created/updated .env file with SerpAPI key\033[0m"

# Install the required package
echo -e "\033[0;34m📦 Installing google-search-results package...\033[0m"
pip install google-search-results
if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Package installed successfully\033[0m"
else
    echo -e "\033[0;31m❌ Error installing package. Please run: pip install google-search-results\033[0m"
    exit 1
fi

# Test the setup
echo -e "\033[0;34m🧪 Testing SerpAPI setup...\033[0m"
python3 -c "
import os
import sys
sys.path.append('src')

try:
    from jobs_search import JobSearchService
    service = JobSearchService()
    print('✅ SerpAPI setup successful!')
    print('✅ Job search service initialized')
    print('✅ Ready to search for jobs!')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m🎉 SerpAPI setup complete!\033[0m"
    echo ""
    echo "Next steps:"
    echo "1. Run the application: ./run.py"
    echo "2. Open: http://localhost:8501"
    echo "3. Go to the 'Job Search' tab"
    echo "4. Start searching for ML Engineer, Data Scientist, and ML Infrastructure Engineer jobs!"
    echo ""
    echo "Features available:"
    echo "• Search all target roles at once"
    echo "• Search by specific company"
    echo "• Custom search with filters"
    echo "• Save results to job tracker"
    echo "• Export results to CSV"
    echo ""
    echo "Your SerpAPI key is now configured and ready to use! 🚀"
else
    echo -e "\033[0;31m❌ Setup test failed. Please check your API key and try again.\033[0m"
    exit 1
fi
