"""
Report service module

Centralizes all report-related functionality for creating, storing, and retrieving reports.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# from services.dashboard_service import get_dashboard_with_analysis
from data_access.main import get_nutrition_reference
from services.aggregator import filter_transactions
from services.js_bridge_service import generate_html_file, generate_pdf
from services.prompt import get_ai_analysis
from utils.utils import calculate_age, convert_dates_to_strings

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
    
    metadata_file = os.path.join(REPORTS_DIR, "report_index.json")
    
    # Create or load the existing metadata index
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            reports_index = json.load(f)
    else:
        reports_index = {"reports": []}

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

    patient_data = format_report_data(patient_data, start_date, end_date)

    # TODO: This shouldn't call another report generation function, it should only do the ai analysis and append the results to the existing patient data
    if include_ai:
        try:
            logger.info(f"Generating AI analysis for patient {patient_id}...")
            logger.info(f"Patient Data: {patient_data}")

            # Create a reduced context to minimize prompt size
            reduced_patient_data = patient_data.copy()
            reduced_patient_data.pop("food_transactions", None)
            logger.info(f"Reduced patient data for AI analysis: {reduced_patient_data}")

            # Send reduced data to the AI
            analysis_json = get_ai_analysis(reduced_patient_data)
            logger.info(f"AI analysis response for patient {patient_id}: {analysis_json}")

            analysis_data = json.loads(analysis_json)

            # Merge analysis results into the original patient_data
            patient_data["ai_analysis"] = {
                key: analysis_data[key]
                for key in ["SUMMARY", "ANALYSIS", "RECOMMENDATIONS", "HEALTH_INSIGHTS"]
                if key in analysis_data
            }

            logger.info(f"Patient data with AI analysis appended: {patient_data}")
        except Exception as analysis_error:
            logger.error(f"Error generating AI analysis: {str(analysis_error)}")
            patient_data['ai_analysis'] = {
                "SUMMARY": "AI analysis could not be generated at this time.",
                "ANALYSIS": "",
                "RECOMMENDATIONS": "",
                "HEALTH_INSIGHTS": ""
            }

    data = patient_data
    
    # data = get_dashboard_with_analysis(
    #     patient_data=patient_data,
    #     patient_id=patient_id,
    #     start_date=start_date,
    #     end_date=end_date,
    #     include_analysis=include_ai,
    # )

    if 'date_range' not in data:
        data['date_range'] = {}
    
    # Store dates in the data
    data['date_range']['start'] = start_date
    data['date_range']['end'] = end_date
    
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
        generate_pdf(html_path)
        
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
    

def format_report_data(patient_data: Dict[str, Any], start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Format patient data for dashboard display with optional date filtering.
    
    Args:
        patient_data: The raw patient data from database
        start_date: Optional start date for filtering (format: YYYY-MM-DD)
        end_date: Optional end date for filtering (format: YYYY-MM-DD)
        
    Returns:
        Formatted dashboard data dictionary
    """
    
    logger.info(f"Formating patient data: {patient_data}")

    # Extract patient info
    patient_info = patient_data.get('patient_info', {})
    patient_id = patient_info.get('id', 'unknown')
    
    # Extract and format allergies
    allergies = [allergy.get('allergen', '') for allergy in patient_data.get('allergies', [])]
    
    # Extract food transactions
    transactions = patient_data.get('food_transactions', [])
    logger.info(f"Found {len(transactions)} transactions for patient: {patient_id}")
    
    # Get all nutrition references for easier lookup
    nutrition_refs = get_nutrition_reference()
    
    # Create a lookup dictionary with proper type conversion for IDs
    nutrition_ref_dict = {}
    for ref in nutrition_refs:
        try:
            ref_id = int(ref['id'])
            nutrition_ref_dict[ref_id] = ref
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to process nutrition reference ID: {e}")

    # logger.info(f"Nutrition ref dict {nutrition_ref_dict}")

    transactions = filter_transactions(transactions, start_date, end_date)
    
    # Compute total calories and servings
    total_calories = 0
    food_items = []
    
    for transaction in transactions:
        # Try to get nutritional info for this transaction
        try:
            ref_id = int(transaction.get('nutrition_ref_id', 0))
            nutrition_info = nutrition_ref_dict.get(ref_id, {})

            logger.info(nutrition_info)
            
            food_name = nutrition_info.get('food_name', 'Unknown item')
            serving_count = float(transaction.get('serving_count', 1))
            calories_per_serving = float(nutrition_info.get('calories', 0))
            
            transaction_calories = calories_per_serving * serving_count
            total_calories += transaction_calories
            
            # Add to food items list
            food_items.append({
                'name': food_name,
                'quantity': serving_count,
                'calories': calories_per_serving,
                'date': transaction.get('consumption_date', '')
            })
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error processing transaction nutritional data: {e}")
            continue
    
    # Calculate macronutrient targets and actuals
    carbs_actual = 0
    protein_actual = 0
    fat_actual = 0
    fiber_actual = 0

    for t in transactions:
        if 'nutrition_ref_id' in t:
            ref_id = int(t.get('nutrition_ref_id', 0))
            nutrition_info = nutrition_ref_dict.get(ref_id, {})
            serving_count = float(t.get('serving_count', 1))

            carbs_actual += float(nutrition_info.get('carbs_g', 0)) * serving_count
            protein_actual += float(nutrition_info.get('protein_g', 0)) * serving_count
            fat_actual += float(nutrition_info.get('fat_g', 0)) * serving_count
            fiber_actual += float(nutrition_info.get('fiber_g', 0)) * serving_count
    
    # Default targets - these would normally come from a patient's profile
    calorie_target = 2000  # Default value
    carbs_target = 250     # Default value
    protein_target = 50    # Default value
    fat_target = 70        # Default value
    fiber_target = 25      # Default value
    
    # Format the dashboard data
    report_data = {
        'patient': {
            'id': patient_id,
            'name': f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}",
            'age': calculate_age(patient_info.get('date_of_birth')),
            'allergies': allergies
        },
        'nutrients': {
            'calories': {
                'actual': total_calories,
                'target': calorie_target
            },
            'carbs': {
                'actual': carbs_actual,
                'target': carbs_target
            },
            'protein': {
                'actual': protein_actual,
                'target': protein_target
            },
            'fat': {
                'actual': fat_actual,
                'target': fat_target
            },
            'fiber': {
                'actual': fiber_actual,
                'target': fiber_target
            }
        },
        'food_items': food_items,
        'summary': {
            'total_calories': total_calories,
            'total_items_consumed': len(food_items),
            'date_range': {
                'start': start_date or '',
                'end': end_date or ''
            }
        }
    }
    
    return report_data