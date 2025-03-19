import os
import json
from datetime import datetime
import logging

REPORTS_DIR = "reports"

def ensure_reports_directory():
    """Ensure the reports directory exists."""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        logging.info(f"Created reports directory: {REPORTS_DIR}")

def get_report_filename(patient_id, report_type="nutrition", format="pdf"):
    """Generate a filename for a report based on patient_id and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{patient_id}_{report_type}_{timestamp}.{format}"

def store_report_metadata(patient_id, filename, report_type="nutrition", start_date=None, end_date=None, format="pdf", renderer=None):
    """Store metadata about a generated report."""
    ensure_reports_directory()
    
    metadata_file = os.path.join(REPORTS_DIR, "report_index.json")
    
    # Create or load the existing metadata index
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            reports_index = json.load(f)
    else:
        reports_index = {"reports": []}
    
    # Determine format from filename if not specified
    if not format:
        ext = os.path.splitext(filename)[1].lower()
        format = ext[1:] if ext else "pdf"  # Remove the dot
    
    # Create metadata for the new report
    report_metadata = {
        "patient_id": patient_id,
        "filename": filename,
        "report_type": report_type,
        "format": format,
        "renderer": renderer,
        "generated_at": datetime.now().isoformat(),
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }
    
    # Add to the index
    reports_index["reports"].append(report_metadata)
    
    # Save the updated index
    with open(metadata_file, "w") as f:
        json.dump(reports_index, f, indent=2)
    
    return report_metadata

def get_reports_for_patient(patient_id):
    """Get all reports for a specific patient."""
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