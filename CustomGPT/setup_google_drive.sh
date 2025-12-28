#!/bin/bash

# setup_google_drive.sh
# This script helps set up Google Drive integration for the Srivatsav Job Search GPT.

echo -e "\033[0;34m🔧 Setting up Google Drive Integration\033[0m"
echo "=================================================="

# Check if required packages are installed
echo -e "\033[0;34m📦 Installing required packages...\033[0m"
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 python-docx

if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Packages installed successfully\033[0m"
else
    echo -e "\033[0;31m❌ Error installing packages. Please check your pip installation.\033[0m"
    exit 1
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo -e "\033[0;31m❌ credentials.json not found!\033[0m"
    echo ""
    echo "To set up Google Drive integration:"
    echo "1. Go to Google Cloud Console: https://console.cloud.google.com/"
    echo "2. Create a new project or select existing one"
    echo "3. Enable Google Drive API"
    echo "4. Create credentials (OAuth 2.0 Client ID)"
    echo "5. Download the credentials.json file"
    echo "6. Place it in this directory"
    echo ""
    echo "Detailed steps:"
    echo "1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "2. Click 'Create Credentials' > 'OAuth 2.0 Client ID'"
    echo "3. Choose 'Desktop application'"
    echo "4. Download the JSON file and rename it to 'credentials.json'"
    echo "5. Place it in: $(pwd)/credentials.json"
    echo ""
    echo "After placing credentials.json, run this script again."
    exit 1
fi

echo -e "\033[0;32m✅ credentials.json found\033[0m"

# Test Google Drive setup
echo -e "\033[0;34m🧪 Testing Google Drive setup...\033[0m"
python3 -c "
import sys
import os
sys.path.append('src')
try:
    from google_drive_service import create_google_drive_service
    service = create_google_drive_service()
    if service:
        print('\033[0;32m✅ Google Drive setup successful!\033[0m')
        print('\033[0;32m✅ Authentication completed\033[0m')
        print('\033[0;32m✅ Ready to upload resumes to Google Drive!\033[0m')
    else:
        print('\033[0;31m❌ Google Drive setup failed\033[0m')
        sys.exit(1)
except ImportError as e:
    print(f'\033[0;31m❌ Import error: {e}\033[0m')
    sys.exit(1)
except Exception as e:
    print(f'\033[0;31m❌ Error: {e}\033[0m')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
echo -e "\033[0;32m🎉 Google Drive setup complete!\033[0m"
echo ""
echo "✅ Your resumes will be uploaded to:"
echo "   https://drive.google.com/drive/folders/1aAPPAvPlgq5VTHbMM-QV4TRban-NZ1oF"
echo ""
echo "Next steps:"
echo "1. Run the application: ./run.py"
echo "2. Go to Job Search page"
echo "3. Click 'Generate All Resumes'"
echo "4. Check 'Upload to Google Drive' option"
echo "5. Your resumes will be automatically uploaded to your specified folder!"
echo ""
echo "Your Google Drive integration is now ready! 🚀"
else
    echo -e "\033[0;31m❌ Setup test failed. Please check your credentials and try again.\033[0m"
    exit 1
fi
