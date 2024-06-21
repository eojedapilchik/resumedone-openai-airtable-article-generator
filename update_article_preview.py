import json
import os

from helpers.airtable_handler import AirtableHandler
from helpers.webflow_handler import CollectionWbflHandler, EnglishCollectionWbflHandler, update_article_log
from models.article import Article

data_table = os.environ.get("TABLE_DATA")


class ArticlePreviewProcessor:
    def __init__(self):
        self.airtable_handler = AirtableHandler(data_table)

    def process_preview_update(self, record_id: str):
        article_detail = self.get_article(record_id)
        job_name = article_detail.get('Job Name')
        type_category = article_detail.get('Type Category')
        article = Article(record_id=record_id, job_name=job_name)
        try:
            wbf_params = article_detail.get('webflow parameters (from blog for webflow)')
            preview_data = article_detail.get('resume sample slider data')
            webflow_itm_id = article_detail.get('Webflow ID')
            blog = article_detail.get('blog') 
            del article_detail
            if webflow_itm_id is not None and preview_data is not None and wbf_params is not None:
                webflow_params = json.loads(sanitize_for_json(wbf_params[0] if len(wbf_params)>0 else ""))
                prevw_data = json.loads(sanitize_for_json(preview_data))
                wbfl_handler = CollectionWbflHandler(webflow_params=webflow_params, type_category=type_category)
                if blog == 'resume-example.com':
                    wbfl_handler = EnglishCollectionWbflHandler(webflow_params=webflow_params, type_category=type_category)
                wbfl_handler.update_preview(airtable_rec_id=article.record_id, wbfl_item_id=webflow_itm_id,
                                            data=prevw_data)
            else:
                update_article_log(airtable_handler=self.airtable_handler, record_id=article.record_id,
                               msg=f"Icompleted data (Please check: webflowId, preview data, webflow params)")
                return
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            update_article_log(airtable_handler=self.airtable_handler, record_id=article.record_id,
                               msg=f"Unexpected error: {str(e)}")
            return

    def get_article(self, record_id: str):
        found_article = self.airtable_handler.get_records(filter_by_formula=f"FIND(\"{record_id}\", {{Airtable ID}})")
        if not found_article or found_article[0] is None:
            print("No article found")
            return None
        return found_article[0].get("fields") or None


def sanitize_for_json(input_str: str) -> str:
    replacements = {
        '\n': ' ',  
    }

    for char, replacement in replacements.items():
        input_str = input_str.replace(char, replacement)

    return input_str
