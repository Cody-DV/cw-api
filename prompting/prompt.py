import os
import sys

from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()

endpoint = os.getenv(
    "AZUREAI_ENDPOINT_URL", "https://cardwatch-reporting-ai.openai.azure.com/"
)
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

azure_openai = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-10-01-preview",
)


def get_ai_prompt_response(data):
    # TODO: Lower temperature on AI model to make results more consistant
    # Create another function for general prompting

    with open("prompting/templates/response_format.json", "r") as f:
        response_format = f.read()

    response_format_str = str(response_format)

    response = azure_openai.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": f"Given some dietary data you generate a report summarizing the user's caloric and \
                            nutritional intake. Assess if they are at risk of common dietary concerns based on \
                            their allergies and risk factors. The response should only contain a json object following the \
                            format of the template provided below. Replace all placeholder values with data gathered from the \
                            data provided by the user. If no data is available, replace empty fields with 'na' \
                            and ensure valid json in the response. Template: {response_format_str}",
            },
            {"role": "user", "content": str(data)},
        ],
    )

    return response.choices[0].message.content
