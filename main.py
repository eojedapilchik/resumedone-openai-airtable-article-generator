import json
import os
import time
import random
import re
from fastapi import FastAPI, BackgroundTasks, Body, HTTPException, Query
from dotenv import load_dotenv
import requests
from helpers.article_processor import ArticleProcessor
from helpers.skill_processor import SkillProcessor
from models.article import Article
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.frontapp_handler import FrontAppHandler, FrontAppError
from helpers.lemlist_handler import LemlistHandler
from helpers.instantlyai_handler import InstantlyHandler
from helpers.prompts_config import prompts_cfg
from helpers.content_processor import process_content
from categorize_articles import update_category
from typing import Dict, List
from models.experience import Experience
from models.instantly_lead import Lead
from fastapi.middleware.cors import CORSMiddleware
from models.lemlist_webhook import WebhookData
from models.instantly_webhook import InstantlyWebhookData
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()
# Determine the number of workers
cpu_count = os.cpu_count()
max_workers = cpu_count * 2
executor = ThreadPoolExecutor(max_workers=max_workers)
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

SKILL_NUMBER = 1000
data_table = os.environ.get("TABLE_DATA")
data_job_titles_table = os.environ.get("TABLE_JOB_TITLE_DATA")
show_debug = os.environ.get("SHOW_DEBUG") == "True"
log_text = ""
last_index = None
skill_database_selection = {
    "DB1": {
        "baseID": os.getenv('SKILL_DB'),
        "promptTableID": os.getenv('TABLE_JOB_TITLE_SKILLS_PROMPTS'),
        "jobTileTableID": os.getenv('TABLE_JOB_TITLE_DATA'),
        "logFieldId": 'fldItAzHHZqCXIe2L',
        "JSONFieldId": 'fld4E0I8A0wpMJnpR',
        "statusFieldId": 'fldPB27E7ukn8tEyd',
        "elapsedTimeFieldId": 'fldy8C7I29M1qr15W',
        "finishedTimeFieldId": 'fldL2EO87nY2uFITE',
    },
    "DB2": {
        "baseID": os.getenv('SKILL_DB_ANNEX'),
        "promptTableID": os.getenv('TABLE_JOB_TITLE_SKILLS_PROMPTS_ANNEX'),
        "jobTileTableID": os.getenv('TABLE_JOB_TITLE_DATA_ANNEX'),
        "logFieldId": 'fldC5HJV2NhmScEJu',
        "JSONFieldId": 'fldSEO3ffaME80GPs',
        "statusFieldId": 'fldVB756iqaDLIHJ3',
        "elapsedTimeFieldId": 'fldyCqWuhezAbH1cq',
        "finishedTimeFieldId": 'fldDSb63NlIY333cx',
    }
}


