from pydantic import BaseModel
from typing import List, Optional, Union


class BlogCollection(BaseModel):
    collection_id: str 
    webflow_article_base_url: Optional[str] = None


class Blog(BaseModel):
    site_id: str
    blog_rec_id: str
    blog_name: str
    blog_to_webflow_id: str
    language_id: str
    entry_level_kws: List[str]
    resume_example_kws: List[str]
    cv_country_kws: List[str]
    cv_language_kws: List[str]
    job_search_kws: List[str]
    cl_language_kws: List[str]
    job_itw_kws: List[str]
    cover_letter_kws: List[str]
    cv_collection: Union[BlogCollection, None] = None
    cover_letter_collection: Union[BlogCollection, None] = None
    job_search_collection: Union[BlogCollection, None] = None

