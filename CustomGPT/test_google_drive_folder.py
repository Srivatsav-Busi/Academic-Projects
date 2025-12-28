#!/usr/bin/env python3
"""
Test script to verify Google Drive folder access.
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_google_drive_folder():
    """Test access to the specific Google Drive folder."""
    print("🧪 Testing Google Drive Folder Access...")
    print("=" * 50)
    
    try:
        from google_drive_service import create_google_drive_service
        
        # Create service
        service = create_google_drive_service()
        if not service:
            print("❌ Failed to create Google Drive service")
            return False
        
        # Test folder access
        target_folder_id = "1aAPPAvPlgq5VTHbMM-QV4TRban-NZ1oF"
        print(f"📁 Testing access to folder: {target_folder_id}")
        
        if service.use_existing_folder(target_folder_id):
            print("✅ Successfully connected to your Google Drive folder!")
            print(f"📁 Folder URL: https://drive.google.com/drive/folders/{target_folder_id}")
            
            # Test folder info
            try:
                folder_info = service.service.files().get(
                    fileId=target_folder_id,
                    fields='id,name,mimeType,createdTime,modifiedTime'
                ).execute()
                
                print(f"📋 Folder Name: {folder_info.get('name', 'Unknown')}")
                print(f"📅 Created: {folder_info.get('createdTime', 'Unknown')}")
                print(f"📅 Modified: {folder_info.get('modifiedTime', 'Unknown')}")
                
            except Exception as e:
                print(f"⚠️ Could not retrieve folder details: {e}")
            
            return True
        else:
            print("❌ Failed to access the specified Google Drive folder")
            print("Please check:")
            print("1. The folder ID is correct")
            print("2. You have access to the folder")
            print("3. Your Google Drive credentials are valid")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Drive folder: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Drive Folder Access Test")
    print("=" * 50)
    
    success = test_google_drive_folder()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Google Drive folder access test passed!")
        print("✅ Your resumes will be uploaded to the correct folder")
    else:
        print("❌ Google Drive folder access test failed!")
        print("Please check your setup and try again.")







