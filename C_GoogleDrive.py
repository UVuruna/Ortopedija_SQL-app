from A_Variables import *
from B_Decorators import Singleton,method_efficency,error_catcher

class GoogleDrive(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized: # moze self ovde
            GoogleDrive._initialized = True
            self.SCOPES = [ 'https://www.googleapis.com/auth/drive',
                            'https://www.googleapis.com/auth/drive.file',
                            'https://www.googleapis.com/auth/admin.directory.user',
                            'https://www.googleapis.com/auth/userinfo.email',
                            'openid']
            self.creds = self.authenticate_google_drive()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            GoogleDrive._initialized = True

            self.UserSession = {'User':self.get_UserEmail()}

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

    def download_File(self, file_id, destination):
        request = self.drive_service.files().get_media(fileId=file_id)
        with open(destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
    
    def download_BLOB(self, file_id):
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.getvalue()


    def upload_UpdateFile(self, file_id, file_path, mime_type):
        media = MediaFileUpload(file_path, mimetype=mime_type)
        self.drive_service.files().update(fileId=file_id, media_body=media).execute()    

    def upload_NewFile_asFile(self, file_name, GoogleDrive_folder, file_path, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def upload_NewFile_asBLOB(self, file_name, GoogleDrive_folder, blob_data, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaIoBaseUpload(io.BytesIO(blob_data), mimetype=mime_type)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    

    def get_UserEmail(self):
        oauth2_service = build('oauth2', 'v2', credentials=self.creds)
        user_info = oauth2_service.userinfo().get().execute()
        return user_info.get('email')
    
    def get_FileInfo(self, file_id):
        file = self.drive_service.files().get(fileId=file_id, fields='name, size, mimeType').execute()
        return file


if __name__ == '__main__':

    user = GoogleDrive()
    user_email = user.get_UserEmail()
    print(user_email)