import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from models.article import Article
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.html_utils import (add_p_tags, convert_bullets_to_html,
                                convert_numbers_to_ol, remove_double_quotes, remove_empty_html_tags)

class PromptCommand(ABC):
    @abstractmethod
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        openai_handler = openai_handler or OpenAIHandler()
        show_debug = os.environ.get("SHOW_DEBUG") == "True"
        if openai_handler is None:
            raise ValueError("openai_handler cannot be None")
        prompt_text = prompt.get("prompt")
        if prompt_text is not None or prompt_text != "":
            for i in range(retries):
                try:
                    prompt["response"] = openai_handler.prompt(prompt_text)
                    if show_debug:
                        prompt_info = f"\n[SECTION {prompt['position']}] \n {prompt['section']} \n[PROMPT] \n " \
                                      f"{prompt['prompt']}\n"
                        print(prompt_info + f"\n\n[RESPONSE] {prompt['response']}\n\n")
                    break
                except OpenAIException as e:
                    if i < retries - 1:  # i is zero indexed
                        time.sleep((2 ** i))  # exponential backoff, sleep for 2^i seconds
                        print(f"Retrying OpenAI request...")
                        continue
                    else:
                        print("OpenAI request failed after " + str(retries) + " attempts.")
                        failed_text = f"\n\n *OPENAI REQUEST FAILED AFTER {retries} ATTEMPTS* \n" \
                                      f"*NO CONTENT WAS GENERATED FOR SECTION {prompt['section']}* \n\n"
                        prompt["response"] = ""
                        prompt["error"] = failed_text

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




