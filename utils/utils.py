import json
import datetime
from decimal import Decimal
import datetime


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
    elif isinstance(json_obj, datetime.datetime):
        return json_obj.isoformat()
    elif isinstance(json_obj, datetime.date):
        return json_obj.isoformat()
    elif isinstance(json_obj, Decimal):
        return str(json_obj)
    else:
        return json_obj