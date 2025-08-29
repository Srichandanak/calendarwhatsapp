from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    """Fetch today's events from Google Calendar."""
    creds = None
    # Load saved credentials if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Connect to Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    print("Fetching today's events...")

    # Start and end of today (UTC)
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    today_end = datetime.datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

    # Query calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=today_start,
        timeMax=today_end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print('No events found for today.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

if __name__ == '__main__':
    main()
