from abc import ABC, abstractmethod
from typing import Dict
from helpers.html_utils import (add_p_tags, convert_bullets_to_html,
                                convert_numbers_to_ol, remove_double_quotes, remove_empty_html_tags)

class PromptCommand(ABC):
    @abstractmethod
    def execute(self, prompt: Dict, retries: int, **kwargs) -> str:
        pass

class MetaDataPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, **kwargs) -> str:
        metadata = kwargs.get('metadata')
        if metadata is None:
            raise ValueError("MetaData prompt command requires 'metadata' parameter")
        # Processing logic for meta prompts
        return ""

class ImagePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, **kwargs) -> str:
        image_urls = kwargs.get('image_urls')
        if image_urls is None:
            raise ValueError("Image section requires 'image_urls' parameter")
        # Processing logic for image prompts
        return ""

class ExamplePromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, **kwargs) -> str:
        # Processing logic for image prompts
        return ""


class DefaultPromptCommand(PromptCommand):
    def execute(self, prompt: Dict, retries: int, **kwargs) -> str:
        # Processing logic for image prompts
        return ""


