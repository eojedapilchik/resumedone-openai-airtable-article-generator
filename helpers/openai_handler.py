import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


class OpenAIException(Exception):
    """Custom exception for OpenAI errors."""

    def __init__(self, message, response=None):
        super().__init__(message)

        # Assuming `response` is the raw response object from the requests library:
        self.response = response

        # Attempt to extract status code and OpenAI-specific error message:
        self.status_code = response.status_code if response else None
        try:
            self.openai_error = response.json().get('error', '') if response else None
        except ValueError:
            self.openai_error = None

        # Print statements for immediate feedback:
        print(f"OpenAIException encountered!")
        print(f"Message: {message}")
        if self.status_code:
            print(f"HTTP Status Code: {self.status_code}")
        if self.openai_error:
            print(f"OpenAI-specific Error Message: {self.openai_error}")


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
