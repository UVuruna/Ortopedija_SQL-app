import os
import pickle
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth import impersonated_credentials
from google.oauth2 import service_account
import io
from B_Decorators import Singleton
import json
import requests



class GoogleDrive_User(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            print(f"INITING {GoogleDrive_User}")
            self.SCOPES = [ 'https://www.googleapis.com/auth/drive',
                            'https://www.googleapis.com/auth/drive.file',
                            'https://www.googleapis.com/auth/admin.directory.user',
                            'https://www.googleapis.com/auth/userinfo.email',
                            'openid']
            self.creds = self.authenticate_google_drive()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            GoogleDrive_User._initialized = True

    def authenticate_google_drive(self):
        creds = None
        # Proverite da li postoji www_token.pickle fajl koji čuva korisničke kredencijale
        if os.path.exists('www_token.pickle'):
            with open('www_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # Ako nema kredencijala ili su nevažeći, korisnik mora da se autentifikuje
        if not creds or not creds.valid:
            print("Refreshing credentials...")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("Running authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file('www_credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Sačuvajte kredencijale za sledeću upotrebu
            with open('www_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def download_file(self, file_id, destination):
        request = self.drive_service.files().get_media(fileId=file_id)
        with open(destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

    def update_file(self, file_id, file_path, mime_type):
        media = MediaFileUpload(file_path, mimetype=mime_type)
        self.drive_service.files().update(fileId=file_id, media_body=media).execute()
        print('File ID: %s' % file_id)
        return file_id 

    def upload_file_fromPC(self, file_name, GoogleDrive_folder, file_path, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % file.get('id'))
        return file.get('id')

    def upload_blob_file(self, file_name, GoogleDrive_folder, blob_data, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaIoBaseUpload(io.BytesIO(blob_data), mimetype=mime_type)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % file.get('id'))
        return file.get('id')
    
    def get_file_info(self, file_id):
        file = self.drive_service.files().get(fileId=file_id, fields='name, size, mimeType').execute()
        return file

    def get_user_email(self):
        oauth2_service = build('oauth2', 'v2', credentials=self.creds)
        user_info = oauth2_service.userinfo().get().execute()
        return user_info.get('email')

    def add_test_user(self, user_email):
        service = build('iam', 'v1', credentials=self.creds)
        project_id = 'rhmh-sqlite'  # ID vašeg GCP projekta
        service_account_email = f'{project_id}@{project_id}.iam.gserviceaccount.com'
        resource = {
            'keyAlgorithm': 'KEY_ALG_RSA_2048',
            'privateKeyType': 'TYPE_GOOGLE_CREDENTIALS_FILE'
        }
        response = service.projects().serviceAccounts().keys().create(
            name=f'projects/{project_id}/serviceAccounts/{service_account_email}',
            body=resource
        ).execute()
        return response



if __name__ == '__main__':

    user = GoogleDrive_User()
    user_email = user.get_user_email()
    print(user_email)



