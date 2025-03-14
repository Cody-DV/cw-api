import json
from flask import Blueprint, jsonify, request, current_app as app

from services.aggregator import get_customer_data, collect_reporting_data
from services.prompt import get_ai_prompt_response
from services.report import generate_pdf_report
from data_access.main import get_patients
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

@routes_bp.route("/generate-report", methods=["GET"])
def generate_report():
    # TODO: Add parameters for customer ID, start date, end date
    # Get customer profile, and transactions in the time window.
    # Map nutrients from food consumed in transactions

    with open("report_generation/mock_report_data.json", "r") as file:
        decoded_json = json.load(file)
    report = generate_pdf_report(decoded_json)

    return jsonify(report)

@routes_bp.route("/clients", methods=["GET"])
def get_clients():
    patients = get_patients()
    print(f"Patients: {patients}")

    return jsonify(patients)