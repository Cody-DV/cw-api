# routes/routes.py

"""
Routes module for CardWatch Reporting API

Defines all API routes and endpoints for the application
"""
import logging
import os
import json
from flask import Blueprint, jsonify, request, current_app as app
from services.aggregator import collect_reporting_data
from services.dashboard_service import get_dashboard_with_analysis
from services.report_service import generate_patient_report, get_reports_for_patient
from services.chat_service import process_chat_message
from services.js_bridge_service import DateTimeEncoder
from data_access.main import get_patients

# Create Blueprint for all routes
routes_bp = Blueprint("routes", __name__)
logger = logging.getLogger(__name__)


def get_patient_data(patient_id):
    """Helper function to collect patient data."""
    return collect_reporting_data(int(patient_id))

def validate_patient_id(patient_id):
    """Helper function to validate patient ID."""
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    return None

def handle_exception(e, message):
    """Helper function to handle exceptions."""
    app.logger.error(f"{message}: {str(e)}")
    return jsonify({"error": message, "details": str(e)}), 500

@routes_bp.route("/", methods=["GET"])
def status():
    """Health check endpoint"""
    return jsonify(message="CardWatch Reporting API is active")

@routes_bp.route("/clients", methods=["GET"])
def get_clients():
    """Get all clients/patients"""
    patients = get_patients()

    logger.info(f"ROUTES: Retrieved {len(patients)} clients from the database")
    if patients:
        logger.info(f"Sample client data: {patients[0]}")
    else:
        logger.warning("No clients found in the database!")

    return jsonify(patients)

@routes_bp.route("/dashboard-data", methods=["GET"])
def get_dashboard_data():
    """
    Get dashboard data for a specific patient with optional date filtering.
    """
    patient_id = request.args.get('patient_id')
    validation_error = validate_patient_id(patient_id)
    if validation_error:
        return validation_error

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    include_analysis = request.args.get('include_analysis', 'false').lower() == 'true'

    try:
        patient_data = get_patient_data(patient_id)
        result_data = get_dashboard_with_analysis(
            patient_data=patient_data,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            include_analysis=include_analysis,
        )
        logger.info(f"Dashboard data retrieved: {result_data}")
        return jsonify(result_data)
    except Exception as e:
        return handle_exception(e, "Failed to generate dashboard data")


@routes_bp.route("/generate-report", methods=["GET"])
def generate_report():
    """
    Generate a PDF report for a patient.
    """
    patient_id = request.args.get('patient_id')
    validation_error = validate_patient_id(patient_id)
    if validation_error:
        return validation_error

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sections_param = request.args.get('sections')
    include_ai = request.args.get('include_ai', 'true').lower() == 'true'
    sections = [s.strip() for s in sections_param.split(',')] if sections_param else None

    try:
        patient_data = get_patient_data(patient_id)
        report_result = generate_patient_report(
            patient_data,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            sections=sections,
            include_ai=include_ai
        )

        return jsonify(report_result)
    except Exception as e:
        return handle_exception(e, "Failed to generate report")

@routes_bp.route("/get-patient-reports", methods=["GET"])
def get_patient_reports():
    """
    Get a list of previously generated reports for a patient.
    """
    patient_id = request.args.get('patient_id')
    validation_error = validate_patient_id(patient_id)
    if validation_error:
        return validation_error

    try:
        reports = get_reports_for_patient(patient_id)
        logger.info(f"Retrieved {len(reports)} reports for patient {patient_id}")
        return jsonify({"patient_id": patient_id, "reports": reports})
    except Exception as e:
        return handle_exception(e, "Failed to retrieve reports")

@routes_bp.route("/chat", methods=["POST"])
def chat():
    """
    AI chat endpoint for dietitians to ask questions about patient data.
    """
    request_data = request.json
    if not request_data:
        return jsonify({"error": "No request data provided"}), 400

    patient_id = request_data.get('patient_id')
    message = request_data.get('message')
    chat_history = request_data.get('chat_history', [])

    validation_error = validate_patient_id(patient_id)
    if validation_error:
        return validation_error
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        patient_data = get_patient_data(patient_id)
        chat_result = process_chat_message(
            patient_data=patient_data,
            patient_id=patient_id,
            message=message,
            chat_history=chat_history
        )
        return jsonify(chat_result)
    except Exception as e:
        return handle_exception(e, "Failed to process chat message")