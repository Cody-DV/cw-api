"""
Dashboard service module

Centralizes all dashboard-related functionality with a focus on data formatting and unified interfaces.
"""
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional

from services.prompt import get_dashboard_analysis
from data_access.main import get_nutrition_reference

logger = logging.getLogger(__name__)

def ensure_date_string(date_obj):
    """Convert a date object to string if needed"""
    logger.info(f"++++++++++ - Ensuring date string: {date_obj}")
    logger.info(f"++++++++++ - Date Obj type date string: {type(date_obj)}")

    return date_obj

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
    logger = logging.getLogger(__name__)
    
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
    carbs_actual = sum(float(nutrition_ref_dict.get(int(t.get('nutrition_ref_id', 0)), {}).get('carbohydrate', 0)) * float(t.get('serving_count', 1)) 
                       for t in transactions if 'nutrition_ref_id' in t)
    protein_actual = sum(float(nutrition_ref_dict.get(int(t.get('nutrition_ref_id', 0)), {}).get('protein', 0)) * float(t.get('serving_count', 1)) 
                         for t in transactions if 'nutrition_ref_id' in t)
    fat_actual = sum(float(nutrition_ref_dict.get(int(t.get('nutrition_ref_id', 0)), {}).get('fat', 0)) * float(t.get('serving_count', 1)) 
                     for t in transactions if 'nutrition_ref_id' in t)
    fiber_actual = sum(float(nutrition_ref_dict.get(int(t.get('nutrition_ref_id', 0)), {}).get('fiber', 0)) * float(t.get('serving_count', 1)) 
                       for t in transactions if 'nutrition_ref_id' in t)
    
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
            'name': patient_info.get('name', f"Patient {patient_id}"),
            'age': calculate_age(patient_info.get('birth_date')),
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

# def create_unified_report_format(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Create a unified data format that works for both dashboard display and PDF/HTML reports.
    
#     Args:
#         dashboard_data: Dashboard data (with or without AI analysis)
        
#     Returns:
#         Unified format data dictionary
#     """
#     logger = logging.getLogger(__name__)
    
#     # Extract patient data
#     patient = dashboard_data.get('patient', {})
#     nutrients = dashboard_data.get('nutrients', {})
#     food_items = dashboard_data.get('food_items', [])
#     summary = dashboard_data.get('summary', {})
    
#     # Create unified structure
#     unified_data = {
#         'report_date': datetime.now().isoformat(),
#         'patient_info': {
#             'id': patient.get('id', ''),
#             'name': patient.get('name', ''),
#             'age': patient.get('age', ''),
#             'allergies': patient.get('allergies', [])
#         },
#         'date_range': {
#             'start': summary.get('date_range', {}).get('start', ''),
#             'end': summary.get('date_range', {}).get('end', '')
#         },
#         'nutrients': {
#             'calories': {
#                 'actual': nutrients.get('calories', {}).get('actual', 0),
#                 'target': nutrients.get('calories', {}).get('target', 0)
#             },
#             'macronutrients': {
#                 'carbs': {
#                     'actual': nutrients.get('carbs', {}).get('actual', 0),
#                     'target': nutrients.get('carbs', {}).get('target', 0),
#                     'percentage': calculate_percentage(
#                         nutrients.get('carbs', {}).get('actual', 0),
#                         nutrients.get('carbs', {}).get('target', 0)
#                     )
#                 },
#                 'protein': {
#                     'actual': nutrients.get('protein', {}).get('actual', 0),
#                     'target': nutrients.get('protein', {}).get('target', 0),
#                     'percentage': calculate_percentage(
#                         nutrients.get('protein', {}).get('actual', 0),
#                         nutrients.get('protein', {}).get('target', 0)
#                     )
#                 },
#                 'fat': {
#                     'actual': nutrients.get('fat', {}).get('actual', 0),
#                     'target': nutrients.get('fat', {}).get('target', 0),
#                     'percentage': calculate_percentage(
#                         nutrients.get('fat', {}).get('actual', 0),
#                         nutrients.get('fat', {}).get('target', 0)
#                     )
#                 },
#                 'fiber': {
#                     'actual': nutrients.get('fiber', {}).get('actual', 0),
#                     'target': nutrients.get('fiber', {}).get('target', 0),
#                     'percentage': calculate_percentage(
#                         nutrients.get('fiber', {}).get('actual', 0),
#                         nutrients.get('fiber', {}).get('target', 0)
#                     )
#                 }
#             }
#         },
#         'food_items': food_items,
#         'summary': {
#             'total_calories': summary.get('total_calories', 0),
#             'total_items_consumed': summary.get('total_items_consumed', 0)
#         }
#     }
    
#     # Include AI analysis if it exists in the dashboard data
#     if 'ai_analysis' in dashboard_data:
#         unified_data['ai_analysis'] = dashboard_data['ai_analysis']
    
#     logger.info(f"Created unified data format with {len(food_items)} food items")
#     return unified_data

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
    return_unified: bool = False
) -> Dict[str, Any]:
    """
    Get formatted dashboard data with optional AI analysis
    
    Args:
        patient_data: Raw patient data
        patient_id: Patient identifier
        start_date: Optional start date for filtering (format: YYYY-MM-DD)
        end_date: Optional end date for filtering (format: YYYY-MM-DD)
        include_analysis: Whether to include AI analysis
        return_unified: Whether to return the unified format instead of the dashboard format
        
    Returns:
        Formatted dashboard data dictionary (or unified format if return_unified=True)
    """
    logger = logging.getLogger(__name__)
    
    # Format data for dashboard display
    dashboard_data = format_dashboard_data(patient_data, start_date, end_date)
    
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
    
    # Create the unified format if requested
    # if return_unified:
    #     unified_data = create_unified_report_format(dashboard_data)
    #     logger.info(f"Unified data prepared for patient {patient_id}")
    #     return unified_data
    
    logger.info(f"Dashboard data prepared for patient {patient_id} with {len(dashboard_data.get('food_items', []))} food items")
    return dashboard_data