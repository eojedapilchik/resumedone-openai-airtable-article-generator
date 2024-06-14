import json
from dotenv import load_dotenv
from typing import List, Union
from models.instantly_lead import Lead
import time
import requests
import os

load_dotenv()


class JsonFileHandler:
    def __init__(self, filename: str = None):
        self.file_path = f"backup_{filename}.json"

    def write_file(self, content: json):
        try:
            with open(self.file_path, "w") as file:
                json.dump(content, file, indent=2)
        except Exception as e:
            print(str(e))
            self.delete_file()

    def read_file(self) -> json:
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except Exception as e:
            print(str(e))
            self.delete_file()
        return None

    def is_file_exist(self):
        return os.path.isfile(self.file_path)

    def delete_file(self):
        if self.is_file_exist():
            os.remove(self.file_path)
        print(f"File removed: {self.file_path}")
