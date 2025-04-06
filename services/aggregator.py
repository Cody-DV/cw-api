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


# def get_nutrient_totals(patient_data):
#     """
#     {"patient": 
#     {"id": 1, "name": "John Doe", "age": 45, "allergies": ["Peanuts", "Shellfish"]}, 
#     "nutrients": {
#         "calories": {"actual": 347.0, "target": 2000}, 
#         "carbs": {"actual": 42.0, "target": 250}, 
#         "protein": {"actual": 33.96, "target": 50}, 
#         "fat": {"actual": 4.07, "target": 70}, 
#         "fiber": {"actual": 2.8, "target": 25}}, 
#         "food_items": [
#             {"name": "Apple, raw", "quantity": 1.0, "calories": 52.0, "date": "2025-02-01"}, 
#             {"name": "Chicken Breast, roasted", "quantity": 1.0, "calories": 165.0, "date": "2025-02-01"}, 
#             {"name": "Rice, white, cooked", "quantity": 1.0, "calories": 130.0, "date": "2025-02-02"}], 
#         "summary": {"total_calories": 347.0, "total_items_consumed": 3, "date_range": {"start": "2023-03-01", "end": "2025-03-25"}}, 
#         "ai_analysis": {"SUMMARY": "John Doe's current dietary intake shows a varied consumption pattern with specific nutrient targets. His severe allergy to peanuts and moderate allergy to shellfish necessitate careful dietary planning to avoid these allergens.", "ANALYSIS": "The available food transaction data is limited, making it difficult to comprehensively analyze John's nutrient intake against his targets. However, based on the targets provided, John should aim for 2000 calories, 60g protein, 70g fat, 250g carbohydrates, 25g fiber, and 2300mg sodium daily. Additionally, his vitamin C target is 75mg. Without detailed nutrient data from the food transactions, it's unclear how his actual intake compares to these targets.", "RECOMMENDATIONS": "John should focus on consuming a balanced diet that meets his nutrient targets while avoiding peanuts and shellfish. Incorporating a variety of fruits, vegetables, lean proteins, and whole grains can help meet his vitamin C, fiber, and overall nutrient needs. Monitoring his intake through a food diary or app could provide more precise insights into his nutritional status.", "HEALTH_INSIGHTS": "John's severe peanut allergy requires vigilance to prevent exposure, which could lead to life-threatening reactions. His moderate shellfish allergy also necessitates caution, particularly in dining out and consuming processed foods. Ensuring adequate nutrient intake while avoiding allergens is crucial for maintaining his overall health and preventing allergic reactions."}, 
#         "date_range": {"start": "2023-03-01", "end": "2025-03-25"}
#     }
#     """
#     """
#     Format patient data for dashboard display with optional date filtering.
    
#     Args:
#         patient_data: The raw patient data from database
#         start_date: Optional start date for filtering (format: YYYY-MM-DD)
#         end_date: Optional end date for filtering (format: YYYY-MM-DD)
        
#     Returns:
#         Formatted dashboard data dictionary
#     """
    
#     # Extract patient info
#     patient_info = patient_data.get('patient_info', {})
#     patient_id = patient_info.get('id', 'unknown')
    
#     # Extract and format allergies
#     allergies = [allergy.get('allergen', '') for allergy in patient_data.get('allergies', [])]
    
#     # Extract food transactions
#     transactions = patient_data.get('food_transactions', [])
#     logger.info(f"Found {len(transactions)} transactions for patient: {patient_id}")
    
#     # Get all nutrition references for easier lookup
#     nutrition_refs = get_nutrition_reference()
    
#     # Create a lookup dictionary with proper type conversion for IDs
#     nutrition_ref_dict = {}
#     for ref in nutrition_refs:
#         try:
#             ref_id = int(ref['id'])
#             nutrition_ref_dict[ref_id] = ref
#         except (ValueError, TypeError) as e:
#             logger.error(f"Failed to process nutrition reference ID: {e}")

#     logger.info(f"Nutrition ref dict {nutrition_ref_dict}")

#     transactions = filter_transactions(transactions, start_date, end_date)
    
    
#     # Compute total calories and servings
#     total_calories = 0
#     food_items = []
    
#     for transaction in transactions:
#         # Try to get nutritional info for this transaction
#         try:
#             ref_id = int(transaction.get('nutrition_ref_id', 0))
#             nutrition_info = nutrition_ref_dict.get(ref_id, {})

#             logger.info(nutrition_info)
            
#             food_name = nutrition_info.get('food_name', 'Unknown item')
#             serving_count = float(transaction.get('serving_count', 1))
#             calories_per_serving = float(nutrition_info.get('calories', 0))
            
#             transaction_calories = calories_per_serving * serving_count
#             total_calories += transaction_calories
            
#             # Add to food items list
#             food_items.append({
#                 'name': food_name,
#                 'quantity': serving_count,
#                 'calories': calories_per_serving,
#                 'date': transaction.get('consumption_date', '')
#             })
#         except (ValueError, TypeError, KeyError) as e:
#             logger.error(f"Error processing transaction nutritional data: {e}")
#             continue
    
#     # Calculate macronutrient targets and actuals
#     carbs_actual = 0
#     protein_actual = 0
#     fat_actual = 0
#     fiber_actual = 0

#     for t in transactions:
#         if 'nutrition_ref_id' in t:
#             ref_id = int(t.get('nutrition_ref_id', 0))
#             nutrition_info = nutrition_ref_dict.get(ref_id, {})
#             serving_count = float(t.get('serving_count', 1))

#             carbs_actual += float(nutrition_info.get('carbs_g', 0)) * serving_count
#             protein_actual += float(nutrition_info.get('protein_g', 0)) * serving_count
#             fat_actual += float(nutrition_info.get('fat_g', 0)) * serving_count
#             fiber_actual += float(nutrition_info.get('fiber_g', 0)) * serving_count
    
#     # Default targets - these would normally come from a patient's profile
#     calorie_target = 2000  # Default value
#     carbs_target = 250     # Default value
#     protein_target = 50    # Default value
#     fat_target = 70        # Default value
#     fiber_target = 25      # Default value
    
#     # Format the dashboard data
#     dashboard_data = {
#         'patient': {
#             'id': patient_id,
#             'name': f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}",
#             'age': calculate_age(patient_info.get('date_of_birth')),
#             'allergies': allergies
#         },
#         'nutrients': {
#             'calories': {
#                 'actual': total_calories,
#                 'target': calorie_target
#             },
#             'carbs': {
#                 'actual': carbs_actual,
#                 'target': carbs_target
#             },
#             'protein': {
#                 'actual': protein_actual,
#                 'target': protein_target
#             },
#             'fat': {
#                 'actual': fat_actual,
#                 'target': fat_target
#             },
#             'fiber': {
#                 'actual': fiber_actual,
#                 'target': fiber_target
#             }
#         },
#         'food_items': food_items,
#         'summary': {
#             'total_calories': total_calories,
#             'total_items_consumed': len(food_items),
#             'date_range': {
#                 'start': start_date or '',
#                 'end': end_date or ''
#             }
#         }
#     }
    
#     return dashboard_data