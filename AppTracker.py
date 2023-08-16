import os
import time
import psutil
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
service = build('calendar', 'v3', credentials=creds)

# Application you want to track
target_app_name = "GitHubDesktop.exe"  # Replace with the app name

def get_active_window_title():
    active_window = psutil.win32.get_active_window()
    return psutil.win32.get_process_module_filename(active_window[1])

def create_calendar_event(start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event['summary']}")

def main():
    prev_app = None
    start_time = None

    while True:
        active_app = get_active_window_title()

        if active_app.endswith(target_app_name):
            if prev_app != active_app:
                start_time = datetime.now()

            prev_app = active_app
        else:
            if prev_app and start_time:
                end_time = datetime.now()
                elapsed_time = end_time - start_time

                if elapsed_time > timedelta(seconds=60):  # Minimum time to log
                    event_summary = f"Time spent in {os.path.basename(prev_app)}: {elapsed_time}"
                    create_calendar_event(start_time.isoformat(), end_time.isoformat(), event_summary)

                prev_app = None
                start_time = None

        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    main()
