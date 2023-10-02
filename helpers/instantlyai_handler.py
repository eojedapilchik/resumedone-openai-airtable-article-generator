from dotenv import load_dotenv
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

    def add_contact_to_campaign(self, campaign_id, contact_data):
        """Add a contact/lead to a specific campaign."""
        print(contact_data)
        endpoint = f"{self.base_url}/lead/add"
        response = requests.post(endpoint, data=contact_data, auth=("", self.api_key), headers=self.headers)

        if 200 <= response.status_code < 300:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")


# Example usage:
if __name__ == "__main__":
    instantly_api_key = os.getenv('INSTANTLY_API_KEY')

    handler = InstantlyHandler(instantly_api_key)

    # List all campaigns
    campaigns = handler.list_campaigns()
    print(campaigns)
