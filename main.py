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


class Article(BaseModel):
    job_name: str
    record_id: str
    language: Optional[str] = 'EN'


@app.post("/article-texts/")
async def get_test(background_tasks: BackgroundTasks, article: Article):
    if article.record_id and article.job_name:
        background_tasks.add_task(process_article, article)
        return {"status": "processing AI generated sections for article: " + article.job_name}
    else:
        return {"status": "missing data"}


@app.get("/article-texts/")
async def get_test(background_tasks: BackgroundTasks, record_id: str = None, job_name: str = None,
                   language: str = 'EN'):
    if record_id and job_name:
        article = Article(record_id=record_id, job_name=job_name)
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
        print("No prompts found")
        return None
    parsed_prompts = [
        {**prompt, "prompt": prompt["prompt"].replace("[job_name]", article.job_name)}
        for prompt in prompts
    ]
    # for prompt in parsed_prompts:
    #     print(prompt)
    #     print("\n\n")
    responses = process_prompts(parsed_prompts)
    if responses is None:
        print("No responses found")
        return None
    sorted_responses = sorted(responses, key=lambda x: x["position"])
    print(sorted_responses)
    update_airtable_record(article.record_id, sorted_responses)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


def get_prompts(language: str = 'EN'):
    airtable_handler = AirtableHandler(prompts_table)
    records = airtable_handler.get_records()
    if records:
        prompts = [{
            "section": record.get("fields").get("Section Name"),
            "prompt": record.get("fields").get(f"Prompt {language}"),
            "position": record.get("fields").get("Position")
        } for record in records]
        return prompts
    return None


def process_prompts(prompts: list):
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
                if show_debug:
                    print(f"\n\n {response} \n\n")
                prompt["response"] = f"\n\n {response}\n\n"
                break
            except OpenAIException as e:
                print("Error: " + str(e))
                if i < retries - 1:  # i is zero indexed
                    time.sleep((2 ** i))  # exponential backoff, sleep for 2^i seconds
                    print(f"Retrying OpenAI request...")
                    continue
                else:
                    print("OpenAI request failed after " + str(retries) + " attempts.")
                    prompt["response"] = f"\n\n *NO CONTENT WAS GENERATED FOR SECTION {prompt['section']}* \n\n"
    return prompts


def update_airtable_record(record_id, responses_list):
    print("[+] Updating Airtable record...")
    airtable_handler = AirtableHandler(data_table)
    if len(responses_list) < 25:
        print("[-] Insufficient responses provided.")
        return None
    responses = [response["response"] for response in responses_list]
    try:
        fields = {
            "fldFsFpm8taTGaBk9": responses[0],
            "fldoUnQPkc8UHzVJd": responses[1],
            "fldqBiG7n5AjEbEhy": responses[2],
            "fldNQFEK8c2eToiCk": responses[3],
            "fld0MC9OQyiUJjqJS": responses[4],
            "fldjt9swf8CqMRhxq": responses[5],
            "fldcHfigokcJByFAY": responses[6],
            "fldcw4Q2TWfMUFawR": responses[7],
            "fldj7O9GYhsvKDQOB": responses[8],
            "fldUlWlpErsxnHSiW": responses[9],
            "fld9WJI4YEEQslt9U": responses[10],
            "fldQKHHlQSkG7KmUf": responses[11],
            "fldKAlyaIPW8bxjNG": responses[12],
            "fldXJgiOEkXfLp32V": responses[13],
            "fldIDvFwq4kLoTX6c": responses[14],
            "fldpqfjWJqzimVSAC": responses[15],
            "fldOhsX1mDSvx8UtR": responses[16],
            "fld7UkEv2wXVGsu5Q": responses[17],
            "fldoTPcyB9aZSHprX": responses[18],
            "fld9P0edvo50PXI6J": responses[19],
            "fldaemLzy1zV1qBq0": responses[20],
            "fld4PaKlF4OyiarbC": responses[21],
            "fldeL1ubpzxaGc2eQ": responses[22],
            "fldM22W6tIrvIjuM7": responses[23],
            "fldrt3niG38mxy4tq": responses[24],
            "fld7vn74uF0ZxQhXe": ''.join(responses)
        }
        airtable_handler.update_record(record_id, fields)
        print("[+] Airtable record updated successfully.")
    except Exception as e:
        print(f"[!!] Error updating record: {str(e)}")
