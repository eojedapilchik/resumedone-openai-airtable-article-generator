import os
import time
import random
import datetime
import re
from fastapi import FastAPI, BackgroundTasks, Body, HTTPException
from dotenv import load_dotenv
from models.article import Article
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.frontapp_handler import FrontAppHandler, FrontAppError
from helpers.lemlist_handler import LemlistHandler
from helpers.instantlyai_handler import InstantlyHandler
from helpers.prompts import prompts
from categorize_articles import update_category
from typing import List
from models.instantly_lead import Lead
from fastapi.middleware.cors import CORSMiddleware
from tasks import add_contacts_to_campaigns
from models.lemlist_webhook import WebhookData
from models.instantly_webhook import InstantlyWebhookData

app = FastAPI()

allowed_origins = [
    "https://block--st-ma-tla-qc-s-h-m-c-p--re52m6d.alt.airtableblocks.com"
]
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # allows all origins
    allow_origin_regex=r"https://.*\.alt\.airtableblocks\.com$",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)

load_dotenv()

prompts_table = os.environ.get("TABLE_PROMPTS")
data_table = os.environ.get("TABLE_DATA")
show_debug = os.environ.get("SHOW_DEBUG") == "True"
log_text = ""
last_index = None


@app.post("/article-texts/")
async def create_article_sections(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.post("/article-category/")
async def update_article_category(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(update_category, article.record_id, article.job_name, article.base_id)
        return {"status": "processing AI categorization for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.post("/article/url/")
async def create_article_url(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(update_url, article.record_id, article.job_name, article.language)
        return {"status": "processing AI categorization for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.get("/article-texts/{record_id}/")
async def create_article(background_tasks: BackgroundTasks, record_id: str, job_name: str,
                         language: str, image_urls: str = None):
    if record_id and job_name and language:
        article = Article(record_id=record_id, job_name=job_name, language=language, image_urls=image_urls)
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + job_name}
    else:
        return {"status": "missing data"}


@app.get("/health/")
async def health_check():
    return {"status": "alive"}


@app.post("/review/{conversation_id}/language/{language}/")
async def create_review_conversation(background_tasks: BackgroundTasks, conversation_id: str, language: str):
    # validate language is a string
    if not language or not isinstance(language, str):
        return {"status": "invalid language"}
    if not conversation_id:
        return {"status": "invalid conversation_id"}
    background_tasks.add_task(create_review_conversation_task, conversation_id, language)
    return {"status": "processing review for Frontapp conversation"}


@app.get("/lemlist/campaigns/")
async def get_campaigns():
    lemlist_api_key = os.environ.get("LEMLIST_API_KEY")
    if lemlist_api_key is None:
        return {"status": "missing lemlist api key"}
    handler = LemlistHandler(lemlist_api_key)
    campaigns = handler.list_campaigns()
    return {"status": "success",
            "campaigns": campaigns}


@app.get("/instantly/campaigns/")
async def get_campaigns():
    handler = get_instantly_handler()
    try:
        campaigns = handler.list_campaigns()
        return {"status": "success",
                "campaigns": campaigns}
    except Exception as e:
        return {"status": "error",
                "response": str(e)}


@app.post("/instantly/campaigns/{campaign_id}/leads/")
async def add_leads_to_campaign(campaign_id: str, leads: List[Lead]):
    handler = get_instantly_handler()
    try:
        response = handler.add_leads_to_campaign(campaign_id, leads)
        return {"status": "success",
                "response": response}
    except Exception as e:
        return {"status": "error",
                "response": str(e)}


@app.post("/instantly/events/")
async def process_webhook(data: InstantlyWebhookData, background_tasks: BackgroundTasks):
    print("Received data")
    print(data.model_dump_json(exclude_none=True))
    background_tasks.add_task(process_instantly_webhook, data)
    # get the id of the background task
    return {"status": "Success. Data is being processed in the background"}


# @app.post("/events/emailreplied/")
# async def process_webhook2(request: Request):
#     body = await request.json()
#     print("Received data:", body)
#     return {"status": "Success. Data is being processed in the background"}


@app.post("/webhook/email_replied/")
async def receive_webhook(data: WebhookData = Body(...)):
    # sendUserEmail = data.sendUserEmail
    # subject = data.subject
    # campaignName = data.campaignName
    # leadId = data.leadId
    # campaignId = data.campaignId
    # text = data.text
    # TODO: optionally check if message is in gmail, process message with openai, send first email
    print(f"Received webhook: {data}")

    return {"message": "Webhook received and processed!"}


def add_p_tags(text):
    # Split the input text into paragraphs based on two or more newlines
    paragraphs = re.split(r'\n\s*\n', text.strip(), flags=re.DOTALL)

    for i in range(len(paragraphs)):
        if not re.match(r'^\s*<\w+>', paragraphs[i]):
            paragraphs[i] = '<p>' + paragraphs[i] + '</p>'

    return '\n\n'.join(paragraphs)


def convert_bullets_to_html(text):
    def replace_with_ul(match):
        items = match.group(0).strip().split('\n')
        li_items = ['<li>' + item[2:].strip() + '</li>' for item in items]
        return '<ul>\n' + '\n'.join(li_items) + '\n</ul>'

    # Replace bulleted lists with <ul><li>...</li></ul>
    text = re.sub(r'(?m)^\s*-\s*.+((\n\s*-.*)*)', replace_with_ul, text)
    return text


def convert_numbers_to_ol(text):
    def replace_with_ol(match):
        items = match.group(0).strip().split('\n')
        li_items = ['<li>' + re.sub(r'^\d+\.\s*', '', item).strip() + '</li>' for item in items]
        return '<ol>\n' + '\n'.join(li_items) + '\n</ol>'

    # Replace numbered lists with <ol><li>...</li></ol>
    text = re.sub(r'(?m)^\s*\d+\.\s*.+((\n\s*\d+\..*)*)', replace_with_ol, text)
    return text


def remove_double_quotes(text):
    text = re.sub(r'^\"', '', text)
    text = re.sub(r'\"$', '', text)
    return text


def remove_empty_html_tags(text):
    pattern = r'<(\w+)\s*>\s*</\1>'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return cleaned_text


def add_html_tags(text):
    text = convert_bullets_to_html(text)
    text = convert_numbers_to_ol(text)
    text = add_p_tags(text)
    text = remove_empty_html_tags(text)
    return text


def update_url(record_id: str, job_name: str, language: str):
    at_token = os.environ.get("AIRTABLE_PAT_SEO_WK")
    airtable_handler = AirtableHandler("tblSwYjjy85nHa6yd", "appkwM6hcso08YF3I", at_token)
    openai_handler = OpenAIHandler()
    if not language or prompts.get('url', {}).get(language) is None:
        print(f"Language not supported for url generation {language}")
        return
    prompt = prompts['url'][language].replace("((title of card))", job_name)
    response = openai_handler.prompt(prompt).lower()
    if len(response) > 0:
        print(f"url ai response {response}")
        airtable_handler.update_record(record_id, {"fldeVySqEkmppVMK7": response}, )
    else:
        print("No response received from OpenAI")


def process_instantly_webhook(data: InstantlyWebhookData):
    if data.event_type == "reply_received":
        handler = get_instantly_handler()
        lead = handler.get_leads_from_campaign(data.campaign_id, data.email)
        if lead is None or len(lead) <= 0:
            print("No lead found")
            return
        sequence = lead[0].get("lead_data", {}).get("sequence_reply", 0)
        if data.is_first or sequence <= 1:
            print("First email received")
            # do the price calculation for the backlink
            # process email with openai
            # send email
            # update lead sequence_reply
        else:
            print("Not first email")

            # send email
            # update lead sequence_reply
        handler.update_leads_sequence_reply(data.campaign_id, data.email, int(sequence) + 1)
        print("Processed reply")
    else:
        print("Not a reply")


def get_instantly_handler():
    """
    Get the InstantlyHandler instance
    :return: InstantlyHandler
    """
    instantly_api_key = os.environ.get("INSTANTLY_API_KEY")
    if instantly_api_key is None:
        raise HTTPException(status_code=400, detail="Missing INSTANTLY API KEY in environment")
    return InstantlyHandler(instantly_api_key)


def create_review_conversation_task(conversation_id: str, language: str) -> bool:
    """
    Create a review for a given conversation in FrontApp.

    Args:
    - conversation_id (str): The ID of the conversation in FrontApp.
    - language (str): The language of the review prompts to use.

    Returns:
    - bool: True if the review was created successfully, False otherwise.
    """
    global last_index
    front_app = FrontAppHandler(os.environ.get("FRONT_API_TOKEN"))
    prompts = get_review_prompts(language)
    openai_handler = OpenAIHandler()
    # Generate a unique random index
    while True:
        random_index = random.randint(0, len(prompts) - 1)
        if random_index != last_index:
            break

    last_index = random_index
    print(f"\r\nRandom index: {random_index} \r\n")
    if prompts is None:
        return False
    try:
        response = openai_handler.prompt(prompts[random_index])
        if response is None or response == "":
            print("No review was obtained from OpenAI")
            return False
        response = sanitize_for_json(response)
        print(f"review: {response}")
        data = {"custom_fields": {
            "Review": response,
        }}
        front_app.update_conversation(conversation_id, data)
        front_app.create_comment(conversation_id, response)
        return True
    except OpenAIException as e:
        return False
    except FrontAppError as e:
        return False


def get_review_prompts(language: str) -> list:
    """
    Retrieve review prompts for a given language from Airtable.

    Args:
    - language (str): The desired language for the review prompts.

    Returns:
    - list: A list of review prompts.
    """
    review_prompts_table = os.environ.get("REVIEW_PROMPTS_TABLE")
    if not review_prompts_table:
        print("Environment variable REVIEW_PROMPTS_TABLE not set!")
        return []

    airtable_handler = AirtableHandler(review_prompts_table)
    try:
        review_prompts = airtable_handler.get_records(filter_by_formula=f"{{Language}}='{language}'")
        if not review_prompts or review_prompts[0] is None:
            print("No review prompts found")
            return []
        review_prompts = review_prompts[0].get("fields")
        review_prompts.pop("Language")
        review_prompts = list(review_prompts.values())
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    print(f"Retrieved {len(review_prompts)} review prompts")
    return review_prompts


@app.post("/lemlist/campaigns/contacts/bulk/")
async def add_contacts_to_campaign(campaign_id: str, contacts_data: list):
    lemlist_api_key = os.environ.get("LEMLIST_API_KEY")
    if lemlist_api_key is None:
        return {"status": "missing lemlist api key"}

    task = add_contacts_to_campaigns.delay(add_contacts_to_campaigns, campaign_id, contacts_data, lemlist_api_key)

    return {"status": "processing",
            "responses": f"Contacts are being added in the background. Task id: {task.id}"}


def remove_unwrapped_headers(text):
    pattern = r'\bh[123]\b'
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text


def process_article(article: Article):
    start_time = time.time()
    prompts = get_prompts(article.language)
    if prompts is None:
        update_airtable_record_log(article.record_id, "No prompts Retrieved")
        print("No prompts found")
        return None
    parsed_prompts = [
        {**prompt, "prompt": (prompt.get("prompt") or "").replace("[job_name]", article.job_name)}
        for prompt in prompts if prompt.get("prompt") != ""
    ]

    sorted_prompts = sorted(parsed_prompts, key=lambda x: x["position"] or float("inf"))
    responses = process_prompts(sorted_prompts, article)
    if responses is None:
        update_airtable_record_log(article.record_id, "No responses found for prompts")
        print("No responses found")
        return None

    #update_airtable_record_log(article.record_id, "Responses retrieved and sorted")
    if show_debug:
        sections = [record["section"] for record in responses]
        print(sections)
        prompts = [record["prompt"] for record in responses]
        print(prompts)
    end_time = time.time()
    elapsed_time_bf_at = end_time - start_time
    update_airtable_record(article.record_id, responses, elapsed_time_bf_at)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


def get_prompts(language: str):
    airtable_handler = AirtableHandler(prompts_table)
    records = airtable_handler.get_records()
    if records:
        prompts = [{
            "response": "",
            "section": record.get("fields").get("Section Name"),
            "prompt": record.get("fields").get(f"Prompt {language}"),
            "position": record.get("fields").get("Position"),
            "type": record.get("fields").get("Type", "").lower()
            if record.get("fields").get("Type", "").lower() != "body" else ""
        } for record in records]
        return prompts
    return None


def process_prompts(prompts: list, article: Article):
    global log_text
    record_id = article.record_id
    images_url_csv = article.image_urls
    images_url = images_url_csv.split(",") if images_url_csv else []
    retries = int(os.getenv("OPENAI_RETRIES", 3))
    openai_handler = OpenAIHandler()
    index = 0
    metadata_list = ["meta title", "meta description"]
    metadata = {
        metadata_list[0]: "",
        metadata_list[1]: ""
    }
    for prompt in prompts:
        index += 1
        for i in range(retries):
            try:
                print(f" - Processing prompt...{index} -> Attempt {i + 1}/{retries}")
                prompt_text = prompt.get("prompt")
                response = ""
                if prompt_text is not None or prompt_text != "":
                    response = openai_handler.prompt(prompt.get("prompt"))
                print(f"[+] Received response from OpenAI {index}")
                update_airtable_record_log(record_id, f"Received response from OpenAI - # {index}")
                prompt_info = f"\n[SECTION {prompt['position']}] \n {prompt['section']} \n[PROMPT] \n " \
                              f"{prompt['prompt']}\n"
                log_text += prompt_info
                if show_debug:
                    print(prompt_info + f"\n\n[RESPONSE] {response}\n\n")
                if prompt["type"] in metadata_list:
                    metadata[prompt["type"]] = remove_double_quotes(response)
                    break
                if prompt["type"].lower().strip() == "image":
                    image_url = images_url.pop(0) if len(images_url) > 0 else ""
                    print(f"Image url: {image_url}")
                    if image_url:
                        response = f'<img src="{image_url}"/>'
                        prompt["response"] = f"\n{response}\r\n"
                    break
                if prompt["type"].lower().strip() == "example":
                    response = add_html_tags(remove_double_quotes(response))
                    prompt[
                        "response"] = f'<div class="grey-div">\n<div class="grey-div">\n<div>{response}</div>\n</div>\n</div><br>'
                    break
                if prompt["type"] and prompt["type"] != "":
                    response = remove_unwrapped_headers(remove_double_quotes(response))
                    prompt["response"] = f"\n<{prompt['type']}>{response}</{prompt['type']}>\r\n"
                    break
                else:
                    response = add_html_tags(remove_double_quotes(response))
                    prompt["response"] = f"\n{response}\r\n"
                break
            except OpenAIException as e:
                print("Error: " + str(e))
                if i < retries - 1:  # i is zero indexed
                    time.sleep((2 ** i))  # exponential backoff, sleep for 2^i seconds
                    print(f"Retrying OpenAI request...")
                    continue
                else:
                    print("OpenAI request failed after " + str(retries) + " attempts.")
                    failed_text = f"\n\n *OPENAI REQUEST FAILED AFTER {retries} ATTEMPTS* \n" \
                                  f"*NO CONTENT WAS GENERATED FOR SECTION {prompt['section']}* \n\n"
                    log_text += failed_text
                    prompt["response"] = failed_text

        if metadata and index == 2:
            update_metadata(record_id, metadata)
    return prompts


def update_airtable_record(record_id, responses_list, elapsed_time_bf_at: float = 0):
    global log_text
    print("[+] Updating Airtable record...")
    airtable_handler = AirtableHandler(data_table)
    if len(responses_list) <= 0:
        print("[-] Insufficient responses provided.")
        return None
    responses = [response["response"] for response in responses_list]
    current_utc_time = datetime.datetime.utcnow()
    iso8601_date = current_utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    try:
        fields = {
            "fld7vn74uF0ZxQhXe": ''.join(responses),
            "fldus7pUQ61eM1ymY": elapsed_time_bf_at,
            "fldsnne20dP9s0nUz": "To Review",
            "fldTk3wrPUWrx0AjP": iso8601_date,
            "fldpnyajPwaBXM6Zb": log_text if log_text != "" else "Success"
        }
        airtable_handler.update_record(record_id, fields)
        print("[+] Airtable record updated successfully.")
        log_text = ""
    except Exception as e:
        print(f"[!!] Error updating record: {str(e)}")
        print(responses_list)


def update_metadata(record_id, metadata: dict):
    print("[+] Updating Airtable record...")
    airtable_handler = AirtableHandler(data_table)
    try:
        fields = {
            "fldIvmfoPfkJbYDcy": metadata.get("meta description"),
            "fld4v3esUgKDDH9aI": metadata.get("meta title"),
        }
        airtable_handler.update_record(record_id, fields)
        print("[+] Airtable record updated successfully.")
    except Exception as e:
        print(f"[!!] Error updating record: {str(e)}")


def update_airtable_record_log(record_id, new_status: str = 'Error'):
    print("[+] Updating Airtable record...")
    airtable_handler = AirtableHandler(data_table)
    try:
        fields = {
            "fldpnyajPwaBXM6Zb": new_status
        }
        airtable_handler.update_record(record_id, fields)
        print("[+] Airtable record updated successfully.")
    except Exception as e:
        print(f"[!!] Error updating record: {str(e)}")


def sanitize_for_json(input_str: str) -> str:
    replacements = {
        '\\': '',  # Remove backslashes
        '"': '',  # Remove double quotes
        '\n': ' ',  # Replace newlines with space
        '\t': ' ',  # Replace tabs with space
        '\r': ' ',  # Replace carriage returns with space
        '\'': '',  # Replace single quotes with apostrophes
    }

    for char, replacement in replacements.items():
        input_str = input_str.replace(char, replacement)

    return input_str
