from __future__ import print_function
import os.path
import os
import base64
from bs4 import BeautifulSoup
import re
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from datetime import datetime, timedelta


class GoogleEmailService:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    _sender = os.getenv("GMAIL_SENDER")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(
        script_dir
    )

    def __init__(self, account_name):
        self.sender = os.getenv(f"GMAIL_SENDER_{account_name.upper()}")
        self.account_name = account_name
        self.service = self.authenticate_google_account()

    def authenticate_google_account(self):
        creds = None
        folder_path = self.parent_dir
        print(f"folder_path: {folder_path}")
        token_path = f"{folder_path}/token_{self.account_name}.json"

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print(f"authenticate_google_account for {self.account_name}: No valid credentials found.")
                credentials_path = f"{folder_path}/credentials_{self.account_name}.json"
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                print(
                    f"A new window to authorize app for {self.account_name} is required. Please check your browser."
                )

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        try:
            service = build("gmail", "v1", credentials=creds)
            print(f"Gmail service authenticated successfully for {self.account_name}.")
        except HttpError as error:
            service = None
            print(f"An error occurred trying gmail service for {self.account_name}: {error}")
        return service

    def send_email(self, to, subject, message_text, cc=None):
        if not message_text or not to or not subject:
            raise ValueError("Cannot send email without message, to, and subject")
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        message = self.create_message(to, cc, subject, message_text)
        message_sent = (
            self.service.users().messages().send(userId="me", body=message).execute()
        )
        message_sent["date"] = current_date
        return message_sent

    def create_message(self, to, cc, subject, message_text):
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = self.sender
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        return {"raw": base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def list_messages_with_subject(self, user_id, subject):
        try:
            response = (
                self.service.users()
                .messages()
                .list(userId=user_id, q=subject)
                .execute()
            )
            messages = []
            if "messages" in response:
                messages.extend(response["messages"])

            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = (
                    self.service.users()
                    .messages()
                    .list(userId=user_id, q=subject, pageToken=page_token)
                    .execute()
                )
                messages.extend(response["messages"])

            return messages
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_message(self, user_id, msg_id):
        try:
            message = (
                self.service.users().messages().get(userId=user_id, id=msg_id).execute()
            )
            print(f'Message snippet: {message["snippet"]}')

            return message
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_last_otp(self, limit=3, text=""):
        """Retrieves recent emails using the Gmail API"""

        if not text:
            text = "Your account verification passcode is :"
        subject = os.getenv("", "Collective Medical Account Verification Passcode")
        result = (
            self.service.users()
            .messages()
            .list(userId="me", q=subject, maxResults=limit)
            .execute()
        )
        messages = result.get("messages")

        for msg in messages:
            txt = (
                self.service.users().messages().get(userId="me", id=msg["id"]).execute()
            )
            try:
                snippet = txt["snippet"]
                payload = txt["payload"]
                # parts = payload['parts']
                # data = payload['body']['data']
                # data = data.replace("-", "+").replace("_", "/")
                # decoded_data = base64.b64decode(data).decode('utf-8')
                # soup = BeautifulSoup(decoded_data, "lxml")
                # body = soup.body()
                if text in snippet:
                    pattern = r": ([A-Z]{5,})"
                    match = re.search(pattern, snippet)
                    if match:
                        otp = match.group(1)
                        print(f"Found the OTP: {otp}")
                        return otp
            except BaseException as error:
                print("An error occurred: ", str(error))

        print(f"An OTP email was not found within the last {limit} emails")

    def get_thread(self, user_id, thread_id):
        try:
            thread = self.service.users().threads().get(userId=user_id, id=thread_id).execute()
            messages = thread['messages']
            # print(f'Thread ID: {thread["id"]}')
            # print(f'Number of messages in this thread: {len(messages)}')
            # print(f'Snippet of the last message: {messages[-1]["snippet"]}')

            # The original email is the first email in the thread
            original_email = messages[0]
            # print(f'Original email Subject: {original_email["payload"]["headers"]}')
            # print(f'Original email Subject: {original_email["id"]}')
            return thread
        except HttpError as error:
            print(f'An error occurred: {error}')

    def check_if_reply(self, user_id, msg_id):
        message = self.get_message(user_id, msg_id)
        thread_id = message['threadId']

        if thread_id:
            thread = self.get_thread(user_id, thread_id)
            # If the thread has more than one email, the message is a reply
            if len(thread['messages']) > 1:
                print(f'Message {msg_id} is a reply.')
                return True
            else:
                print(f'Message {msg_id} is not a reply.')
                return False
        else:
            print(f'Message {msg_id} is not a reply.')
            return False

    def list_threads_last_24_hours(self, user_id):
        try:

            # Calculate the timestamp for 24 hours ago
            after = datetime.now() - timedelta(hours=24)
            after = int(after.timestamp())

            # Query all threads from the last 24 hours
            response = self.service.users().threads().list(userId=user_id,
                                                           q=f'after:{after}').execute()

            threads = []
            if 'threads' in response:
                threads.extend(response['threads'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().threads().list(userId=user_id,
                                                               q=f'after:{after}',
                                                               pageToken=page_token).execute()
                threads.extend(response['threads'])

            return threads
        except HttpError as error:
            print(f'An error occurred: {error}')

    def get_threads_with_replies(self, user_id="me"):
        threads = self.list_threads_last_24_hours(user_id)
        threads_replied = []
        skipped = 0
        for thread in threads:
            thread_data = self.get_thread(user_id, thread['id'])
            messages = thread_data['messages']
            # print(f'Number of messages in this thread: {len(messages)}')
            if len(messages) >= 2:
                found_reply = False
                for msg in messages:
                    message = self.get_message(user_id, msg['id'])
                    for header in message['payload']['headers']:
                        if header['name'] == 'From' and 'mailer-daemon@googlemail.com' in header['value']:
                            print(f"Skipping a bounce notification.")
                            skipped += 1
                            found_reply = True
                            break
                        if header['name'] == 'In-Reply-To':
                            # print(f'\n ** This email is a reply to: {header["value"]}\n')
                            threads_replied.append(thread['id'])
                            found_reply = True
                            break
                            # print(f'\n ** This email is a reply to: {header["value"]}\n')
                    if found_reply:
                        break
        print(f'Number of threads replied: {len(threads_replied)}')
        print(f'Number of threads skipped: {skipped} - bounced emails')
        return threads_replied

    def watch_inbox(self, user_id="me", topic_name="projects/lead-automation-397419/topics/InboxMessages"):
        try:
            response = self.service.users().watch(userId=user_id,
                                                  body={
                                                      'labelIds': ['INBOX'],
                                                      'topicName': topic_name,
                                                      'labelFilterAction': 'include'
                                                  }).execute()
            print(response)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def stop_watching_inbox(self, user_id="me"):
        try:
            response = self.service.users().stop(userId=user_id).execute()
            print(response)
        except HttpError as error:
            print(f'An error occurred: {error}')


if __name__ == "__main__":
    service = GoogleEmailService("alcides")
    service.stop_watching_inbox()