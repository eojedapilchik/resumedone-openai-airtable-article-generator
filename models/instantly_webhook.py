from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class InstantlyWebhookData(BaseModel):
    timestamp: datetime
    event_type: str
    workspace: str
    campaign_id: str
    unibox_url: Optional[HttpUrl] = None
    campaign_name: str = None
    step: int = 0
    email_account: str
    reply_text_snippet: str = None
    is_first: Optional[bool] = False
    lead_email: str
    email: str
    firstName: Optional[str] = None
    reply_subject: Optional[str] = None
    reply_text: str
    reply_html: str
