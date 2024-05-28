from pydantic import BaseModel
from typing import Optional

class Experience(BaseModel):
    experience_content: str
    job_role: str
    company_name: str