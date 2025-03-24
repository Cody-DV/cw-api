"""
Report service module

Centralizes all report-related functionality for creating, storing, and retrieving reports.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from services.dashboard_service import get_dashboard_with_analysis
from services.js_bridge_service import generate_html_file, generate_pdf

# Define constants
REPORTS_DIR = "reports"

logger = logging.getLogger(__name__)

# Report section options - used for customizing report content
REPORT_SECTIONS = {
    "calories": "Caloric Intake",
    "macronutrients": "Macronutrient Distribution",
    "food_consumed": "Food Items Consumed",
    "food_group_recommendations": "Food Group Recommendations",
    "nutrient_intake": "Detailed Nutrient Intake",
    "summary": "Nutrition Summary",
    "ai_analysis": "AI Nutritional Analysis"
}

def ensure_reports_directory():
    """Ensure the reports directory exists."""
    try:
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR)
            logger.info(f"Created reports directory: {REPORTS_DIR}")
    except Exception as e:
        logger.error(f"Failed to create reports directory: {str(e)}")
        raise

def get_report_filename(patient_id, report_type="nutrition", format="pdf"):
    """
    Generate a filename for a report based on patient_id and timestamp.
    
    Args:
        patient_id: ID of the patient
        report_type: Type of report
        format: File format extension
        
    Returns:
        String filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{patient_id}_{report_type}_{timestamp}.{format}"

def store_report_metadata(patient_id, filename, report_type="nutrition", start_date=None, end_date=None, format="pdf"):
    """
    Store metadata about a generated report.
    
    Args:
        patient_id: ID of the patient
        filename: Name of the report file
        report_type: Type of report
        start_date: Start date of report period
        end_date: End date of report period
        format: File format
        
    Returns:
        Report metadata dictionary
    """

    # logger.info(f"Trying ensure reports directory")
    # ensure_reports_directory()
    
    metadata_file = os.path.join(REPORTS_DIR, "report_index.json")
    
    # Create or load the existing metadata index
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            reports_index = json.load(f)
    else:
        reports_index = {"reports": []}

    logger.info(f"Trying datetime NOW()")
    logger.info(datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    logger.info(f"Report metadata before storing: patient_id={patient_id}, \
                filename={filename}, report_type={report_type}, format={format}, \
                generated_at={datetime.now().strftime("%Y%m%d_%H%M%S")}, start_date={start_date}, \
                end_date={end_date}")

    # Create metadata for the new report
    report_metadata = {
        "patient_id": patient_id,
        "filename": filename,
        "report_type": report_type,
        "format": format,
        "generated_at": datetime.now().strftime('%Y%m%d_%H%M%S'),
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }
    logger.info(f"Storing report metadata: {report_metadata}")
    
    # Add to the index
    reports_index["reports"].append(report_metadata)
    
    # Save the updated index
    with open(metadata_file, "w") as f:
        json.dump(reports_index, f, indent=2)
    
    return report_metadata

def get_reports_for_patient(patient_id):
    """
    Get all reports for a specific patient.
    
    Args:
        patient_id: ID of the patient
        
    Returns:
        List of report metadata dictionaries
    """
    metadata_file = os.path.join(REPORTS_DIR, "report_index.json")
    
    if not os.path.exists(metadata_file):
        return []
    
    with open(metadata_file, "r") as f:
        reports_index = json.load(f)
    
    # Filter reports for the specified patient
    patient_reports = [
        report for report in reports_index.get("reports", [])
        if str(report.get("patient_id")) == str(patient_id)
    ]
    
    # Sort by generated_at date (newest first)
    patient_reports.sort(
        key=lambda x: x.get("generated_at", ""), 
        reverse=True
    )
    
    return patient_reports

def generate_patient_report(
    patient_data: Dict[str, Any], 
    patient_id: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    sections: Optional[List[str]] = None, 
    include_ai: bool = True
) -> Dict[str, Any]:
    """
    Generate a PDF report for a patient.
    
    Args:
        patient_data: Patient data dictionary
        patient_id: ID of the patient
        start_date: Start date for report period (format: YYYY-MM-DD)
        end_date: End date for report period (format: YYYY-MM-DD)
        sections: List of sections to include
        include_ai: Whether to include AI analysis (default=True)
        
    Returns:
        Dictionary with report status and file information
    """
    logger = logging.getLogger(__name__)
    
    # Get unified dashboard data with analysis
    data = get_dashboard_with_analysis(
        patient_data=patient_data,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        include_analysis=include_ai,
    )

    if 'date_range' not in data:
        data['date_range'] = {}
    
    # Store dates in the data
    data['date_range']['start'] = start_date
    data['date_range']['end'] = end_date
    
    # Set up the report directory
    # ensure_reports_directory()
    
    # Generate filename
    if patient_id:
        filename = get_report_filename(patient_id, format="pdf")
    else:
        filename = f"nutrition_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Set up file paths
    pdf_path = os.path.join(REPORTS_DIR, filename)
    html_path = os.path.join(REPORTS_DIR, f"{os.path.splitext(filename)[0]}.html")
    
    try:
        # Generate HTML version
        logger.info("Generating HTML report")
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "js", "templates", "report-template.html"
        )
        
        generate_html_file(
            data=data,
            output_html_path=html_path,
            template_path=template_path
        )
        logger.info(f"HTML report created at {html_path}")
        
        # Generate PDF
        logger.info("Generating PDF")
        generate_pdf(
            data=data,
            output_path=pdf_path,
            template_path=template_path
        )
        logger.info(f"PDF created at {pdf_path}")

        # Store metadata
        if patient_id:
            logger.info("Storing report metadata")
            logger.info(f"Storing report metadata with inputs: patient_id={patient_id}, filename={filename}, report_type='nutrition', start_date={start_date}, end_date={end_date}, format='pdf'")
            metadata = store_report_metadata(
                patient_id, 
                filename, 
                "nutrition", 
                start_date, 
                end_date,
                format="pdf"
            )
            logger.info(f"Metadata stored successfully: {metadata}")

        # # Return response
        response = {
            "status": "Report generated",
            "file": filename,
            "path": pdf_path,
            "html_path": html_path,
            "format": "pdf",
            "sections_included": sections,
        }

        logger.info(f"Returning response: {response}")
        return response
    
    
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        
        # If HTML generation succeeded but PDF failed
        if os.path.exists(html_path):
            logger.info(f"PDF generation failed but HTML was created at {html_path}")
            
            # Store metadata for HTML report
            if patient_id:
                metadata = store_report_metadata(
                    patient_id, 
                    os.path.basename(html_path), 
                    "nutrition", 
                    start_date, 
                    end_date,
                    format="html"
                )
            
            return {
                "status": "HTML report generated (PDF failed)",
                "file": os.path.basename(html_path),
                "path": html_path,
                "format": "html",
                "sections_included": sections,
                "error": str(e)
            }
        
        # Both HTML and PDF generation failed
        raise RuntimeError(f"Report generation failed: {str(e)}")