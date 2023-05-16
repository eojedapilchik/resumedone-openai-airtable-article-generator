import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


class OpenAIException(Exception):
    """Custom exception for OpenAI errors."""


class OpenAIHandler:
    def __init__(self, engine: str = None):
        if engine is None:
            engine = os.getenv("OPENAI_ENGINE", "text-davinci-002")
        self.engine = engine

    def prompt(self, message: str, max_tokens: int = 1000, temperature: float = 0.7):

        try:
            response = openai.Completion.create(engine=self.engine,
                                                prompt=message, max_tokens=max_tokens, temperature=temperature)
            return response.choices[0].text.strip()
        except Exception as e:
            print("Open AI Error: " + str(e))
            raise OpenAIException(str(e)) from e
