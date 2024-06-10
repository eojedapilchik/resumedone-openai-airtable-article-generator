import json
import os
import re
import time

from helpers.phone_validator_handler import PhoneValidatorHandler


def load_country_code():
    with open("country_code.json", 'r') as file:
        return json.load(file)
    
def revalidate_phone_number(validator: PhoneValidatorHandler,phone: str, country: str):
    country_code = load_country_code().get(country)
    if country_code:
        if phone.startswith('0'):
            phone=phone[1:]
        phone = country_code + phone 
        phone = re.sub(r'\D', '', phone)
        time.sleep(1)
        return validator.get_all_metadata(phone)
    else:
        print('Country name is invalid or not found')
        return {
            'status' : 'error',
            'error_message' : 'Country code not found'
        }