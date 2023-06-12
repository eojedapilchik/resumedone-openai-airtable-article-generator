import os
import time

from dotenv import load_dotenv
from helpers.airtable_handler import AirtableHandler
from helpers.openai_handler import OpenAIHandler
import requests
from bs4 import BeautifulSoup

load_dotenv()


def main():
    at_token = os.environ.get("AIRTABLE_PAT_SEO_WK")
    airtable_handler = AirtableHandler("tblSwYjjy85nHa6yd", "appkwM6hcso08YF3I", at_token)
    published_en_fr_articles = airtable_handler.get_all_records(view="viwCYqMpgvSDQMP8B")
    print(len(published_en_fr_articles))
    openai_handler = OpenAIHandler("text-davinci-003")
    for article in published_en_fr_articles[0:5]:
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
        time.sleep(10)
        print(response+"\n\n")


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


if __name__ == '__main__':
    main()
