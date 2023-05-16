import os
from dotenv import load_dotenv
from pyairtable import Table

load_dotenv()


class AirtableHandler:
    def __init__(self, table_id: str, base_key: str = None, personal_access_token: str = None):
        if personal_access_token is None:
            personal_access_token = os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN")
        if base_key is None:
            base_key = os.environ.get("BASE_ID")
        if not personal_access_token:
            raise ValueError("Personal Access Token not provided or found in environment variables")
        if table_id is None:
            raise ValueError("Table name not provided")
        self._personal_access_token = personal_access_token
        self._base_key = base_key
        self._table = Table(personal_access_token, base_key, table_id)

    @property
    def base_key(self):
        return self._base_key

    @property
    def personal_access_token(self):
        return self._personal_access_token

    @property
    def table(self):
        return self._table

    def get_records(self, table_name: str = None, filter_by_formula: str = None):
        if table_name:
            temp_table = Table(self._personal_access_token, self._base_key, table_name)
            return temp_table.all()
        return self._table.all()

    def update_record(self, record_id: str, fields: dict, table_name: str = None):
        update_table = self._table
        if table_name:
            update_table = Table(self._personal_access_token, self._base_key, table_name)
        try:
            update_table.update(record_id, fields)
        except Exception as e:
            print(e)
            raise e
