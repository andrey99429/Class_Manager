import pytz
import pickle
import os.path
from datetime import datetime
from class_manager.settings import BASE_DIR, TIME_ZONE
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

utc = pytz.timezone('UTC')
tz = pytz.timezone(TIME_ZONE)


def local_now():
    dt = datetime.now()
    return dt.astimezone(tz)


class DriveManager:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    ROOT_FOLDER_ID = '1Dy9BBG_8Irg-oebpPEqcRsuUb_DirVQe'
    MARKS_SHEET_ID = ''
    __instance = None

    def __init__(self):
        if DriveManager.__instance is not None:
            raise ReferenceError('Trying to create singleton object twice!')
        else:
            DriveManager.__instance = self

        creds = None

        token_path = os.path.join(BASE_DIR, 'GoogleAPI/token.pickle')
        credentials_path = os.path.join(BASE_DIR, 'credentials.json')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server()

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.drive = build('drive', 'v3', credentials=creds)
        self.sheets = build('sheets', 'v4', credentials=creds)

    @staticmethod
    def get():
        if DriveManager.__instance is None:
            DriveManager()
        return DriveManager.__instance

    def list_files(self, folder_id):
        results = self.drive.files().list(
            fields='files(id, name, modifiedTime)',
            q="'{}' in parents".format(folder_id)
        ).execute()
        files = results.get('files', [])

        for file in files:
            dt = utc.localize(datetime.strptime(file['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ'))
            dt = dt.astimezone(tz)
            file['modifiedTime'] = dt

        return files

    def create_folder(self, folder_name, writers_gmail):
        result = self.drive.files().create(
            body={
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.ROOT_FOLDER_ID]
            },
            fields='id',
        ).execute()

        folder_id = result['id']

        self.add_writer(folder_id, writers_gmail)

        return folder_id

    def rename_folder(self, folder_id, folder_name):
        result = self.drive.files().update(
            body={
                'name': folder_name
            },
            fileId=folder_id
        ).execute()

    def add_writer(self, folder_id, writers_gmail):
        result = self.drive.permissions().create(
            fileId=folder_id,
            sendNotificationEmail=True,
            body={
                'emailAddress': writers_gmail,
                'type': 'user',
                'role': 'writer'
            }
        ).execute()

    def update_writer(self, folder_id, writers_gmail):
        result = self.drive.permissions().list(
            fileId=folder_id
        ).execute()

        id_to_delete = []

        for permission in result['permissions']:
            if permission['role'] == 'writer':
                id_to_delete.append(permission['id'])

        for permission_id in id_to_delete:
            result = self.drive.permission().delete(
                fileId=folder_id,
                permissionId=permission_id
            ).execute()

        self.add_writer(folder_id, writers_gmail)


if __name__ == '__main__':
    dm: DriveManager = DriveManager().get()


