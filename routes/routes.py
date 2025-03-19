import json
from flask import Blueprint, jsonify, request, current_app as app
from datetime import datetime

from services.aggregator import get_customer_data, collect_reporting_data
from services.prompt import get_ai_prompt_response
from services.dashboard_service import get_dashboard_with_analysis
from services.report_service import generate_patient_report, get_reports_for_patient
from services.chat_service import process_chat_message
from data_access.main import get_patients, get_food_transactions, get_nutrient_targets
from utils.utils import clean_prompt_response

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/", methods=["GET"])
def status():
    return jsonify(message="API is active")

@routes_bp.route("/prompt", methods=["GET"])
def prompt_route():
    # TODO: Allow various types of prompting to ask for insights on a customer
    # Allow for more features beyond report generation

    customer_data = get_customer_data(1)
    prompt_response = get_ai_prompt_response(customer_data)

    response = clean_prompt_response(prompt_response)

    # Pretty-print the JSON
    app.logger.info(json.dumps(response, indent=4))

    return response

@routes_bp.route("/get-report-data", methods=["POST"])
def get_report_data():
    patient_id = request.json.get('patient_id')
    
    response = collect_reporting_data(patient_id)
    app.logger.info(response)

    return jsonify(response)

@routes_bp.route("/dashboard-data", methods=["GET"])
def get_dashboard_data():
    """
    Get dashboard data for a specific patient with optional date filtering.
    Query parameters:
    - patient_id: ID of the patient (required)
    - start_date: Start date for filtering data (optional, format: YYYY-MM-DD)
    - end_date: End date for filtering data (optional, format: YYYY-MM-DD)
    - include_analysis: Whether to include AI analysis (optional, default=false)
    """
    patient_id = request.args.get('patient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    include_analysis = request.args.get('include_analysis', 'false').lower() == 'true'
    
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    
    try:
        # Collect all patient data
        patient_data = collect_reporting_data(int(patient_id))
        
        # Get dashboard data with optional analysis from service
        dashboard_data = get_dashboard_with_analysis(
            patient_data=patient_data,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            include_analysis=include_analysis
        )
        
        # Log the final dashboard data
        app.logger.info(f"Final dashboard food items: {len(dashboard_data.get('food_items', []))} items")
        app.logger.info(f"Final dashboard nutrients: {list(dashboard_data.get('nutrients', {}).keys())}")
        
        return jsonify(dashboard_data)
    except Exception as e:
        app.logger.error(f"Error generating dashboard data: {str(e)}")
        return jsonify({"error": "Failed to generate dashboard data"}), 500


@routes_bp.route("/generate-report", methods=["GET"])
def generate_report():
    """
    Generate a PDF report for a patient with optional parameters.
    Query parameters:
    - patient_id: ID of the patient (required)
    - start_date: Start date for report period (optional, format: YYYY-MM-DD)
    - end_date: End date for report period (optional, format: YYYY-MM-DD)
    - sections: Comma-separated list of sections to include (optional)
    - include_ai: Whether to include AI analysis (optional, default=true)
    """
    patient_id = request.args.get('patient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sections_param = request.args.get('sections')
    include_ai = request.args.get('include_ai', 'true').lower() == 'true'
    
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
        
    # Parse sections if provided
    sections = None
    if sections_param:
        sections = [s.strip() for s in sections_param.split(',')]
    
    app.logger.info(f"Generating report for patient {patient_id} from {start_date} to {end_date}")
    app.logger.info(f"Sections: {sections}, Include AI: {include_ai}")
    
    try:
        # Collect patient data
        patient_data = collect_reporting_data(int(patient_id))
        
        # Use report generator service to create the report
        report_result = generate_patient_report(
            patient_data,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            sections=sections,
            include_ai=include_ai
        )
        
        # Check if report generation was successful
        if report_result.get("status") == "Error":
            app.logger.error(f"Report generation failed: {report_result.get('error')}")
            return jsonify({"error": "Failed to generate report", "details": report_result.get('error')}), 500
            
        app.logger.info(f"Report generated successfully: {report_result.get('file')}")
        
        return jsonify(report_result)
    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": "Failed to generate report", "details": str(e)}), 500


@routes_bp.route("/get-patient-reports", methods=["GET"])
def get_patient_reports():
    """
    Get a list of previously generated reports for a patient.
    Query parameters:
    - patient_id: ID of the patient (required)
    """
    patient_id = request.args.get('patient_id')
    
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    
    try:
        reports = get_reports_for_patient(patient_id)
        return jsonify({"patient_id": patient_id, "reports": reports})
    except Exception as e:
        app.logger.error(f"Error retrieving reports: {str(e)}")
        return jsonify({"error": "Failed to retrieve reports"}), 500

@routes_bp.route("/clients", methods=["GET"])
def get_clients():
    patients = get_patients()
    print(f"Patients: {patients}")

    return jsonify(patients)

@routes_bp.route("/chat", methods=["POST"])
def chat():
    """
    AI chat endpoint for dietitians to ask questions about patient data.
    
    Request body:
    - patient_id: ID of the patient (required)
    - message: The dietitian's question or message (required)
    - chat_history: Optional array of previous messages in the conversation
    
    Returns:
    - response: The AI's response to the message
    - chat_history: Updated chat history including the new message and response
    """
    # Get request data
    request_data = request.json
    
    if not request_data:
        return jsonify({"error": "No request data provided"}), 400
    
    patient_id = request_data.get('patient_id')
    message = request_data.get('message')
    chat_history = request_data.get('chat_history', [])
    
    # Validate required fields
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        # Get patient data for context
        patient_data = collect_reporting_data(int(patient_id))
        
        # Process the chat message using the chat service
        chat_result = process_chat_message(
            patient_data=patient_data,
            patient_id=patient_id,
            message=message,
            chat_history=chat_history
        )
        
        app.logger.info(f"Chat response processed successfully")
        
        # Return the response and updated chat history
        return jsonify(chat_result)
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Failed to process chat message", 
            "details": str(e)
        }), 500