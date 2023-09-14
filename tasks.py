from helpers.lemlist_handler import LemlistHandler
from celery import Celery

celery_instance = Celery('lemlist_campaign_generator')
celery_instance.config_from_object('celery_config')


@celery_instance.task(bind=True)
def add_contacts_to_campaigns(campaign_id: str, contacts_data: list, api_key: str):
    responses = []
    handler = LemlistHandler(api_key)
    for contact_data in contacts_data:
        response = handler.add_contact_to_campaign(campaign_id, contact_data)
        responses.append(response)
