from typing import List, Optional
from pydantic import BaseModel
from models.instantly_lead import Lead


class LeadsToCampaignPayload(BaseModel):
    campaign_id: str
    skip_if_in_workspace: Optional[bool] = False
    leads: List[Lead]
