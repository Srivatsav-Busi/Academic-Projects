"""
Google Drive Service for uploading generated resumes.
Handles authentication and file uploads to Google Drive.
"""

import os
import io
import yaml
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

logger = logging.getLogger(__name__)

class GoogleDriveService:
    """Service for uploading files to Google Drive."""
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json", config_file: str = "config/google_drive_config.yaml"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.config_file = config_file
        self.service = None
        self.folder_id = None
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Google Drive configuration from YAML file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file not found: {self.config_file}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API."""
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.error("Google Drive libraries not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
            return False
            
        creds = None
        
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.info("Please download credentials.json from Google Cloud Console")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                # Use a specific port and redirect URI for better compatibility
                creds = flow.run_local_server(port=8080, redirect_uri_trailing_slash=False)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive authentication successful")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
            return False
    
    def create_resume_folder(self, folder_name: str = "Generated Resumes") -> Optional[str]:
        """Create a folder for storing resumes in Google Drive."""
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
            
        try:
            # Check if folder already exists
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            items = results.get('files', [])
            if items:
                self.folder_id = items[0]['id']
                logger.info(f"Using existing folder: {folder_name}")
                return self.folder_id
            
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            self.folder_id = folder.get('id')
            logger.info(f"Created folder: {folder_name} (ID: {self.folder_id})")
            return self.folder_id
            
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return None
    
    def use_existing_folder(self, folder_id: str) -> bool:
        """Use an existing Google Drive folder by ID."""
        if not self.service:
            logger.error("Google Drive service not initialized")
            return False
            
        try:
            # Verify the folder exists and is accessible
            folder = self.service.files().get(
                fileId=folder_id,
                fields='id,name,mimeType'
            ).execute()
            
            if folder.get('mimeType') == 'application/vnd.google-apps.folder':
                self.folder_id = folder_id
                logger.info(f"Using existing folder: {folder.get('name')} (ID: {folder_id})")
                return True
            else:
                logger.error(f"ID {folder_id} is not a folder")
                return False
                
        except Exception as e:
            logger.error(f"Failed to access folder {folder_id}: {e}")
            return False
    
    def upload_resume(self, file_content: bytes, filename: str, job_title: str, company: str) -> Optional[Dict[str, Any]]:
        """Upload a resume file to Google Drive."""
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
            
        if not self.folder_id:
            logger.error("No folder ID set. Call create_resume_folder() first.")
            return None
            
        try:
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id],
                'description': f"Generated resume for {job_title} at {company}"
            }
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            logger.info(f"Uploaded resume: {filename} (ID: {file.get('id')})")
            
            return {
                'file_id': file.get('id'),
                'filename': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink'),
                'job_title': job_title,
                'company': company,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload resume {filename}: {e}")
            return None
    
    def upload_multiple_resumes(self, resumes_data: list) -> list:
        """Upload multiple resumes to Google Drive."""
        if not self.service:
            logger.error("Google Drive service not initialized")
            return []
            
        uploaded_files = []
        
        for resume_data in resumes_data:
            try:
                result = self.upload_resume(
                    file_content=resume_data['file_content'],
                    filename=resume_data['filename'],
                    job_title=resume_data['job_title'],
                    company=resume_data['company']
                )
                
                if result:
                    uploaded_files.append(result)
                    
            except Exception as e:
                logger.error(f"Failed to upload resume for {resume_data.get('job_title', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} resumes to Google Drive")
        return uploaded_files
    
    def get_folder_link(self) -> Optional[str]:
        """Get the web view link for the resume folder."""
        if not self.folder_id:
            return None
            
        try:
            folder = self.service.files().get(
                fileId=self.folder_id,
                fields='webViewLink'
            ).execute()
            
            return folder.get('webViewLink')
        except Exception as e:
            logger.error(f"Failed to get folder link: {e}")
            return None

def create_google_drive_service() -> Optional[GoogleDriveService]:
    """Create and authenticate a Google Drive service."""
    if not GOOGLE_DRIVE_AVAILABLE:
        logger.warning("Google Drive libraries not available")
        return None
        
    service = GoogleDriveService()
    if service.authenticate():
        return service
    else:
        return None
