import json
from dotenv import load_dotenv
from typing import List, Union
from models.instantly_lead import Lead
import time
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
        print(f"Adding {len(leads)} leads to campaign {campaign_id}...")
        start_time = time.time()
        response = requests.post(endpoint, data=payload, headers=self.headers)
        if 200 <= response.status_code < 300:
            print(f"Leads added successfully to campaign {campaign_id}.")
            print(f"Elapsed time: {time.time() - start_time} seconds.")
            return response.json()
        print(f"Elapsed time: {time.time() - start_time} seconds.")
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

    def update_leads_sequence_reply(self, campaign_id: str, email: str, sequence_reply: int):
        self.update_leads_variable(campaign_id, email, "sequence_reply", sequence_reply)

    def update_leads_variable(self, campaign_id: str, email: str, variable: str, value: Union[int, str, float]):
        """Update leads custom variables from a specific campaign."""
        data = {
            "api_key": self.api_key,
            "campaign_id": campaign_id,
            "email": email,
            "variables": {
                variable: value
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
    lead = handler.get_leads_from_campaign('1718d2c1-88ae-41c9-8006-b8928905e457', 'eojedapilchik@gmail.com')
    print(lead)
    handler.update_leads_sequence_reply('1718d2c1-88ae-41c9-8006-b8928905e457', 'eojedapilchik@gmail.com', 1)
