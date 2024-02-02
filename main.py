import os
import time
import random
import re
from fastapi import FastAPI, BackgroundTasks, Body, HTTPException, Query
from dotenv import load_dotenv
from helpers.article_processor import ArticleProcessor
from models.article import Article
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.frontapp_handler import FrontAppHandler, FrontAppError
from helpers.lemlist_handler import LemlistHandler
from helpers.instantlyai_handler import InstantlyHandler
from helpers.prompts_config import prompts_cfg
from categorize_articles import update_category
from typing import List
from models.instantly_lead import Lead
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/article/{record_id}/translate-job/")
async def translate_job_name(background_tasks: BackgroundTasks, record_id: str, job_name: str):
    if record_id and job_name:
        background_tasks.add_task(translate_job, record_id, job_name)
        return {"status": "processing job name translation for article: " + job_name}
    else:
        return {"status": "missing data"}


@app.get("/article-texts/{record_id}/")
async def create_article(background_tasks: BackgroundTasks, record_id: str, job_name: str,
                         language: str, image_urls: str = None, internal_refs: str = None,
                         article_type: str = Query(None, alias="type")):
    if record_id and job_name and language:
        article = Article(record_id=record_id, job_name=job_name, language=language, image_urls=image_urls,
                          internal_refs=internal_refs, type=article_type)
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


def update_url(record_id: str, job_name: str, language: str):
    at_token = os.environ.get("AIRTABLE_PAT_SEO_WK")
    airtable_handler = AirtableHandler("tblSwYjjy85nHa6yd", "appkwM6hcso08YF3I", at_token)
    openai_handler = OpenAIHandler()
    if not language or prompts_cfg.get('url', {}).get(language) is None:
        print(f"Language not supported for url generation {language}")
        return
    prompt = prompts_cfg['url'][language].replace("((title of card))", job_name)
    response = openai_handler.prompt(prompt).lower()
    if len(response) > 0:
        print(f"url ai response {response}")
        airtable_handler.update_record(record_id, {"fldeVySqEkmppVMK7": response}, )
    else:
        print("No response received from OpenAI")


def translate_job(record_id, job_name):
    engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
    openai_handler = OpenAIHandler(engine)
    if prompts_cfg.get('translate', {}) is None:
        print(f"A prompt for translation was not found")
        return None
    prompt = prompts_cfg['translate'].replace("((title of card))", job_name)
    response = openai_handler.prompt(prompt).lower()
    if len(response) > 0:
        print(f"translation ai response {response}")
        try:
            airtable_handler = AirtableHandler(data_table)
            airtable_handler.update_record(record_id, {"fldUIXxtRzNURofJT": response})
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("No response received from OpenAI")
        return None


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


def remove_unwrapped_headers(text):
    pattern = r'\bh[123]\b'
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text


def process_article(article: Article):
    start_time = time.time()
    print(f"Processing Article: {article.job_name} id {article.record_id} type: {article.type}")
    prompts = get_prompts(article)
    engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
    article_processor = ArticleProcessor(OpenAIHandler(engine), article.record_id, AirtableHandler(data_table))
    if prompts is None:
        article_processor.update_airtable_record_log(article.record_id, "No prompts Retrieved")
        print("No prompts found")
        return None

    sorted_prompts = sorted(prompts, key=lambda x: x["position"] or float("inf"))

    prompts = article_processor.process(sorted_prompts, article)
    if prompts is None:
        article_processor.update_airtable_record_log(article.record_id, "No responses found for prompts")
        print("No responses found")
        return None

    if show_debug:
        sections = [record["section"] for record in prompts]
        print(sections)
        prompts = [record["prompt"] for record in prompts]
        print(prompts)

    end_time = time.time()
    elapsed_time_bf_at = end_time - start_time
    article_processor.update_airtable_record(article.record_id, prompts, elapsed_time_bf_at)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


def get_prompts(article: Article):
    article_type_name_parsed = article.type.upper().strip().replace(' ', '_')
    table_env_variable_name = f"TABLE_{article_type_name_parsed}_PROMPTS"
    table_name = os.environ.get(table_env_variable_name)
    if table_name is None:
        print(f"Table name not found for {article_type_name_parsed}")
        return None
    airtable_handler = AirtableHandler(table_name)
    records = airtable_handler.get_records()
    return [parse_prompt(record, article) for record in records] if records else None


def parse_prompt(record: dict, article: Article):
    prompt_text = record.get("fields").get(f"Prompt {article.language}", "")
    placeholders = re.findall(r'\[(.*?)]', prompt_text)
    for placeholder in placeholders:
        #value_to_replace = record.get("fields").get(placeholder, f"No value for {placeholder}")
        prompt_text = prompt_text.replace(f"[{placeholder}]", article.job_name)

    return {
            "response": "",
            "section": record.get("fields").get("Section Name"),
            "plain_text": "",
            "prompt": prompt_text,
            "position": record.get("fields").get("Position"),
            "type": record.get("fields").get("Type", "").lower()
            if record.get("fields").get("Type", "").lower() != "body" else ""
        }


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
