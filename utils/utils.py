import json


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