import logging
import json
from flask import Flask, jsonify, request
from data_collection.collector import collect_data
from data_aggregation.aggregator import aggregate_data
from prompting.prompt import prompt
from report_generation.report import generate_pdf_report

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@app.route("/", methods=["GET"])
def status():
    return jsonify(message="API is active")


@app.route("/collect", methods=["POST"])
def collect():
    data = collect_data(request.json)
    return jsonify(data)


@app.route("/aggregate", methods=["POST"])
def aggregate():
    data = aggregate_data(request.json)
    return jsonify(data)


@app.route("/prompt", methods=["GET"])
def prompt_route():
    response = prompt()

    # Decode the string into proper JSON
    decoded_json = json.loads(response)

    # Pretty-print the JSON (optional)
    print(json.dumps(decoded_json, indent=4))

    # log.info(f"Response: {response}")
    return decoded_json


@app.route("/generate-report", methods=["POST"])
def generate_report():
    report = generate_pdf_report(request.json)
    return jsonify(report)


if __name__ == "__main__":
    app.run(debug=True)
