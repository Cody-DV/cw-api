"""
Dashboard service module

Centralizes all dashboard-related functionality with a focus on data formatting and unified interfaces.
"""
import json
import logging
from datetime import datetime, date
import os
from typing import Dict, Any, Optional

from services.prompt import get_dashboard_analysis
from data_access.main import get_nutrition_reference
from utils.utils import convert_dates_to_strings

logger = logging.getLogger(__name__)


def calculate_age(birth_date):
    """
    Calculate age from birthdate
    
    Args:
        birth_date: Date of birth as string ('YYYY-MM-DD') or date object
        
    Returns:
        Age as an integer, or empty string if calculation fails
    """
    if not birth_date:
        return ''
    
    try:
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, TypeError):
        return ''

def format_dashboard_data(patient_data: Dict[str, Any], start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Format patient data for dashboard display with optional date filtering.
    
    Args:
        patient_data: The raw patient data from database
        start_date: Optional start date for filtering (format: YYYY-MM-DD)
        end_date: Optional end date for filtering (format: YYYY-MM-DD)
        
    Returns:
        Formatted dashboard data dictionary
    """
    
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

    logger.info(f"Nutrition ref dict {nutrition_ref_dict}")
    
    # Filter transactions by date if start_date and end_date are provided
    if start_date and end_date:
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
        except (ValueError, TypeError) as date_error:
            logger.error(f"Date filtering error: {date_error}")
    
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
    dashboard_data = {
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
    
    return dashboard_data


def calculate_percentage(actual, target):
    """Calculate percentage of actual vs target"""
    if not target or target == 0:
        return 0
    return round((actual / target) * 100)

def get_dashboard_with_analysis(
    patient_data: Dict[str, Any], 
    patient_id: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    include_analysis: bool = False, 
) -> Dict[str, Any]:
    """
    Get formatted dashboard data with optional AI analysis
    
    Args:
        patient_data: Raw patient data
        patient_id: Patient identifier
        start_date: Optional start date for filtering (format: YYYY-MM-DD)
        end_date: Optional end date for filtering (format: YYYY-MM-DD)
        include_analysis: Whether to include AI analysis
        
    Returns:
        Formatted dashboard data dictionary)
    """
    data_directory = 'data_storage'  # Directory where JSON files are stored
    os.makedirs(data_directory, exist_ok=True)

    logger.info(f"Generating dashboard data for patient {patient_id} from {start_date} to {end_date}")
    logger.info(type(start_date))

    file_path = os.path.join(data_directory, f'{patient_id}_{start_date}_{end_date}.json')
    
    # Check if the data already exists
    if not os.path.exists(file_path):
        # Format data for dashboard display
        dashboard_data = format_dashboard_data(patient_data, start_date, end_date)

        logger.info(f"get_dashboard_with_analysis: {dashboard_data}")
        
        # Add AI-generated analysis if requested
        if include_analysis:
            try:
                logger.info(f"Generating AI analysis for patient {patient_id}...")
                
                # Generate analysis and parse JSON response
                analysis_json = get_dashboard_analysis(patient_data)
                analysis_data = json.loads(analysis_json)
                
                # Add analysis to dashboard data
                dashboard_data['ai_analysis'] = analysis_data
                logger.info("AI analysis successfully generated and added to dashboard data")
            except Exception as analysis_error:
                logger.error(f"Error generating AI analysis: {str(analysis_error)}")
                dashboard_data['ai_analysis'] = {
                    "SUMMARY": "AI analysis could not be generated at this time.",
                    "ANALYSIS": "",
                    "RECOMMENDATIONS": "",
                    "HEALTH_INSIGHTS": ""
                }
        with open(file_path, 'w') as file:
            logger.info(f"Saving dashboard data to {file_path}")
            json.dump(dashboard_data, file)

    elif os.path.exists(file_path):
        logger.info(f"Dashboard data already exists for patient {patient_id} from {start_date} to {end_date}. Loading from file.")
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {'message': 'Data not found.'}, 404

    logger.info(f"Dashboard data prepared for patient {patient_id} with {len(dashboard_data.get('food_items', []))} food items")
    return dashboard_data