from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import pickle
from googleapiclient.http import MediaIoBaseDownload
import io

class GoogleDriveAPI:
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # def __init__(self):
    #     #self.token_path = r'C:\Users\trent\VSCode\registerturn\token.pickle'
    #     self.token_path = os.path.join(os.getcwd(), 'token.pickle')
    #     self.creds = self.authenticate()
    #     self.service = build('drive', 'v3', credentials=self.creds)
    #     self.secret_file = os.path.join(os.getcwd(), 'credentials.json')

    # def authenticate(self):
    #     creds = None
    #     if os.path.exists(self.token_path):
    #         with open(self.token_path, 'rb') as token:
    #             creds = pickle.load(token)

    #     if not creds or not creds.valid:
    #         if creds and creds.expired and creds.refresh_token:
    #             creds.refresh(Request())
    #         else:
    #             flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, self.SCOPES)
    #             creds = flow.run_local_server(port=0)
    #         with open(self.token_path, 'wb') as token:
    #             pickle.dump(creds, token)

    #     return creds
    def __init__(self, force_new_token=False):
        # Set the path to `credentials.json` in the `testflaskapp` directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Goes up one level from `modules`
        self.secret_file = os.path.join(base_dir, 'credentials.json')

        # Define separate token paths for different environments
        if os.environ.get("PYTHONANYWHERE_DOMAIN"):
            self.token_path = os.path.join(base_dir, 'server_token.pickle')
        else:
            self.token_path = os.path.join(base_dir, 'local_token.pickle')

        self.creds = self.authenticate(force_new_token=force_new_token)
        self.service = build('drive', 'v3', credentials=self.creds)

    def authenticate(self, force_new_token=False):
        creds = None
        if not force_new_token and os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds
     
    def find_file(self, file_name):
        try:
            query = f"name='{file_name}' and trashed=false"
            response = self.service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)').execute()
            
            files = response.get('files', [])
            if files:
                file_id = files[0]['id']
                mime_type = files[0]['mimeType']
                print(f'File found: {file_name} with ID: {file_id} and MIME type: {mime_type}')
                return file_id, mime_type
            else:
                print(f'File {file_name} not found.')
                return None, None
        except Exception as e:
            print(f"An error occurred while searching for the file: {e}")
            return None, None

    def trash_file(self, file_id):
        try:
            if file_id:
                self.service.files().update(fileId=file_id, body={'trashed': True}).execute()
                print(f'File with ID {file_id} moved to trash.')
            else:
                print(f"No file ID provided for trashing.")
        except Exception as e:
            print(f"An error occurred while trashing the file: {e}")

    def upload_file(self, file_name_on_drive, file_path, mime_type='application/vnd.google-apps.spreadsheet'):
        try:
            file_metadata = {'name': file_name_on_drive, 'mimeType': mime_type}
            media = MediaFileUpload(file_path, mimetype='text/csv')
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')
            print(f'File uploaded with ID: {file_id}')
            return file_id
        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")
            return None

    def convert_google_sheets_to_csv(self, file_id, destination_path):
        try:
            request = self.service.files().export_media(fileId=file_id, mimeType='text/csv')
            with open(destination_path, 'wb') as f:
                f.write(request.execute())
            print(f'Google Sheets file {file_id} converted and saved as CSV to {destination_path}')
        except Exception as e:
            print(f"An error occurred while converting Google Sheets to CSV: {e}")

    def delete_file(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
            print('File Deleted')
        except Exception as e:
            print('An error occurred:', e)

    def empty_trash(self):
        try:
            self.service.files().emptyTrash().execute()
            print("Trash emptied.")
        except Exception as e:
            print(f"An error occurred while emptying the trash: {e}")

    def download_file(self, file_name, destination_path):
        results = self.service.files().list(q=f"name='{file_name}'", spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if not items:
            print(f"File '{file_name}' not found.")
            return None
        
        file_id = items[0]['id']
        print(f"Found file '{file_name}' with ID: {file_id}")
        
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        
        print(f"File '{file_name}' downloaded to {destination_path}.")
        return destination_path

# Add this function:
def get_tracked_ticker_from_cloud(csv_file,file_name):
    """Export the Google Sheets file as CSV and download it to the local system."""
    
    drive = GoogleDriveAPI()
    # Find the Google Sheets file on Drive by its name 'tracking' (not 'tracking.csv')
    file_id, mime_type = drive.find_file(file_name)  # Search for 'tracking' here

    if file_id and mime_type == 'application/vnd.google-apps.spreadsheet':
        # If the file is a Google Sheets file, export it as a CSV
        drive.convert_google_sheets_to_csv(file_id, csv_file)
    else:
        print("File is not a Google Sheets document or not found.")

#drive_api = GoogleDriveAPI()