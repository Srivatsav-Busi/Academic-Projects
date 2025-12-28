#!/usr/bin/env python3
"""
Simple Google Drive setup script that handles OAuth without redirect URI issues.
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_google_drive_simple():
    """Set up Google Drive with a simpler OAuth flow."""
    print("🔧 Simple Google Drive Setup")
    print("=" * 40)
    
    # Check if credentials.json exists
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found!")
        print("Please download it from Google Cloud Console first.")
        return False
    
    print("✅ credentials.json found")
    
    try:
        from google_drive_service import GoogleDriveService
        
        # Create service
        service = GoogleDriveService()
        
        print("🔐 Starting authentication...")
        print("This will open a browser window for Google sign-in.")
        print("If you see a redirect URI error, follow the setup guide in GOOGLE_DRIVE_SETUP.md")
        
        # Authenticate
        if service.authenticate():
            print("✅ Authentication successful!")
            
            # Test folder access
            target_folder_id = "1aAPPAvPlgq5VTHbMM-QV4TRban-NZ1oF"
            print(f"📁 Testing access to your folder...")
            
            if service.use_existing_folder(target_folder_id):
                print("✅ Successfully connected to your Google Drive folder!")
                print(f"📁 Folder URL: https://drive.google.com/drive/folders/{target_folder_id}")
                
                # Test upload (optional)
                print("\n🧪 Testing upload capability...")
                test_content = b"Test resume content"
                test_result = service.upload_resume(
                    test_content,
                    "test_resume.docx",
                    "Test Position",
                    "Test Company"
                )
                
                if test_result:
                    print("✅ Upload test successful!")
                    print(f"📄 Test file uploaded: {test_result['web_view_link']}")
                    
                    # Clean up test file
                    try:
                        service.service.files().delete(fileId=test_result['file_id']).execute()
                        print("🧹 Test file cleaned up")
                    except:
                        print("⚠️ Could not clean up test file (you can delete it manually)")
                else:
                    print("⚠️ Upload test failed, but authentication worked")
                
                print("\n🎉 Google Drive setup complete!")
                print("You can now use the job search assistant with Google Drive uploads.")
                return True
            else:
                print("❌ Could not access your target folder")
                print("Please check that the folder ID is correct and you have access to it.")
                return False
        else:
            print("❌ Authentication failed")
            print("Please check your credentials and try again.")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure credentials.json is valid")
        print("2. Check that Google Drive API is enabled in your project")
        print("3. Follow the setup guide in GOOGLE_DRIVE_SETUP.md")
        return False

if __name__ == "__main__":
    success = setup_google_drive_simple()
    
    if success:
        print("\n✅ Setup complete! You can now run: ./run.py")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)







