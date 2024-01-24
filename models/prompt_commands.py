import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from helpers.airtable_handler import AirtableHandler
from models.article import Article
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.html_utils import (remove_double_quotes, add_html_tags, remove_unwrapped_headers)


class PromptCommand(ABC):
    @abstractmethod
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None,
                airtable_handler: Optional[AirtableHandler] = None, **kwargs) -> None:
        openai_handler = openai_handler or OpenAIHandler()
        show_debug = os.environ.get("SHOW_DEBUG") == "True"
        if openai_handler is None:
            raise ValueError("openai_handler cannot be None")
        prompt_text = prompt.get("prompt")
        prompt_text = prompt_text.strip() if prompt_text else ""
        if prompt_text is not None or prompt_text != "":
            for i in range(retries):
                try:
                    response = openai_handler.prompt(prompt_text)
                    prompt["plain_text"] = f"{response}\n"
                    response = remove_double_quotes(response)
                    prompt["response"] = response
                    if show_debug:
                        prompt_info = f"\n[SECTION {prompt['position']}] \n {prompt['section']} \n[PROMPT] \n " \
                                      f"{prompt['prompt']}\n"
                        print(prompt_info + f"\n\n[RESPONSE] {prompt['response']}\n\n")
                    break
                except OpenAIException as e:
                    if i < retries - 1:  # i is zero indexed
                        time.sleep((10 ** i))  # exponential backoff, sleep for 2^i seconds
                        print(f"Retrying OpenAI request...")
                        continue
                    else:
                        print("OpenAI request failed after " + str(retries) + " attempts.")
                        failed_text = f"\n\n *OPENAI REQUEST FAILED AFTER {retries} ATTEMPTS* \n" \
                                      f"*NO CONTENT WAS GENERATED FOR SECTION {prompt['section']}* \n\n"
                        prompt["response"] = ""
                        prompt["error"] = failed_text
                        raise Exception("OpenAI request failed after " + str(retries) + " attempts.")


class MetaDataPromptCommand(PromptCommand):

    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        prompt["response"] = ""
        prompt["metadata"] = {"type": prompt["type"], "value": response}
        return None


class SampleCoverLetterCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None,
                airtable_handler: Optional[AirtableHandler] = None,
                **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        prompt["response"] = ""
        prompt["sample_cover_letter"] = add_html_tags(response)
        return None


class ImagePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        image_urls_csv = article.image_urls
        images_urls_list = image_urls_csv.split(",") if image_urls_csv else []
        image_url = images_urls_list.pop(0) if len(images_urls_list) > 0 else ""
        article.image_urls = ",".join(images_urls_list) if len(images_urls_list) > 0 else ""
        image_url = image_url.strip() if image_url else ""
        extra_class = ""
        if article.type is not None and article.type == "Cover Letter":
            extra_class = "cover-letter-image"
        if image_url:
            prompt["response"] = (
                f'\n<figure class="w-richtext-figure-type-image w-richtext-align-center" style="max-width:626px">'
                f'    <div class="imagen {extra_class}">'
                f'        <img src=\'{image_url}\'/>'
                f'    </div>'
                f'</figure>')


class ExamplePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        response = add_html_tags(response)
        prompt["response"] = f'\n<div class=\'grey-div\'>\n<div>{response}</div>\n</div><br>\n'


class DefaultPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        # Processing logic for image prompts
        super().execute(prompt, retries, article, openai_handler, **kwargs)


class InternalReferenceSectionCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        if not article.internal_refs:
            return None
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response", "")
        prompt["response"] = f"<div id='internal-refs'><p>{response}</p><br>{article.internal_refs}</div>" \
            if article.internal_refs else ""


class HTMLPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        tag_type = prompt.get("type").lower().strip()
        is_title = tag_type in ["h1", "h2", "h3"]
        response = prompt.get("response")
        if is_title:
            response = remove_unwrapped_headers(response)
        else:
            response = add_html_tags(response)
        prompt["response"] = f"\n<{prompt['type']}>{response}</{prompt['type']}>\r\n"
