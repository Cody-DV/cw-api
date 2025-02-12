import logging
import json
from flask_cors import CORS
from flask import Flask, jsonify, request
from data_aggregation.aggregator import get_customer_data
from prompting.prompt import get_ai_prompt_response
from report_generation.report import generate_pdf_report

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# Enable CORS for the Flask app
CORS(app)


@app.route("/", methods=["GET"])
def status():
    return jsonify(message="API is active")


@app.route("/prompt", methods=["GET"])
def prompt_route():
    # TODO: Allow various types of prompting to ask for insights on a customer
    # Allow for more features beyond report generation

    customer_data = get_customer_data(1)
    response = get_ai_prompt_response(customer_data)

    # Decode the string into proper JSON
    decoded_json = json.loads(response)

    # Pretty-print the JSON (optional)
    print(json.dumps(decoded_json, indent=4))

    return decoded_json


@app.route("/generate-report", methods=["GET"])
def generate_report():
    # TODO: Add parameters for customer ID, start date, end date
    # Get customer profile, and transactions in the time window.
    # Map nutrients from food consumed in transactions

    customer_data = get_customer_data(1)
    ai_response = json.loads(get_ai_prompt_response(customer_data))
    report = generate_pdf_report(ai_response)

    return jsonify(report)


if __name__ == "__main__":
    app.run(debug=True)
