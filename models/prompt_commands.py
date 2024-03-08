import re
import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from helpers.airtable_handler import AirtableHandler
from helpers.translation_utils import translate_text
from models.article import Article
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.html_utils import (add_p_tags, remove_double_astrix, remove_double_quotes, add_html_tags, remove_empty_html_tags,
                                remove_unwrapped_headers)


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
                    prompt["plain_text"] = f"[SECTION {prompt['position']}]: {response}\n"
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


class FAQTitleCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None,
                airtable_handler: Optional[AirtableHandler] = None,
                **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        prompt["response"] = ""
        prompt["faq_title"] = f'<h2 class="questions-h2">{remove_unwrapped_headers(response)}</h2>'
        return None


class FAQDefaultContentCommand(PromptCommand):

    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None,
                airtable_handler: Optional[AirtableHandler] = None,
                **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        prompt["response"] = ""
        prompt["faq_content"] = self.add_special_design(response)
        return None

    def add_special_design(self, response: str):
        qa_sections=[]
        qa = re.split(r'\s*\n\s*\n*\s*', response.strip())
        res_sections=[]
        for i in range(len(qa)+1):
            sentense= qa[i] if i < len(qa) else None
            if sentense:
                if "?" in sentense:
                    if len(res_sections)>0:
                        qa_sections.append(self.add_response_tags(add_p_tags('\n'.join(res_sections)))) 
                        res_sections=[]
                    qa_sections.append(self.add_question_tags(sentense))
                    continue
                res_sections.append(sentense)
            elif len(res_sections)>0 and i==len(qa):
                qa_sections.append(self.add_response_tags(add_p_tags('\n'.join(res_sections)))) 
        text = '\n'.join(qa_sections)
        text = remove_empty_html_tags(text)
        text = remove_double_astrix(text)
        return text

    def add_question_tags(self, text: str):
        return (f'<div>\n'
                f'     <p>{text}</p>\n')

    def add_response_tags(self, text: str):
        return (f'      {text}\n'
                f'</div>')


class CommonFAQContentCommand(FAQDefaultContentCommand):
    def add_question_tags(self, text: str):
        return (f'<div class="accordian-item">\n'
                f'  <div class="accordian-trigger">\n'
                f'      <div class="accordion-question">{text}</div>\n'
                f'      <div class="accordian-cross">\n'
                f'          <div class="cross-h"></div>\n'
                f'          <div class="cross-h v" style="transform: translate3d(0px, 0px, 0px) scale3d(1, 1, '
                f'1) rotateX('
                f'0deg) rotateY(0deg) rotateZ(0deg) skew(0deg, 0deg); transform-style: preserve-3d;"></div>\n'
                f'      </div>\n'
                f'  </div>\n')

    def add_response_tags(self, text: str):
        return (f'  <div class="accordian-content">\n'
                f'      {text}\n'
                f'  </div>\n'
                f'</div>')


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


class CommonExamplePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        response = add_html_tags(response, from_example_command=True)
        correct_translation = translate_text('correct', article.language)
        prompt["response"] = (
            f'\n<div class="green-highlight">'
            f'  <div class="green-highlight-cont">'
            f'      <img src=\'https://assets.website-files.com/639975e5f44de65498a14a0e'
            f'/63a0b5fcd66a3b979be8565b_icon-check.svg\'>{correct_translation.upper()}</div>'
            f'  <div>{response}</div>'
            f'</div><br>\n')


class SampleResumeExampleCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, article: Article,
                openai_handler: Optional[OpenAIHandler] = None, **kwargs) -> None:
        super().execute(prompt, retries, article, openai_handler, **kwargs)
        response = prompt.get("response")
        response = add_html_tags(response)
        prompt["response"] = f'\n<div class=\'grey-div\'>\n<div>{response}</div>\n</div><br>\n'


class ExampleDefaultPromptCommand(PromptCommand):
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
