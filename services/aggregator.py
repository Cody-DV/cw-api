import json
import logging
from data_access.main import get_allergies, get_food_transactions, get_nutrient_targets, get_patients


def collect_reporting_data(patient_id):
    patient_data = {}

    # Get patient information
    patient_info = get_patients(patient_id)
    if patient_info:
        patient_data['patient_info'] = patient_info[0]  # Assuming patient_id is unique

    # Get patient allergies
    allergies = get_allergies(patient_id)
    patient_data['allergies'] = allergies

    # Get food transactions for the patient
    food_transactions = get_food_transactions(patient_id)
    patient_data['food_transactions'] = food_transactions

    # Get nutrient targets for the patient
    nutrient_targets = get_nutrient_targets(patient_id)
    patient_data['nutrient_targets'] = nutrient_targets

    return patient_data
