import pytest
from unittest.mock import patch
import json
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_status_route(client):
    """Test status route"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "API is active"


@patch("app.get_ai_prompt_response")
def test_prompt_route(mock_prompt, client):
    """Test prompt route with mock data"""
    mock_response = json.dumps({
        "nutrients": {
            "calories": 1500,
            "fiber": 30,
            "vitamin C": 50,
            "protein": 100,
            "fat": 60
        },
        "notes": {
            "dietary_restrictions": "Diabetes Type 1",
            "allergies": "Peanut",
            "general_summary": "Customer ID: A2E3R-8OJYT"
        }
    })
    mock_prompt.return_value = mock_response

    response = client.get("/prompt")
    assert response.status_code == 200
    assert "nutrients" in response.json
    assert response.json["nutrients"]["calories"] == 1500


@patch("app.generate_pdf_report")
@patch("app.get_ai_prompt_response")
def test_generate_report(mock_get_ai_prompt_response, mock_generate_pdf_report, client):
    """Test generate report endpoint with mock report generation"""
    mock_generate_pdf_report.return_value = {"status": "Report generated", "file": "report.pdf"}
    mock_get_ai_prompt_response.return_value = json.dumps({})
    response = client.get("/generate-report")
    assert response.status_code == 200
    assert response.json["status"] == "Report generated"
    assert response.json["file"] == "report.pdf"
