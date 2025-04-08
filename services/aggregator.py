from datetime import datetime, date
import logging
from data_access.main import get_allergies, get_food_transactions, get_nutrient_targets, get_nutrition_reference, get_patients
from utils.utils import calculate_age, convert_dates_to_strings


logger = logging.getLogger(__name__)

def collect_reporting_data(patient_id):
    patient_data = {}

    # Get patient information
    patient_info = get_patients(patient_id)
    if patient_info:
        patient_data['patient_info'] = patient_info[0]  # Assuming patient_id is unique

    # Get patient allergies
    allergies = get_allergies(patient_id)
    patient_data['allergies'] = allergies

    # TODO: Split transactions into a separate function for performance
    # Get food transactions for the patient
    food_transactions = get_food_transactions(patient_id)
    patient_data['food_transactions'] = food_transactions

    # Get nutrient targets for the patient
    nutrient_targets = get_nutrient_targets(patient_id)
    patient_data['nutrient_targets'] = nutrient_targets

    patient_data = convert_dates_to_strings(patient_data)

    return patient_data


def filter_transactions(transactions, start_date, end_date):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        logger.info(f"Filtering transactions by date: {start_date_obj} to {end_date_obj}")
        
        filtered_transactions = []
        for transaction in transactions:
            if 'consumption_date' in transaction:
                try:
                    # Handle both string and date object types for consumption_date
                    transaction_date = transaction['consumption_date']
                    if isinstance(transaction_date, str):
                        transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                    
                    # Include transactions that are within the date range
                    if start_date_obj <= transaction_date <= end_date_obj:
                        filtered_transactions.append(transaction)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error processing transaction date: {e}")
                    continue
        
        # Replace the original transactions list with filtered one
        transactions = filtered_transactions
        logger.info(f"After date filtering: {len(transactions)} transactions remain")
        return transactions
    except (ValueError, TypeError) as date_error:
        logger.error(f"Date filtering error: {date_error}")

