import requests
import os


class LemlistHandler:
    def __init__(self, api_key):
        self.base_url = "https://api.lemlist.com/api"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if api_key is None:
            api_key = os.getenv("LEMLIST_API_KEY")
            if api_key is None:
                raise ValueError("Lemlist API Key not provided or found in environment variables")
        self.api_key = api_key

    def list_campaigns(self):
        """Lists all campaigns in Lemlist."""
        response = requests.get(f"{self.base_url}/campaigns", auth=("", self.api_key), headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def create_webhook_for_campaign(self, campaign_id, webhook_url, event):
        """Creates a webhook for a specific campaign."""
        data = {
            "campaignId": campaign_id,
            "targetUrl": webhook_url,
            "type": event
        }
        response = requests.post(f"{self.base_url}/hooks", json=data, auth=("", self.api_key), headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def get_campaign_by_id(self, campaign_id):
        """Retrieve a specific campaign by its ID."""
        response = requests.get(f"{self.base_url}/campaigns/{campaign_id}", auth=("", self.api_key), headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def add_contact_to_campaign(self, campaign_id, contact_data):
        """Add a contact/lead to a specific campaign."""
        print(contact_data)
        endpoint = f"{self.base_url}/campaigns/{campaign_id}/leads/{contact_data['email']}"
        response = requests.post(endpoint, json=contact_data, auth=("", self.api_key), headers=self.headers)

        if 200 <= response.status_code < 300:
            return response.json()
        raise Exception(f"Error {response.status_code}: {response.text}")



# Example usage:
if __name__ == "__main__":
    lemlist_api_key = "7d36c29ebd1135a65a23a3f75b0c13b9"

    handler = LemlistHandler(lemlist_api_key)

    # List all campaigns
    campaigns = handler.list_campaigns()
    print(campaigns)

    campaign = handler.get_campaign_by_id("cam_6PTMPY9faawMa887R")
    print(campaign)

    try:
        webhook_response = handler.create_webhook_for_campaign("cam_6PTMPY9faawMa887R",
                                                               "https://81b6-81-202-12-69.ngrok-free.app/lemlist"
                                                               "/emailsFailed",
                                                               "emailsFailed")
        print(webhook_response)
    except Exception as e:
        if e.response.status_code == 409:
            print("Webhook already exists")
        print(e)

