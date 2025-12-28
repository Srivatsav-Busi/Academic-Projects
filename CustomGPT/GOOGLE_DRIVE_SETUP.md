# Google Drive Setup Guide

## Fixing the "redirect_uri_mismatch" Error

The error you're seeing occurs because the redirect URI in your Google Cloud Console doesn't match what the application expects.

### Step 1: Update Google Cloud Console Settings

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create a new one)
3. **Navigate to APIs & Services > Credentials**
4. **Click on your OAuth 2.0 Client ID** (the one you downloaded as credentials.json)
5. **In the "Authorized redirect URIs" section, add these URIs:**
   ```
   http://localhost:8080/
   http://127.0.0.1:8080/
   http://localhost:8080
   http://127.0.0.1:8080
   ```

### Step 2: Save and Download Updated Credentials

1. **Click "Save"** in the Google Cloud Console
2. **Download the updated credentials.json** file
3. **Replace the existing credentials.json** in your project root

### Step 3: Test the Setup

Run the test script to verify everything works:

```bash
python3 test_google_drive_folder.py
```

### Step 4: Alternative Setup (If Still Having Issues)

If you're still having issues, try this alternative approach:

1. **In Google Cloud Console**, go to your OAuth 2.0 Client ID
2. **Add these additional redirect URIs:**
   ```
   http://localhost:8080/oauth2callback
   http://127.0.0.1:8080/oauth2callback
   urn:ietf:wg:oauth:2.0:oob
   ```

### Step 5: Verify Your Setup

After updating the redirect URIs:

1. **Delete the existing token.json** file (if it exists):
   ```bash
   rm token.json
   ```

2. **Run the test again**:
   ```bash
   python3 test_google_drive_folder.py
   ```

3. **A browser window should open** asking you to sign in to Google
4. **Grant the necessary permissions** for Google Drive access
5. **The test should complete successfully**

### Troubleshooting

If you're still having issues:

1. **Check that Google Drive API is enabled** in your Google Cloud project
2. **Verify the OAuth consent screen** is configured properly
3. **Make sure you're using the correct Google account** that has access to the target folder
4. **Try creating a new OAuth 2.0 Client ID** if the current one doesn't work

### Your Target Folder

Once authenticated, resumes will be uploaded to:
**https://drive.google.com/drive/folders/1aAPPAvPlgq5VTHbMM-QV4TRban-NZ1oF**

### Next Steps

After successful authentication:
1. Run your application: `./run.py`
2. Go to Job Search page
3. Click "Generate All Resumes"
4. Check "Upload to Google Drive" option
5. Watch as resumes are uploaded to your folder!







