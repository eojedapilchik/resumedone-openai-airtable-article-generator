import os
import json
import re
import time
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.airtable_handler import AirtableHandler

def process_content(text_to_translate, image_url, record_id, airtable_handler):
    # list_of_languages = os.getenv("LIST_OF_LANGUAGES").split(", ")
    start_time = time.time()
    model_vision = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
    openai_handler = OpenAIHandler(model_vision)

    fields_list = airtable_handler.get_table_schema("Content").fields
    if not fields_list:
        print("No fields found in Content table")
        return

    language_list = extract_language_fields(fields_list)

    list_of_languages = [language['iso_code'] for language in language_list]

    batch_size = len(list_of_languages) // 8
    batches = [list_of_languages[i:i + batch_size] for i in range(0, len(list_of_languages), batch_size)]

    is_error = False
    aggregated_data = {}
    for index, batch in enumerate(batches):
        print(f"Processing content batch {index}...{batch}")
        data, error = process_batch(batch, text_to_translate, image_url, openai_handler)
        if error:
            is_error = True
            aggregated_data.update(data)
            break  # Stop processing if error
        aggregated_data.update(data)
        # add a delay to avoid rate limiting
        time.sleep(5)

    elapsed_time = time.time() - start_time
    aggregated_data["elapsed_time"] = str(elapsed_time)
    update_airtable_record(record_id, aggregated_data, airtable_handler, is_error, language_list)
    print(f"Elapsed time: {elapsed_time}")

def process_batch(batch, text_to_translate, image_url, openai_handler):

    message = prepare_message(text_to_translate, image_url, batch)

    try:
        response = openai_handler.prompt_with_image_input(message, image_url)
        print(f"Batch response: {response}")
        data = process_openai_response(response)
        return data, False
    except OpenAIException as e:
        msg = f"Error in batch processing OpenAI: {str(e)}\r\n batch: {batch}"
        print(msg)
        return {"error": msg}, True


def extract_language_fields(fields_list):
    language_pattern = re.compile(r'^([a-z]{2}(?:-[a-zA-Z]{2})?) - [A-Za-z ]+$')
    return [
        {
            'iso_code': language_pattern.match(field.name).group(1),
            'field_id': field.id,
            'field_name': field.name
        }
        for field in fields_list
        if field.type in ('singleLineText','multilineText') and language_pattern.match(field.name)
    ]

def prepare_message(text_to_translate, image_url, list_of_languages):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text",
                 "text":  f"""Using the provided image as context, translate the text '{text_to_translate}' into the following languages: {list_of_languages}. 
                 Provide the response in JSON format, using the same keys as specified in the languages list.
                 Important Instructions: 1. If the text contains constants, code elements, or HTML tags, do not translate these. Keep them unchanged.
                 2. Maintain any special characters such as parentheses (), braces {{}}, brackets [], >>, <<, /,//,\\, . and similar symbols exactly as they appear. 
                 3. Only translate the human-readable text while preserving the structure of the text. Do not include any additional text or commentary in the response."""
                 },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                },
            ],
        }
    ]

def process_openai_response(response):
    match = re.search(r'{.*}', response, re.DOTALL)
    if match:
        response = match.group(0)
        data = json.loads(response)
        return data
    else:
        msg = f"Error converting text to json:\r\n {response}"
        print(msg)
        return {"error": msg}


def update_airtable_record(record_id: str, data: dict, airtable_handler: AirtableHandler, is_error: bool = False,
                           language_list=None):
    if language_list is None:
        language_list = []
    fields = {}
    if is_error:
        fields["fldWrOfUF03hHjMls"]= str(data.get("error"))
    for language in language_list:
        iso_code = language['iso_code']
        field_id = language['field_id']
        fields[field_id] = data.get(iso_code, "")
    fields["fldorL0bJiNXElC3k"] = data.get("elapsed_time", "")
    airtable_handler.update_record(record_id, fields)

