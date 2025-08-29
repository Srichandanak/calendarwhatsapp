from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser   # for parsing Google datetime strings

# Scopes = permission we need (read-only access to Google Calendar)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# How many minutes before an event we want to be reminded
REMINDER_MINUTES = 30

def main():
    """Checks today's calendar events and prints reminders for upcoming ones."""
    creds = None
    
    # token.json stores the user’s access and refresh tokens, created automatically
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    print("🔍 Checking today's events...")

    # Start and end of today (UTC)
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    today_end = datetime.datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

    # Fetch today's events
    events_result = service.events().list(
        calendarId='primary',
        timeMin=today_start,
        timeMax=today_end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print("📭 No events scheduled for today.")
        return

    now = datetime.datetime.utcnow()

    for event in events:
        # Parse event start time
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        start = parser.parse(start_str)

        # Time difference in minutes
        diff = (start - now).total_seconds() / 60

        if 0 < diff <= REMINDER_MINUTES:
            print(f"⏰ Reminder: '{event['summary']}' starts in {int(diff)} minutes at {start}")
        else:
            print(f"➡️ Skipping: '{event['summary']}' (starts at {start})")

if __name__ == '__main__':
    main()
