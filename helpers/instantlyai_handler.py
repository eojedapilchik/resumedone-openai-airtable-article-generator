import json
from dotenv import load_dotenv
from typing import List
from models.instantly_lead import Lead
import requests
import os

load_dotenv()


class InstantlyHandler:
    def __init__(self, api_key):
        self.base_url = "https://api.instantly.ai/api/v1"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if api_key is None:
            api_key = os.getenv("660gh4qzwgme87nxjbe07ce1hqmq")
            if api_key is None:
                raise ValueError("Lemlist API Key not provided or found in environment variables")
        self.api_key = api_key

    def list_campaigns(self):
        """Lists all campaigns in Lemlist."""
        response = requests.get(f"{self.base_url}/campaign/list?api_key={self.api_key}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def add_leads_to_campaign(self, campaign_id: str, leads: List[Lead]):
        """Add a leads to a specific campaign."""
        payload = json.dumps({
            "api_key": self.api_key,
            "campaign_id": campaign_id,
            "skip_if_in_workspace": False,
            "leads": [lead.model_dump(exclude_none=True) for lead in leads]
        })
        endpoint = f"{self.base_url}/lead/add"
        response = requests.post(endpoint, data=payload, headers=self.headers)
        if 200 <= response.status_code < 300:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")

    def get_leads_from_campaign(self, campaign_id: str, email: str):
        """Get leads from a specific campaign."""
        response = requests.get(
            f"{self.base_url}/lead/get?api_key={self.api_key}&campaign_id={campaign_id}&email={email}",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def update_leads_sequence_reply(self, campaign_id: str, email: str, value: int):
        """Update leads custom variables from a specific campaign."""
        data = {
            "api_key": self.api_key,
            "campaign_id": campaign_id,
            "email": email,
            "variables": {
                "sequence_reply": value
            }
        }
        try:
            response = requests.post(
                f"{self.base_url}/lead/data/update",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
        except requests.HTTPError:
            # If the update fails, try the set operation
            response = requests.post(
                f"{self.base_url}/lead/data/set",  # Assuming this is the endpoint for the set operation
                json=data,
                headers=self.headers
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()


# Example usage:
if __name__ == "__main__":
    instantly_api_key = os.getenv('INSTANTLY_API_KEY')

    handler = InstantlyHandler(instantly_api_key)

    # List all campaigns
    campaigns = handler.list_campaigns()
    print(campaigns)
    lead = handler.get_leads_from_campaign('4f128968-5d88-404e-b261-7407c439a1a3', 'eojedapilchik@gmail.com')
    print(lead)
    handler.update_leads_sequence_reply('4f128968-5d88-404e-b261-7407c439a1a3', 'vijay@resumedone.io', 1)

