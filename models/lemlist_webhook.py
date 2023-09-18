from pydantic import BaseModel, EmailStr


class WebhookData(BaseModel):
    sendUserEmail: EmailStr
    subject: str = None
    campaignName: str = None
    leadId: str
    campaignId: str
    text: str
    leadEmail: EmailStr
    emailId: str
    messageId: str
    isFirst: bool = True
    sequenceId: str = None
    emailTemplateId: str = None
    sendUserId: str = None
    type: str
