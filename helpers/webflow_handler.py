import json
from dotenv import load_dotenv
from typing import List, Union
from models.instantly_lead import Lead
import time
import requests
import os

load_dotenv()


class WebflowHandler:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.webflow.com/v2"
        if api_key is None:
            api_key = os.getenv("WEBFLOW_API_KEY")
            if api_key is None:
                raise ValueError("Webflow API Key not provided or found in environment variables")
        self.headers = {"Accept": "application/json", "authorization": f"Bearer {api_key}"}

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
        response.raise_for_status()
