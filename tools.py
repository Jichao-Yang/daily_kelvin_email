import os.path
import base64
import time
from pywttr import Wttr
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import to and from email accounts
assert os.path.exists('./secrets/info.py')
from secrets.info import *

def forecast(city='Chicago'):
    wttr = Wttr(city)
    # Prevent HTTP timeout
    while True:
        try:
            forecast = wttr.en().weather[0]
            break
        except:
            print('Trying again...')
            time.sleep(10)
            continue

    # In normal units (celcius and kmh)
    high = int(forecast.maxtemp_c)
    low = int(forecast.mintemp_c)
    hourly_windspeed = []
    for hourly_item in forecast.hourly:
        hourly_windspeed.append(float(hourly_item.windspeed_kmph))
    windspeed = sum(hourly_windspeed)/len(hourly_windspeed)
    # Switch from Celcius to Kelvin
    high = int(high + 273.15)
    low = int(low + 273.15)
    # Switch from kmh to multiples of lightspeed
    windspeed = int(windspeed * 10e9/1079252848.7999)

    return high, low, windspeed

def write():
    subject = 'Your Daily Kelvin Forecast'
    with open('message_body.txt', 'r', encoding='utf-8') as f:
        content = ''.join(f.readlines())

    content = content.format(*forecast())

    return subject, content

def compile():
    message = EmailMessage()
    subject, content = write()
    message.set_content(content)
    message['Subject'] = subject

    return message

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

def send(creds, to_addr):
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

if __name__ == '__main__':
    creds = get_credentials()
    for to_addr in debug_email_list:
        send(creds, to_addr)