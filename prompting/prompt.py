import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Mock data
MOCK_DIETARY_DATA = [
    {"food": "apple", "calories": 95, "nutrients": {"fiber": 4.4, "vitamin C": 8.4}},
    {"food": "banana", "calories": 105, "nutrients": {"fiber": 3.1, "vitamin C": 10.3}},
    {
        "food": "chicken breast",
        "calories": 165,
        "nutrients": {"protein": 31, "fat": 3.6}
    }
]
MOCK_ALLERGIES = ["peanuts", "shellfish", "gluten"]
MOCK_RISK_FACTORS = ["high blood pressure", "diabetes", "high cholesterol"]


def prompt():
    data = {
        "dietary_data": MOCK_DIETARY_DATA,
        "allergies": MOCK_ALLERGIES,
        "risk_factors": MOCK_RISK_FACTORS
    }

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "developer",
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
                                    "description": "A general summary of the dietary assessment",
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
