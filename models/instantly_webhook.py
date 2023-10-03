from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional
from datetime import datetime


class InstantlyWebhookData(BaseModel):
    timestamp: datetime
    event_type: str
    workspace: UUID4
    campaign_id: UUID4
    unibox_url: Optional[HttpUrl] = None
    campaign_name: str
    step: int
    email_account: str
    reply_text_snippet: str
    is_first: Optional[bool] = False
    lead_email: str
    email: str
    firstName: Optional[str] = None
    reply_subject: Optional[str] = None
    reply_text: str
    reply_html: str
