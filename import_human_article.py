import json
import os
from typing import Optional

from helpers.airtable_handler import AirtableHandler
from helpers.json_file_handler import JsonFileHandler
from helpers.webflow_handler import WebflowHandler
from models.blog import Blog, BlogCollection

data_table = os.environ.get("TABLE_DATA")
blog_table = os.environ.get("TABLE_BLOG_ID")
log_fld_id = os.environ.get("LOG_IMPORTATION_FLD_ID")


def process_webflow_item_importation(blog: Blog, category: str):
    webflow_handler = WebflowHandler()
    file_container = get_file_handler(blog, category)
    category_collection = switch_collection(blog, category)
    if not category_collection:
        print("Collection Id does not exist")
        update_importation_log(blog=blog, message=f"{category.upper()} collection Id does not exist in params")
        return
    if not file_container.is_file_exist():
        file_container.write_file([])
    for i in range(20):
        offset = 100 * i
        print(f"Offset: {offset}")
        update_importation_log(blog=blog, message=f"Offset: {offset}")
        response = webflow_handler.list_collection_items(collection_id=category_collection.collection_id, offset=offset, limit=100)
        saved_response = file_container.read_file()
        if response:
            items = response.get("items")
            if len(items) > 0:
                for idx, item in enumerate(items):
                    target_id = item.get('id')
                    if item.get('isArchived') is False and item.get('isDraft') is False:
                        found_items = list(filter(lambda elm: elm["id"] == target_id, saved_response))
                        if len(found_items) == 0:
                            webflow_backup_item = remove_unused_keys(item)
                            webflow_backup_item['imported_in_airtable'] = False
                            saved_response.append(webflow_backup_item)
                    items[idx] = {}
                del items
                file_container.write_file(saved_response)
            else:
                break
    update_importation_log(blog=blog, message="Backup updated!!!")
    print('File updated')


def get_file_handler(blog: Blog, category: str) -> JsonFileHandler:
    file_name = blog.blog_name.replace('.com', '')
    file_name = file_name.replace('-', '_')
    file_name = f"{file_name}_{category}"
    file_container = JsonFileHandler(file_name)
    return file_container


def update_list_article_in_airtable(blog: Blog, category: str):
    file_container = get_file_handler(blog, category)
    if file_container.is_file_exist():
        collection_active = switch_collection(blog=blog, category=category)
        if not collection_active:
            print("Collection Id does not exist")
            update_importation_log(blog=blog, message=f"{category.upper()} collection Id does not exist in params")
            return
        web_collection_buckup = file_container.read_file()
        airtable_handler = AirtableHandler(data_table)
        for nbr, webflow_item in enumerate(web_collection_buckup,1):
            try:
                webflow_id = webflow_item.get('id')
                slug = webflow_item.get('slug')
                if webflow_item.get('imported_in_airtable') is True:
                    continue
                msg = f"{category.upper()} Article imported: {nbr}"
                update_importation_log(blog=blog, message=msg)
                print(msg)
                found_articles = airtable_handler.get_records(
                    filter_by_formula=f"FIND(\"{webflow_id}\", {{Webflow ID}})")
                if len(found_articles) == 0:
                    type_category = ""
                    type_category = get_type_category(slug, blog, category)
                    base_url = collection_active.webflow_article_base_url
                    job_name = sanitize_for_job_name(slug, blog)
                    fields = {
                        "fldHYGVGork1UuCps": job_name,  # job name
                        "fldfoXIUinA9zVkBx": blog.blog_name,  # blog
                        "fldlMpB6SUtr99Oq9": type_category,  # type category
                        "fldE2YQXCz5uEbGBn": blog.language_id,  # language
                        "fldsnne20dP9s0nUz": "Human Article",  # status
                        "fldnqhJgjcPzoLP6S": webflow_id,  # webflow id
                        "fld1uAosEiotY3H1u": f"{base_url}{slug}",  # webflow url
                        "fld1mAn4B5pAljLgP": slug,  # slug
                        "fld4fQ1LNyG0BwJ2g": blog.blog_to_webflow_id,  # blog to webflow
                    }
                    airtable_handler.create_record(fields)
                webflow_item['imported_in_airtable'] = True
                file_container.write_file(web_collection_buckup)
            except Exception as e:
                print(str(e))
                break
        update_importation_log(blog=blog, message=f"Article totally imported")
        print('Article totally updated')
    else:
        print('file does not exist')
        update_importation_log(blog=blog, message=f"backup file does not exist")


def remove_unused_keys(item: dict):
    new_item = {'id': item.get('id')}
    for key, value in item['fieldData'].items():
        if key == 'name' or key == 'slug':
            new_item[key] = value
        continue
    return new_item


def switch_collection(blog: Blog, category: str) -> Optional[BlogCollection]:
    if category == 'cv' and blog.cv_collection:
        return blog.cv_collection
    elif category == 'cl' and blog.cover_letter_collection:
        return blog.cover_letter_collection
    elif category == 'job_search' and blog.job_search_collection:
        return blog.job_search_collection
    return None


def get_type_category(slug: str, blog: Blog, category: str):
    key_words = {
        "Entry Level": blog.entry_level_kws,
        "Resume Country": blog.cv_country_kws,
        "Resume in Language": blog.cv_language_kws,
        "Cover Letter in Language": blog.cl_language_kws,
        "Job Interviews": blog.job_itw_kws,
        "Job Search": blog.job_search_kws,
        "Resume Example": blog.resume_example_kws
    }
    for t_category, kywds in key_words.items():
        tc = next((t_category for key in kywds if key in slug), None)
        if tc:
            return tc

    if category == 'cv':
        return "Resume Example"
    if category == 'cl':
        return "Cover Letter"
    if category == 'job_search':
        return "Job Search"


def sanitize_for_job_name(slug: str, blog: Blog):
    kws = [*blog.resume_example_kws, *blog.entry_level_kws, *blog.cv_country_kws, *blog.cv_language_kws,
           *blog.cl_language_kws, *blog.job_itw_kws, *blog.job_search_kws]
    for kw in kws:
        slug = slug.replace(kw, "")
    job_name = slug.replace('-', ' ')
    job_name = job_name.capitalize()
    return job_name


def update_importation_log(blog: Blog, message:str):
    try:
        airtable_handler = AirtableHandler(blog_table)
        fields = {log_fld_id: message}
        airtable_handler.update_record(blog.blog_rec_id, fields)
    except Exception as e:
        print(f"[!!] Error updating Airtable blog table log for record: {str(e)}")