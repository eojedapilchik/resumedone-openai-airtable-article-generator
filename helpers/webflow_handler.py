import json
from dotenv import load_dotenv
from helpers.airtable_handler import AirtableHandler
import requests
import os

load_dotenv()

data_table = os.environ.get("TABLE_DATA")
RESUME_TYPES = ['Resume Example', 'Entry Level', 'Resume in Language', 'Resume Country', 'Resume Country Multilanguage']
COVER_LETTER_TYPES = ['Cover Letter', 'Cover Letter in Language']


class WebflowHandler:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.webflow.com/v2"
        if api_key is None:
            api_key = os.getenv("WEBFLOW_API_KEY")
            if api_key is None:
                raise ValueError("Webflow API Key not provided or found in environment variables")
        self.headers = {"Accept": "application/json", "authorization": f"Bearer {api_key}",
                        'content-type': 'application/json'}

    def list_collection_items(self, collection_id, cms_local_id: str = None, offset: int = None, limit: int = None):
        """Lists all item in a collection"""
        params = ""
        if cms_local_id or offset or limit:
            params = "?"
            if cms_local_id:
                params = f"{params}cmsLocaleId={cms_local_id}"
            if offset:
                separator = "&" if "cmsLocaleId" in params else ""
                params = f"{params}{separator}"
                params = f"{params}offset={offset}"
            if limit:
                separator = "&" if "cmsLocaleId" in params or "offset" in params else ""
                params = f"{params}{separator}"
                params = f"{params}limit={limit}"
        fetch_url = f"{self.base_url}/collections/{collection_id}/items{params}"
        print(f"Fetching: {fetch_url}")
        response = requests.get(fetch_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")

    def update_item(self, collection_id, item_id: str, field_data: json, is_draft: bool = False,
                    is_archived: bool = False):
        """Update an item"""
        fetch_url = f"{self.base_url}/collections/{collection_id}/items/{item_id}"
        data = {
            "isArchived": is_archived,
            "isDraft": is_draft,
            "fieldData": field_data
        }

        response = requests.patch(fetch_url, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")

    def publish_item(self, collection_id, item_ids: list):
        """Publish item"""
        data = {
            "itemIds": item_ids
        }
        url = f"{self.base_url}/collections/{collection_id}/items/publish"
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 202:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")


class CollectionWbflHandler(WebflowHandler):
    def __init__(self, webflow_params: json, type_category: str, api_key: str = None):
        super().__init__(api_key)
        self.collection_detail = {}
        self.key_id_name = 'resumeId'
        self.key_is_additional_name = 'isAdditionalResume'
        if type_category in RESUME_TYPES:
            self.collection_detail = webflow_params.get('resume_article_params')
        elif type_category in COVER_LETTER_TYPES:
            self.collection_detail = webflow_params.get('cover_letter_params')
            self.key_id_name = 'coverLetterId'
            self.key_is_additional_name = 'isAdditionalCoverLetter'
        self.type_category = type_category
        self.airtable_handler = AirtableHandler(data_table)

    def update_preview(self, airtable_rec_id: str, wbfl_item_id: str, data: list):
        data_template_key = self.restructure_previews_data(data)
        preview_keys = self.get_wbfl_field_data_params(data_template_key)
        field_data = {}
        for key, value in preview_keys.items():
            new_key = self.collection_detail.get(key) or key
            field_data[new_key] = value

        self.update_then_publish_item(airtable_rec_id, field_data, wbfl_item_id)

    def get_wbfl_field_data_params(self, data_template_key):
        if self.type_category in RESUME_TYPES:
            return {
                "template-image": data_template_key['budapest']['url'],
                "show-popup": True,
                "budapest-id": data_template_key['budapest'][self.key_id_name],
                "budapest-thumbnail-image": data_template_key['budapest']['thumbnail_url'],
                "perth-id": data_template_key['perth'][self.key_id_name],
                "perth-thumbnail-image": data_template_key['perth']['thumbnail_url'],
                "rotterdam-id": data_template_key['rotterdam'][self.key_id_name],
                "rotterdam-thumbnail-image": data_template_key['rotterdam']['thumbnail_url'],
                "chicago-id": data_template_key['chicago'][self.key_id_name],
                "chicago-thumbnail-image": data_template_key['chicago']['thumbnail_url']
            }
        elif self.type_category in COVER_LETTER_TYPES:
            return {
                "template-image": data_template_key['budapest']['url'],
                "show-popup": True,
                "budapest-id": data_template_key['budapest'][self.key_id_name],
                "budapest-thumbnail-image": data_template_key['budapest']['thumbnail_url'],
                "perth-id": data_template_key['perth'][self.key_id_name],
                "perth-thumbnail-image": data_template_key['perth']['thumbnail_url'],
                "kiev-id": data_template_key['kiev'][self.key_id_name],
                "kiev-thumbnail-image": data_template_key['kiev']['thumbnail_url'],
                "montecarlo-id": data_template_key['montecarlo'][self.key_id_name],
                "montecarlo-thumbnail-image": data_template_key['montecarlo']['thumbnail_url']
            }
        return {}

    def restructure_previews_data(self, data) -> json:
        template_json = {}
        for preview_item in data:
            preview_item_id = preview_item[self.key_id_name]
            template = preview_item.get('template')
            if template == 'budapest' and preview_item[self.key_is_additional_name]:
                template = 'budapest_1'

            template_json[template] = {
                'thumbnail_url': preview_item.get('thumbnail_url'),
                'url': preview_item.get('url'),
                'title': preview_item.get('title'),
            }
            template_json[template][self.key_id_name] = preview_item_id
        return template_json

    def update_then_publish_item(self, airtable_rec_id, field_data, wbfl_item_id):
        try:
            self.update_item(collection_id=self.collection_detail.get('collection_id'), item_id=wbfl_item_id,
                             field_data=field_data)
            self.publish_item(collection_id=self.collection_detail.get('collection_id'), item_ids=[wbfl_item_id])
            mark_article_preview_updated(airtable_handler=self.airtable_handler, record_id=airtable_rec_id)
        except Exception as e:
            update_article_log(airtable_handler=self.airtable_handler, record_id=airtable_rec_id, msg=str(e))
            print(f"Update and publish failed: {str(e)}")


def mark_article_preview_updated(airtable_handler: AirtableHandler, record_id: str):
    try:
        fields = {
            "fldkrvYybPj3hMYTP": "Html",
        }
        airtable_handler.update_record(record_id, fields)
    except Exception as e:
        print(f"[!!] Error updating Airtable preview status for record: {str(e)}")


def update_article_log(airtable_handler: AirtableHandler, record_id: str, msg: str):
    try:
        fields = {
            "fldnEZ9uHN8mNJPA8": msg,
        }
        airtable_handler.update_record(record_id, fields)
    except Exception as e:
        print(f"[!!] Error updating Airtable log for record: {str(e)}")
