import base64
import pickle
import os.path
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from feedme.emailclients.clientbase import EmailClient


class GoogleClient(EmailClient):

    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

    def __init__(self, credentials_path):
        credentials = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        self.service = build('gmail', 'v1', credentials=credentials, cache_discovery=False)

    def create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text, "html")
        message['subject'] = subject
        message['from'] = sender
        message['to'] = to
        return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, message):
        return self.service.users().messages().send(userId="me", body=message).execute()
