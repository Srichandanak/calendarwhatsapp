import os
import requests
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_upcoming_events():
    """Fetch events within the next 30 minutes from Google Calendar"""
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"
    in_30_mins = (datetime.utcnow() + timedelta(minutes=30)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=in_30_mins,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])

def send_whatsapp_message(message):
    """Send message via WhatsApp Cloud API"""
    url = f"https://graph.facebook.com/v17.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": os.getenv("MY_WHATSAPP_NUMBER"),
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code, response.text)

def main():
    events = get_upcoming_events()
    if not events:
        print("✅ No events in next 30 mins")
        return

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_time = datetime.fromisoformat(start).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        message = f"📅 Reminder: {event['summary']} at {event_time}"
        send_whatsapp_message(message)

if __name__ == "__main__":
    main()
