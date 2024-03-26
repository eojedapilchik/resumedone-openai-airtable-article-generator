import os
import openai


class OpenAIException(Exception):
    """Custom exception for OpenAI errors."""

    def __init__(self, message, response=None):
        super().__init__(message)

        self.response = response
        self.status_code = None
        self.openai_error = None
        if response:
            self.status_code = response.status_code
            try:
                json_response = response.json()
                if 'error' in json_response:
                    self.openai_error = json_response['error']
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
            engine = os.getenv("OPENAI_ENGINE", "gpt-3.5-turbo")
        self.engine = engine
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def prompt(self, message: str, max_tokens: int = 1000,
               temperature: float = 0.7):
        try:
            if self.engine == "text-davinci-003":
                response = openai.Completion.create(engine=self.engine,
                                                    prompt=message,
                                                    max_tokens=max_tokens,
                                                    temperature=temperature)
            else:
                response = openai.ChatCompletion.create(model=self.engine,
                                                        messages=[
                                                            {"role": "user",
                                                             "content": message}],
                                                        temperature=temperature)
            return response.choices[0]["message"]["content"].strip()
        except Exception as e:
            print("Open AI Error: " + str(e))
            raise OpenAIException(str(e)) from e

    def prompt_with_image_input(self, message: list, image_url: str,
                                max_tokens: int = 1000,
                                temperature: float = 0.7,
                               ):

        try:
            print(f"using engine: {self.engine}")
            response = openai.ChatCompletion.create(model=self.engine,
                                                    messages=message,
                                                    max_tokens=max_tokens,
                                                    temperature=temperature)
            return response.choices[0]["message"]["content"].strip()
        except Exception as e:
            print("Open AI Error: " + str(e))
            raise OpenAIException(str(e)) from e
