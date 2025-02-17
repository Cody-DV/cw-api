import pytest
import json
from unittest.mock import patch, MagicMock
from prompting.prompt import get_ai_prompt_response


@patch("prompting.prompt.azure_openai")
def test_prompt(mock_client):
    """Test prompt function with a mocked client"""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "nutrients": {
                            "calories": 1500,
                            "fiber": 30,
                            "vitamin C": 50,
                            "protein": 100,
                            "fat": 60,
                        },
                        "notes": {
                            "dietary_restrictions": "Diabetes Type 1",
                            "allergies": "Peanut",
                            "general_summary": "Customer ID: A2E3R-8OJYT",
                        },
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response
    data = {"sample": "test data"}
    result = get_ai_prompt_response(data)
    result_json = json.loads(result)
    assert result_json["nutrients"]["calories"] == 1500
    assert result_json["notes"]["allergies"] == "Peanut"
