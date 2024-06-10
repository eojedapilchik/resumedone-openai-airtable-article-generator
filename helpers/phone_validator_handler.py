import requests
from requests.exceptions import HTTPError


class PhoneValidatorHandler:
    def __init__(self, token, base_url='https://phone-validator-api.p.rapidapi.com'):
        self.base_url = base_url
        self.headers = {
            'x-rapidapi-host': 'phone-validator-api.p.rapidapi.com',
            'x-rapidapi-key': token,
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        try:
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except Exception as e:
            print(f"PhoneValidator API Error: {e}", response)
            return {
                'status': 'error',
                'status_code': response.status_code,
                'error_message': str(e)
            }


    def get_all_metadata(self, phone_number):
        endpoint = f"/metadata?phone={phone_number}"
        return self._request('GET', endpoint)

