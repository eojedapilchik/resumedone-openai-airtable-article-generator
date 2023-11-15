from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    job_name: str
    record_id: str
    language: Optional[str] = None
    base_id: Optional[str] = None
    image_urls: Optional[str] = None
    internal_refs: Optional[str] = None