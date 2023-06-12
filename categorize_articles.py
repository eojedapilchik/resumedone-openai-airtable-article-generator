import os
import time
import re
import requests
from dotenv import load_dotenv
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler
from bs4 import BeautifulSoup

load_dotenv()


def main():
    start_time = time.time()
    at_token = os.environ.get("AIRTABLE_PAT_SEO_WK")
    airtable_handler = AirtableHandler("tblSwYjjy85nHa6yd", "appkwM6hcso08YF3I", at_token)
    published_en_fr_articles = airtable_handler.get_all_records(view="viwCYqMpgvSDQMP8B", max_records=100)
    print(len(published_en_fr_articles))
    openai_handler = OpenAIHandler("text-davinci-003")
    update_records = []
    total = len(published_en_fr_articles)
    i = 0
    for article in published_en_fr_articles:
        i += 1
        article_name = article.get("fields").get("Title")
        url = article.get("fields").get("URL")
        print(f"Article Name: {article_name}")
        # print(f"URL: {url}")
        title_tag, meta_description = get_title_and_meta_description(url)
        print(f"Title Tag: {title_tag}")
        response = openai_handler.prompt(f"Categorize a blog post with this name: {article_name} and Title Tag: "
                                         f"{title_tag} according to one of the following 18 categories - do not add any"
                                         f" other text to the response, just the category name-: "
                                         f"Accounting and Finance, Administrative,"
                                         f"Creative and Cultural, Engineering, Food & Catering, Information Technology,"
                                         f"Maintenance & Repair, Marketing, Medical, Other, Retail, Sales, Social Work,"
                                         f"Sport & Fitness, Transport & Logistics, Industry, Public Safety and Defense, "
                                         f"Education")
        category = extract_word(response)
        if category:
            print(f"Category: |{category}|")
            update_records.append({"id": article.get("id"), "fields": {"fldfuuMpUoLq5r4Hk": category}})
            print(f"[+] Processed article: {i} / {total} \n\n")
            time.sleep(5)

        if i % 10 == 0:
            airtable_handler.update_records_batch(update_records)
            update_records = []

    if len(update_records) > 0:
        airtable_handler.update_records_batch(update_records)

    print(f"Took {time.time() - start_time} seconds to process {total} articles")


def get_title_and_meta_description(url):
    try:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        title_tag = soup.title.string if soup.title else None

        meta_description = None
        meta_tags = soup.find_all('meta', attrs={'name': 'description'})
        if meta_tags:
            meta_description = meta_tags[0]['content']

        return title_tag, meta_description
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


def extract_word(text):
    keywords = [
        'Accounting and Finance', 'Administrative', 'Creative and Cultural', 'Engineering',
        'Food & Catering', 'Information Technology', 'Maintenance & Repair', 'Marketing',
        'Medical', 'Other', 'Retail', 'Sales', 'Social Work', 'Sport & Fitness',
        'Transport & Logistics', 'Industry', 'Public Safety and Defense', 'Education'
    ]

    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, keywords)))
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(0)
    else:
        return None


if __name__ == '__main__':
    main()
