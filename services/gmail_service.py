import base64
from datetime import UTC, datetime
from email.message import EmailMessage as MIMEEmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = Path(".gmail_token.json")


class GmailError(RuntimeError):
    pass


class GmailService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self) -> Credentials:
        if not self.client_id or not self.client_secret:
            raise GmailError("Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env first.")
        credentials = None
        if TOKEN_FILE.exists():
            credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            config = {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(config, SCOPES)
            credentials = flow.run_local_server(port=0, open_browser=True)
            TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
        return credentials

    def send(self, recipient: str, subject: str, body: str) -> tuple[str, datetime]:
        credentials = self.authenticate()
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        message = MIMEEmailMessage()
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        response = service.users().messages().send(userId="me", body={"raw": encoded}).execute()
        return response["id"], datetime.now(UTC)

