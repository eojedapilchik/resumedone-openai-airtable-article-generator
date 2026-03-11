from typing import List, Optional
from pydantic import BaseModel


class ArticleItem(BaseModel):
    id: str
    title: str
    content_markdown: Optional[str] = ""
    content_html: Optional[str] = ""
    meta_description: Optional[str] = ""
    created_at: Optional[str] = ""
    image_url: Optional[str] = ""
    slug: Optional[str] = ""
    tags: Optional[List[str]] = []


class PublishArticlesData(BaseModel):
    articles: List[ArticleItem]


class PublishArticlesWebhook(BaseModel):
    event_type: str
    timestamp: Optional[str] = ""
    data: PublishArticlesData
