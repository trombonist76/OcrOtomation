from __future__ import print_function
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
import io
import otomation

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main(download=False, file_id= None, download_path=None, file_name=None, upload=False, file_path=None):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    #
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))

    if download:
        mime = "application/pdf"
        request = service.files().export_media(fileId=file_id, mimeType=mime)
        save_path_name = os.path.join(download_path,file_name)
        fh = io.FileIO(save_path_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    elif upload:
        mime = "image/jpeg"
        file_metadata = {"name": file_name, "mimeType": "application/vnd.google-apps.document"}
        media = MediaFileUpload(file_path, mimetype=mime)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id").execute()
        print("File id %s" % file.get("id"))

if __name__ == '__main__':
        # main(download=True,download_path=r"C:\Users\binbi\PycharmProjects\OcrOtomation\TextConvertedGdrive",file_id="1PEZ2T-58H6KCXF8h15RGAZbmc562Ciwfl9keLDa8pdo",file_name="9")
        # main()
        main(upload=True,file_path=r"C:\Users\binbi\PycharmProjects\OcrOtomation\Images\11.jpeg",file_name="15687")