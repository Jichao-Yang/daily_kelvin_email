import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import to and from email accounts
assert os.path.exists('./secrets/accounts.py')
from secrets.accounts import *
from tools import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_credentials(token_path='./secrets/token.json', creds_path='./secrets/credentials.json'):
    '''
    Create OAuth2 credentials from token or credentials json file
    Returns google.oauth2.credentials.Credentials object
    '''
    creds = None
    # token stores authentication info automatically after first log in
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def send(creds):
    '''
    Create and insert a draft email.
    Print the returned draft's message and id.
    Inputs:
        creds: google.oauth2.credentials.Credentials object from get_credentials
        content: string of the email message
    '''
    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)

        # encoded message
        message = compile()
        message['From'] = from_addr
        message['To'] = to_addr
        # ensure encoding method
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {'raw': encoded_message}
        send_message = service.users().messages().send(userId='me', body=create_message).execute()

    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message

creds = get_credentials()
send(creds)