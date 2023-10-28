from abc import ABC, abstractmethod
from typing import Dict, Optional
from models.article import Article
from helpers.openai_handler import OpenAIHandler
from helpers.html_utils import (add_p_tags, convert_bullets_to_html,
                                convert_numbers_to_ol, remove_double_quotes, remove_empty_html_tags)

class PromptCommand(ABC):
    @abstractmethod
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        openai_handler = openai_handler or OpenAIHandler()
        if openai_handler is None:
            raise ValueError("openai_handler cannot be None")
        prompt_text = prompt.get("prompt")
        if prompt_text is not None or prompt_text != "":
            prompt["response"] = openai_handler.prompt(prompt.get("prompt"))

class MetaDataPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        prompt["response"] = "" #remove this line after implementing the logic
        #TODO: update the record in Airtable with the metadata

class ImagePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article, **kwargs) -> None:
        image_urls_csv = article.get("image_urls", "")
        images_urls_list = image_urls_csv.split(",") if image_urls_csv else []
        image_url = images_urls_list.pop(0) if len(images_urls_list) > 0 else ""
        if image_url:
            prompt["response"] = f'<img src="{image_url}"/>'


class ExamplePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)


class DefaultPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        # Processing logic for image prompts
        super().execute(prompt, retries, article, openai_handler, **kwargs)




