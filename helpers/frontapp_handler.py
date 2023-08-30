import requests


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
        response.raise_for_status()
        return response.json()

    def get_conversation(self, conversation_id):
        endpoint = f"/conversations/{conversation_id}"
        return self._request('GET', endpoint)

    def create_comment(self, conversation_id, comment_body):
        endpoint = f"/conversations/{conversation_id}/comments"
        data = {
            'body': comment_body
        }
        return self._request('POST', endpoint, data)
