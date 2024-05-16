import datetime
from typing import List, Dict

from helpers.article_processor import ArticleProcessor


class SkillProcessor(ArticleProcessor):
    def __init__(self, openai_handler, record_id, airtable_handler, db: Dict):
        super().__init__(openai_handler, record_id, airtable_handler)
        self.log_field_id = db.get("logFieldId")
        self.status_field_id = db.get("statusFieldId")
        self.json_field_id = db.get("JSONFieldId")
        self.date_finished_field_id = db.get("finishedTimeFieldId")
        self.elapsed_time_field_id = db.get("elapsedTimeFieldId")

    def update_airtable_record_log(self, record_id, new_status: str = 'Error'):
        self.update_field_record(record_id, new_status, self.log_field_id)

    def update_airtable_record_status(self, record_id, new_status: str = 'Error'):
        self.update_field_record(record_id, new_status, self.status_field_id)

    def update_field_record(self, record_id, new_status: str = 'Error', field_id: str = "fld0oYUmBQvCw1doS"):
        fields = {}
        try:
            fields[field_id] = new_status
            self.airtable_handler.update_record(record_id, fields)
        except Exception as e:
            print(f"[!!] Error updating Airtable for record: {str(e)}")

    def update_airtable_record(self, record_id: str, prompts: List[Dict],
                               elapsed_time_bf_at: float = 0):
        print("[+] Updating Airtable record...")
        if len(prompts) <= 0:
            print("[-] Insufficient responses provided.")
            return None
        plain_text_responses = [response["response"] for response in prompts]
        current_utc_time = datetime.datetime.utcnow()
        iso8601_date = current_utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        result_json = plain_text_responses[0]

        fields = {}
        try:
            fields[self.json_field_id] = result_json
            fields[self.elapsed_time_field_id] = elapsed_time_bf_at
            fields[self.status_field_id] = "Completed"
            fields[self.date_finished_field_id] = iso8601_date

            self.airtable_handler.update_record(record_id, fields)
            print("[+] Airtable record updated successfully.")
        except Exception as e:
            print(f"[!!] Error updating record: {str(e)}")
            print(prompts)
