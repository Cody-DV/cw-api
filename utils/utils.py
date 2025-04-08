import json
from datetime import datetime, date
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def clean_prompt_response(response):
    # Find the first occurrence of '{' and the last occurrence of '}'
    start_index = response.find("{")
    end_index = response.rfind("}")

    # Strip any text before the first '{' and after the last '}'
    if start_index != -1 and end_index != -1:
        response = response[start_index : end_index + 1]

    # Decode the string into proper JSON
    decoded_json = json.loads(response)

    return decoded_json


def convert_dates_to_strings(json_obj):
    """
    Convert all date, datetime, and Decimal objects in a JSON-like dictionary to string format.

    Args:
        json_obj: A dictionary potentially containing date, datetime, and Decimal objects.

    Returns:
        A new dictionary with all date, datetime, and Decimal objects converted to strings.
    """
    if isinstance(json_obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in json_obj.items()}
    elif isinstance(json_obj, list):
        return [convert_dates_to_strings(element) for element in json_obj]
    elif isinstance(json_obj, datetime):
        return json_obj.isoformat()
    elif isinstance(json_obj, date):
        return json_obj.isoformat()
    elif isinstance(json_obj, Decimal):
        return str(json_obj)
    else:
        return json_obj
    

def calculate_age(birth_date):
    if not birth_date:
        return ''
    
    try:
        if isinstance(birth_date, str):
            logging.info(f"Calculating age: {birth_date}")
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, TypeError):
        return ''

    
def calculate_percentage(actual, target):
    """Calculate percentage of actual vs target"""
    if not target or target == 0:
        return 0
    return round((actual / target) * 100)