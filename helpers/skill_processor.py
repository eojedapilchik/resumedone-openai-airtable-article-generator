import os
import datetime
from typing import List, Dict
from helpers.article_processor import ArticleProcessor
from models.article import Article
from models.prompt_command_factory import PromptCommandFactory
from helpers.openai_handler import OpenAIException


class SkillProcessor(ArticleProcessor):
    def update_airtable_record_log(self, record_id, new_status: str = 'Error'):
        self.update_field_record(record_id, new_status, "fldeoe8cq9zejuFmy")
            
    def update_airtable_record_status(self, record_id, new_status: str = 'Error'):
        self.update_field_record(record_id, new_status, "fld0oYUmBQvCw1doS")
            
    def update_field_record(self, record_id, new_status: str = 'Error', field_id: str = "fld0oYUmBQvCw1doS"):
        try:
            fields = {}
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
        # loop through prompts and extract responses
        plain_text_responses = [response["response"] for response in prompts]
        current_utc_time = datetime.datetime.utcnow()
        iso8601_date = current_utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        resultJson = plain_text_responses[0]

        try:
            fields = {
                "flds0W4E1JKU6Zqf8": resultJson,
                "fldDgbDaX1GdPMJBW": elapsed_time_bf_at,
                "fld0oYUmBQvCw1doS": "Completed",
                "flddfrffjq7yAkYAl": iso8601_date
            }
            self.airtable_handler.update_record(record_id, fields)
            print("[+] Airtable record updated successfully.")
        except Exception as e:
            print(f"[!!] Error updating record: {str(e)}")
            print(prompts)

