from report_generation.report import generate_pdf_report


def test_generate_pdf_report():
    """Test PDF report generation logic"""
    input_data = {
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
    }
    result = generate_pdf_report(input_data)
    assert result["status"] == "Report generated"
    assert result["file"] == "report.pdf"
