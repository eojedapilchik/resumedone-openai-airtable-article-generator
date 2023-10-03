from pydantic import BaseModel
from typing import Optional, Dict


class Lead(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    personalization: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    custom_variables: Optional[Dict] = {"sequence_reply": 0}
