import json
import os


def load_translations(language: str):
    translations_file = os.path.join('translations', f'translations_{language}.json')
    try:
        with open(translations_file, 'r', encoding='utf-8') as file:
            translations = json.load(file)
    except FileNotFoundError:
        print(f"Translation file for '{language}' not found.")
        translations = {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in translation file for '{language}'.")
        translations = {}
    return translations


def translate_text(text: str, language: str):
    translations = load_translations(language) if language != 'EN' else {}
    return translations.get(text) or text