@app.post("/article-texts/")
async def create_article_sections(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.get("/generate-bullet-from-experience")
async def generate_bullet_experience(job_role: str, company_name: str, experience_content: str):
    if job_role and company_name and experience_content:
        experience= Experience(job_role=job_role,experience_content=experience_content, company_name=company_name)
        type="extract_bullet"
        if prompts_cfg.get(type, {}) is None:
            print(f"A prompt for extraction was not found")
            return None
        prompt = prompts_cfg[type].replace("[[Job Role]]", experience.job_role)
        prompt = prompt.replace("[[Name of the Company]]", experience.company_name)
        prompt = prompt.replace("[[Experience content]]", experience.experience_content)
        return execute_extraction(prompt)
    else:
        return {"status": "missing data"}


@app.get("/generate-list-of-transformation-selection")
async def generate_list_transformation(transformation_selection: str):
    if transformation_selection:
        type="transformation_list"
        if prompts_cfg.get(type, {}) is None:
            print(f"A prompt for extraction was not found")
            return None
        prompt = prompts_cfg[type].replace("[[List of Transformation selection]]", transformation_selection)
        return execute_extraction(prompt)
    else:
        return {"status": "missing data"}


@app.get("/generate-outcome-question")
async def generate_outcome_question(job_role: str, bullet_point_name: str, language: str):
    if job_role and bullet_point_name:
        if language == '' or  language is None:
            language= 'french'
        type="outcome_question"
        if prompts_cfg.get(type, {}) is None:
            print(f"A prompt for extraction was not found")
            return None
        prompt = prompts_cfg[type].replace("[[job_role]]", job_role)
        prompt = prompt.replace("[[bullet_point_name]]", bullet_point_name)
        prompt = prompt.replace("[[language]]", language)
        engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
        openai_handler = OpenAIHandler(engine)
        response = openai_handler.prompt(prompt)
        return response
    else:
        return {"status": "missing data"}


@app.get("/generate-skill/{record_id}")
async def generate_json_skill(background_tasks: BackgroundTasks, record_id: str, job_name: str,
                              language: str, base_source: str):
    if record_id and job_name and language and (base_source in ['DB1', 'DB2']):
        article = Article(record_id=record_id, job_name=job_name, language=language)
        background_tasks.add_task(process_job, article, base_source)
        return {"status": "processing AI for generating skill for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.get("/process-skill-generation")
async def generate_json_skill(background_tasks: BackgroundTasks, base_source: str):
    if base_source in ['DB1', 'DB2']:
       background_tasks.add_task(lauching_skill_generation_in_bulk, base_source)
       return {"status": "generating skill by AI for article processing "}
    else:
        return {"status": "missing data"}


async def lauching_skill_generation_in_bulk(base_source):
    job_titles = get_new_job_title(base_source)
    tasks = []
    for job_title in job_titles:
        fields = job_title.get('fields')
        if fields:
             record_id = fields.get('Airtable ID')
             job_name = fields.get('Job name')
             article = Article(record_id=record_id, job_name=job_name, language="EN")
             task = run_in_threadpool(process_job, article, base_source)
             tasks.append(task)
    await asyncio.gather(*tasks)


async def run_in_threadpool(fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fn, *args, **kwargs)


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


@app.get("/get-resume-samples-data/{record_id}")
async def target_article_generation(background_tasks: BackgroundTasks, record_id: str, task_id: str, job_name: str,
                                    first_retry_after: int):
    if record_id and job_name and task_id:
        article = Article(record_id=record_id, job_name=job_name)
        background_tasks.add_task(process_getting_task_response, article, task_id, first_retry_after)
        return {"status": "getting resume sample images for article: " + job_name}
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


@app.get("/airtable/translations/{record_id}/")
async def get_translations(record_id: str, background_tasks: BackgroundTasks):
    base_id = os.environ.get("BASE_ADMIN_ID")
    table_id = os.environ.get("TABLE_CONTENT_ADMIN")
    if record_id is None:
        return {"status": "missing record_id"}
    airtable_handler = AirtableHandler(table_id, base_id)
    content = airtable_handler.get_record(record_id, "Content")
    if not content:
        return {"status": "error",
                "message": "No article found"}
    image_urls = content.get("fields").get("image")[0].get("thumbnails").get("full").get("url")
    if not image_urls:
        return {"status": "error",
                "message": "No image found"}
    text_to_translate = content.get("fields").get("en - English")
    if not text_to_translate:
        return {"status": "error",
                "message": "No text found"}
    record_id = content.get("id")

    background_tasks.add_task(process_content, text_to_translate, image_urls, record_id, airtable_handler)
    return {"status": "processing, Results will be updated in Airtable soon",
            "article": record_id}


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


def execute_extraction(prompt :str):
    engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
    openai_handler = OpenAIHandler(engine)
    response = openai_handler.prompt(prompt)
    response = response.replace("\n", "")
    response = response.replace("\\\"", "\"")
    if len(response) > 0:
        try:
            return json.loads(response)
        except Exception as e:
            return {"status": "the response is not a valid json"}
    else:
        print("No response received from OpenAI")
        return {"status": "no response from Open AI"}


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


NOT_LATIN_LANGUAGES = ["Kazakh"]


def translate_job(record_id, job_name):
    convert_job(record_id, job_name, 'translate', "fldUIXxtRzNURofJT")
    lang = get_article_language(record_id)
    if lang in NOT_LATIN_LANGUAGES:
        convert_job(record_id, job_name, 'transliterate', "fldL6ebIQHkbaPv01")


def get_article_language(record_id: str):
    airtable_handler = AirtableHandler(data_table)
    found_article = airtable_handler.get_records(filter_by_formula=f"FIND(\"{record_id}\", {{Airtable ID}})")
    if not found_article or found_article[0] is None:
        print("No article found")
        return None
    return found_article[0].get("fields").get('Language (from Language2)')[0] or None


def convert_job(record_id, job_name, type, fieldId):
    engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
    openai_handler = OpenAIHandler(engine)
    if prompts_cfg.get(type, {}) is None:
        print(f"A prompt for translation was not found")
        return None
    prompt = prompts_cfg[type].replace("((title of card))", job_name)
    response = openai_handler.prompt(prompt).lower()
    if len(response) > 0:
        print(f"translation ai response {response}")
        try:
            airtable_handler = AirtableHandler(data_table)
            airtable_handler.update_record(record_id, {fieldId: response})
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


def process_job(article: Article, base_source: str = "DB1"):
    start_time = time.time()
    print(f"Processing Article: {article.job_name} id {article.record_id} type: Skill generation")
    airtable_skill_token = os.getenv('AIRTABLE_SKILL_GENERATION_TKN')
    engine = os.environ.get("OPENAI_ENGINE_LATEST", "gpt-4")
    selected_db = skill_database_selection.get(base_source)
    prompts = get_job_skill_prompts(article.job_name)
    job_title_table = selected_db.get("jobTileTableID")
    database_id = selected_db.get("baseID")
    skill_processor = SkillProcessor(OpenAIHandler(engine), article.record_id,
                                     AirtableHandler(job_title_table, database_id, airtable_skill_token), selected_db)
    if prompts is None:
        skill_processor.update_airtable_record_log(article.record_id, "No prompts Retrieved")
        print("No prompts found")
        return None
    skill_processor.update_airtable_record_status(article.record_id, "In progress")
    sorted_prompts = sorted(prompts, key=lambda x: x["position"] or float("inf"))

    prompts = skill_processor.process(sorted_prompts, article)
    if prompts is None:
        skill_processor.update_airtable_record_log(article.record_id, "No responses found for prompts")
        print("No responses found")
        return None
    end_time = time.time()
    elapsed_time_bf_at = end_time - start_time
    skill_processor.update_airtable_record(article.record_id, prompts, elapsed_time_bf_at)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


def get_new_job_title(base_source: str='DB1'):
    selected_db = skill_database_selection.get(base_source)
    job_title_table = selected_db.get("jobTileTableID")
    database_id = selected_db.get("baseID")
    airtable_skill_token = os.getenv('AIRTABLE_SKILL_GENERATION_TKN')
    airtable_handler=AirtableHandler(job_title_table, database_id, airtable_skill_token)
    found_job_title = airtable_handler.get_max_records(filter_by_formula=f"AND(FIND('New', {{Status}}), {{JSON}} = '')", max_records=SKILL_NUMBER)
    if not found_job_title or found_job_title[0] is None:
        print("No article found")
        return None
    return found_job_title
    
    
def process_getting_task_response(article: Article, task_id: str, first_retry_after: int = 0):
    url = f"https://api.resumedone-staging.com/v2/task-processor/{task_id}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    airtable_handler = AirtableHandler(data_table)
    airtable_handler.update_record(article.record_id, {
        "fldcTiDTr8BBUNqkk": 'Processing',
    })
    time.sleep(first_retry_after)
    for i in range(1, 30):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    log_message = f'{i}. resume sample for {article.job_name} is loading\n Data: \n{result}'
                    print(log_message)
                    airtable_handler.update_record(article.record_id, {
                        "fldnEZ9uHN8mNJPA8": log_message,
                    })
                    if result.get('status') == 500:
                        airtable_handler.update_record(article.record_id, {
                            "fldcTiDTr8BBUNqkk": 'Error',
                        })
                        break
                    time.sleep(10)
                    continue
                elif isinstance(result, list) and len(result) >= 4:
                    log_message = f'{i}. resume sample for {article.job_name} processed'
                    print(log_message)
                    airtable_handler.update_record(article.record_id, {
                        "fld9lCuvcwKAKEbnz": result,
                        "fldnEZ9uHN8mNJPA8": log_message,
                        "fldcTiDTr8BBUNqkk": 'Completed',
                    })
                    break
                else:
                    log_message = f"{i}. Resume data incomplete \n Data: \n{result}"
                    airtable_handler.update_record(article.record_id, {
                        "fldnEZ9uHN8mNJPA8": log_message,
                        "fldcTiDTr8BBUNqkk": 'Incomplete',
                    })
                    break
            response.raise_for_status()
        except Exception as e:
            error_message = f"An error occurred when getting resume sample data: {e}"
            print(error_message)
            airtable_handler.update_record(article.record_id, {
                "fldnEZ9uHN8mNJPA8": error_message,
                "fldcTiDTr8BBUNqkk": 'Error',
            })
            continue


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


def get_job_skill_prompts(job_name: str):
    type="generate_skill"
    if prompts_cfg.get(type, {}) is None:
        print(f"A prompt for extraction was not found")
        return None
    prompt = prompts_cfg[type].replace("[[job_name]]", job_name)
      
    return [{
        "response": "",
        "section": 'Skill',
        "plain_text": "",
        "prompt": prompt,
        "position": 1,
        "type": "Skill generation"
    }] 


def parse_prompt(record: dict, article: Article):
    prompt_text = record.get("fields").get(f"Prompt {article.language}", "")
    placeholders = re.findall(r'\[(.*?)]', prompt_text)
    for placeholder in placeholders:
        # value_to_replace = record.get("fields").get(placeholder, f"No value for {placeholder}")
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
