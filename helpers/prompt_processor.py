import os
from typing import List, Dict
from models.article import Article
from models.prompt_command_factory import PromptCommandFactory
class ProcessPrompts:
    def __init__(self, openai_handler, record_id):
        self.openai_handler = openai_handler
        self.record_id = record_id
        self.metadata = {"meta title": "", "meta description": ""}
        self.images_url = []
        self.log_text = ""
        self.retries = int(os.getenv("OPENAI_RETRIES", 3))

    def process(self, prompts: List[Dict], article: Article) -> List[Dict]:
        for index, prompt in enumerate(prompts, start=1):
            prompt_type = prompt.get("type", "").lower().strip()
            command = PromptCommandFactory.create_command(prompt_type)
            response = command.execute(prompt, self.retries, article=article)
            prompt["response"] = response
            if self.metadata and index == 2:
                self.update_metadata(self.record_id, self.metadata)
        return prompts

    def update_metadata(self, record_id, metadata):
        # Implement the logic to update metadata here
        pass