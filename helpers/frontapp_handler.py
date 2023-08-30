import requests
from requests.exceptions import HTTPError


class FrontAppError(Exception):
    """Custom exception for FrontApp specific errors."""

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code
        try:
            self.frontapp_error = response.json().get('message', '')
        except ValueError:
            self.frontapp_error = ""
        print(f"FrontAppError encountered!")
        print(f"Message: {message}")
        print(f"HTTP Status Code: {self.status_code}")
        if self.frontapp_error:
            print(f"FrontApp-specific Error Message: {self.frontapp_error}")


class FrontAppHandler:
    def __init__(self, token, base_url='https://api2.frontapp.com'):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise FrontAppError(f"FrontApp API Error: {e}", response)

        return response

    def update_conversation(self, conversation_id, data):
        endpoint = f"/conversations/{conversation_id}"
        return self._request('PATCH', endpoint, data)

    def create_comment(self, conversation_id, comment_body):
        endpoint = f"/conversations/{conversation_id}/comments"
        data = {
            'body': comment_body
        }
        return self._request('POST', endpoint, data)

    def create_draft(self, conversation_id, draft_body, options=None):
        """Create a draft for a given conversation."""
        if options is None:
            options = {}

        endpoint = f"/conversations/{conversation_id}/drafts"
        data = {
            'body': draft_body,
            **options
        }
        return self._request('POST', endpoint, data)
