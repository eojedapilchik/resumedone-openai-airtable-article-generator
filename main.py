import os
import time
from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler, OpenAIException
from typing import Optional

app = FastAPI()

load_dotenv()

prompts_table = os.environ.get("TABLE_PROMPTS")
data_table = os.environ.get("TABLE_DATA")
show_debug = os.environ.get("SHOW_DEBUG") == "True"
log_text = ""


class Article(BaseModel):
    job_name: str
    record_id: str
    language: Optional[str]


@app.post("/article-texts/")
async def get_test(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.get("/article-texts/{record_id}/")
async def get_test(background_tasks: BackgroundTasks, record_id: str, job_name: str,
                   language: str):
    if record_id and job_name and language:
        article = Article(record_id=record_id, job_name=job_name, language=language)
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + job_name}
    else:
        return {"status": "missing data"}


@app.get("/health/")
async def health_check():
    return {"status": "alive"}


def process_article(article: Article):
    start_time = time.time()
    prompts = get_prompts(article.language)
    if prompts is None:
        update_airtable_record_log(article.record_id, "No prompts Retrieved")
        print("No prompts found")
        return None
    filtered_prompts = [prompt for prompt in prompts if prompt.get("prompt") is not None]
    parsed_prompts = [
        {**prompt, "prompt": prompt["prompt"].replace("[job_name]", article.job_name)}
        for prompt in filtered_prompts
    ]
    # Sort prompts by position or by infinity if position is not set
    sorted_prompts = sorted(parsed_prompts, key=lambda x: x["position"] or float("inf"))
    responses = process_prompts(sorted_prompts, article.record_id)
    if responses is None:
        update_airtable_record_log(article.record_id, "No responses found for prompts")
        print("No responses found")
        return None

    update_airtable_record_log(article.record_id, "Responses retrieved and sorted")
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
            "section": record.get("fields").get("Section Name"),
            "prompt": record.get("fields").get(f"Prompt {language}"),
            "position": record.get("fields").get("Position"),
            "type": record.get("fields").get("Type", "").lower()
            if record.get("fields").get("Type", "").lower() != "body" else ""
        } for record in records]
        return prompts
    return None


def process_prompts(prompts: list, record_id: str):
    global log_text
    retries = int(os.getenv("OPENAI_RETRIES", 3))
    openai_handler = OpenAIHandler()
    index = 0
    for prompt in prompts:
        index += 1
        for i in range(retries):
            try:
                print(f" - Processing prompt...{index} -> Attempt {i + 1}/{retries}")
                response = openai_handler.prompt(prompt.get("prompt"))
                print(f"[+] Received response from OpenAI {index}")
                update_airtable_record_log(record_id, f"Received response from OpenAI - # {index}")
                prompt_info = f"\n[SECTION {prompt['position']}] \n {prompt['section']} \n[PROMPT] \n " \
                              f"{prompt['prompt']}\n"
                log_text += prompt_info
                if show_debug:
                    print(prompt_info + f"\n\n[RESPONSE] {response}\n\n")
                if prompt["type"] and prompt["type"] != "":
                    prompt["response"] = f"<{prompt['type']}>{response}</{prompt['type']}>\n"
                else:
                    prompt["response"] = f"{response}\n"
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
    return prompts


def update_airtable_record(record_id, responses_list, elapsed_time_bf_at: float = 0):
    global log_text
    print("[+] Updating Airtable record...")
    airtable_handler = AirtableHandler(data_table)
    if len(responses_list) <= 0:
        print("[-] Insufficient responses provided.")
        return None
    responses = [response["response"] for response in responses_list]
    try:
        fields = {
            "fld7vn74uF0ZxQhXe": ''.join(responses),
            "fldus7pUQ61eM1ymY": elapsed_time_bf_at,
            "fldsnne20dP9s0nUz": "Content Generated",
            "fldpnyajPwaBXM6Zb": log_text,
        }
        airtable_handler.update_record(record_id, fields)
        print("[+] Airtable record updated successfully.")
        log_text = ""
    except Exception as e:
        print(f"[!!] Error updating record: {str(e)}")
        print(responses_list)


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

