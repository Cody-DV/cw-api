import os
import sys

from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()

endpoint = os.getenv("AZUREAI_ENDPOINT_URL", "https://cardwatch-reporting-ai.openai.azure.com/")
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

    response = azure_openai.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "Given some dietary data you generate a report summarizing the user's caloric and \
                            nutritional intake. Assess if they are at risk of common dietary concerns based on \
                            their allergies and risk factors.",
            },
            {"role": "user", "content": str(data)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "report_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "nutrients": {
                            "description": "The total nutrients intake",
                            "type": "object",
                            "properties": {
                                "calories": {
                                    "description": "The sum of caloric intake",
                                    "type": "number"
                                },
                                "fiber": {
                                    "description": "Total fiber intake",
                                    "type": "number"
                                },
                                "vitamin C": {
                                    "description": "Total vitamin C intake",
                                    "type": "number"
                                },
                                "protein": {
                                    "description": "Total protein intake",
                                    "type": "number"
                                },
                                "fat": {
                                    "description": "Total fat intake",
                                    "type": "number"
                                }
                            }
                        },
                        "notes": {
                            "description": "Dietary notes",
                            "type": "object",
                            "properties": {
                                "dietary_restrictions": {
                                    "description": "Details on dietary restrictions",
                                    "type": "string"
                                },
                                "allergies": {
                                    "description": "Information on allergies",
                                    "type": "string"
                                },
                                "general_summary": {
                                    "description": "A general summary of the dietary assessment \
                                        and the customers overall health profile. Also show their customer ID",
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
    )

    return response.choices[0].message.content
