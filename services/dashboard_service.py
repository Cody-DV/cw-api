"""
Dashboard service module
Centralizes all dashboard-related functionality
"""
import json
import logging
from datetime import datetime, date
from services.prompt import get_dashboard_analysis
from data_access.main import get_nutrition_reference

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

def format_dashboard_data(patient_data, start_date=None, end_date=None):
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
            logger.info(f"Added nutrition ref ID {ref_id} to lookup: {ref.get('food_name', 'Unknown')}")
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to process nutrition reference ID: {e}")
    
    logger.info(f"Successfully loaded {len(nutrition_ref_dict)} nutrition references for lookup")
    
    # Debug ref IDs
    transaction_ref_ids = [t.get('nutrition_ref_id') for t in transactions if 'nutrition_ref_id' in t]
    logger.info(f"Transaction ref IDs needed: {transaction_ref_ids}")
    logger.info(f"Available ref IDs: {sorted(list(nutrition_ref_dict.keys()))}")
    
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
                        
                        logger.info(f"Transaction date: {transaction_date} (type: {type(transaction_date).__name__})")
                        
                        if start_date_obj <= transaction_date <= end_date_obj:
                            logger.info(f"Transaction within date range: {transaction}")
                            filtered_transactions.append(transaction)
                        else:
                            logger.info(f"Transaction outside date range: {transaction_date}")
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error parsing transaction date: {e}")
                        continue
            
            logger.info(f"After date filtering: {len(filtered_transactions)} of {len(transactions)} transactions remain")
            transactions = filtered_transactions
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing filter dates: {e}")
            # If date parsing fails, use all transactions
            pass
    
    # Extract nutrient targets
    nutrient_targets = patient_data.get('nutrient_targets', [])
    
    # Convert nutrient targets to a more accessible format with proper type conversion
    formatted_targets = {}
    for target in nutrient_targets:
        try:
            if 'calories_target' in target:
                formatted_targets['calories'] = float(target.get('calories_target', 0))
            if 'protein_target' in target:
                formatted_targets['protein'] = float(target.get('protein_target', 0))
            if 'carbs_target' in target:
                formatted_targets['carbs'] = float(target.get('carbs_target', 0))
            if 'fat_target' in target:
                formatted_targets['fat'] = float(target.get('fat_target', 0))
            if 'fiber_target' in target:
                formatted_targets['fiber'] = float(target.get('fiber_target', 0))
        except (TypeError, ValueError) as e:
            logger.error(f"Error converting target values: {e}")
            # Keep defaults if conversion fails
    
    # Calculate total nutrient consumption from transactions
    total_nutrients = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0
    }
    
    food_items = []
    total_nutrients_before = dict(total_nutrients)
    logger.info(f"Starting to process {len(transactions)} transactions. Initial nutrients: {total_nutrients_before}")
    
    # Double-check transaction data
    if not transactions:
        logger.warning("No transactions to process!")

    # Process each transaction
    for i, transaction in enumerate(transactions):
        logger.info(f"Processing transaction {i+1} of {len(transactions)}: {transaction}")
        
        try:
            # Extract nutrition reference ID as an integer
            nutrition_ref_id = int(transaction.get('nutrition_ref_id', 0))
            servings = float(transaction.get('servings', 1))
            
            # Look up the nutrition data for this reference ID
            nutrition_data = nutrition_ref_dict.get(nutrition_ref_id, {})
            
            # Log details about what we found
            logger.info(f"Looking up nutrition reference ID: {nutrition_ref_id}")
            logger.info(f"Nutrition data keys: {list(nutrition_data.keys()) if nutrition_data else 'None'}")
            
            # If we found nutrition data for this transaction
            if nutrition_data:
                logger.info(f"Found nutrition data for ID {nutrition_ref_id}: {nutrition_data.get('food_name', 'Unknown')}, {servings} servings")
                
                # Add to food items list
                food_items.append({
                    'name': nutrition_data.get('food_name', 'Unknown Food'),
                    'quantity': servings,
                    'date': transaction.get('consumption_date', '')
                })
                
                # Get individual nutrient values and convert from Decimal to float
                try:
                    calories = float(nutrition_data.get('calories', 0))
                    protein = float(nutrition_data.get('protein_g', 0))
                    carbs = float(nutrition_data.get('carbs_g', 0))
                    fat = float(nutrition_data.get('fat_g', 0))
                    fiber = float(nutrition_data.get('fiber_g', 0))
                except (TypeError, ValueError) as e:
                    logger.error(f"Error converting nutrition values: {e}")
                    calories = protein = carbs = fat = fiber = 0
                
                # Log detailed nutrition data
                logger.info(f"Nutrition values for {nutrition_data.get('food_name', 'Unknown')}: " + 
                           f"calories={calories}, protein={protein}, carbs={carbs}, fat={fat}, fiber={fiber}")
                
                # Add to nutrient totals, multiplying by servings
                total_nutrients['calories'] += (calories * servings)
                total_nutrients['protein'] += (protein * servings)
                total_nutrients['carbs'] += (carbs * servings)
                total_nutrients['fat'] += (fat * servings)
                total_nutrients['fiber'] += (fiber * servings)
                
                logger.info(f"Running totals after adding {servings} servings: " +
                           f"calories={total_nutrients['calories']}, protein={total_nutrients['protein']}, " +
                           f"carbs={total_nutrients['carbs']}, fat={total_nutrients['fat']}, fiber={total_nutrients['fiber']}")
            else:
                logger.warning(f"No nutrition data found for ID {nutrition_ref_id}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing transaction data: {e}")
    
    logger.info(f"Finished processing transactions. Final nutrients: {total_nutrients}")
    
    # Format target vs. actual data
    nutrient_comparison = {}
    
    # Set up the nutrient comparison based on our formatted targets and totals
    nutrient_comparison['calories'] = {
        'target': formatted_targets.get('calories', 2000),  # Default to 2000 if not provided
        'actual': total_nutrients['calories']
    }
    
    nutrient_comparison['protein'] = {
        'target': formatted_targets.get('protein', 50),  # Default to 50g if not provided
        'actual': total_nutrients['protein']
    }
    
    nutrient_comparison['carbs'] = {
        'target': formatted_targets.get('carbs', 250),  # Default to 250g if not provided
        'actual': total_nutrients['carbs']
    }
    
    nutrient_comparison['fat'] = {
        'target': formatted_targets.get('fat', 70),  # Default to 70g if not provided
        'actual': total_nutrients['fat']
    }
    
    nutrient_comparison['fiber'] = {
        'target': formatted_targets.get('fiber', 25),  # Default to 25g if not provided
        'actual': total_nutrients['fiber']
    }
    
    # Construct the dashboard data
    dashboard_data = {
        'patient': {
            'id': patient_info.get('id', ''),
            'name': f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}".strip(),
            'age': calculate_age(patient_info.get('date_of_birth')),
            'allergies': allergies
        },
        'nutrients': nutrient_comparison,
        'food_items': food_items,
        'summary': {
            'total_items_consumed': len(food_items),
            'total_calories': total_nutrients['calories'],
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
    }
    
    return dashboard_data

def convert_dashboard_to_report_format(dashboard_data):
    """
    Convert dashboard data format to the format expected by the report generator.
    
    Args:
        dashboard_data: Dashboard data dictionary
        
    Returns:
        Report data dictionary formatted for the PDF generator
    """
    logger = logging.getLogger(__name__)
    
    # Extract data from dashboard format
    patient = dashboard_data.get('patient', {})
    nutrients = dashboard_data.get('nutrients', {})
    food_items = dashboard_data.get('food_items', [])
    summary = dashboard_data.get('summary', {})
    
    # Create a report-compatible structure
    report_data = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "nutrition_profile": {
            "calories": {
                "eaten": str(nutrients.get('calories', {}).get('actual', 0)) if 'calories' in nutrients else "0",
                "target": str(nutrients.get('calories', {}).get('target', 0)) if 'calories' in nutrients else "0"
            },
            "macronutrients": {
                "carbs": {
                    "percentage": str(nutrients.get('carbs', {}).get('actual', 0)) if 'carbs' in nutrients else "0",
                    "target": str(nutrients.get('carbs', {}).get('target', 0)) if 'carbs' in nutrients else "0"
                },
                "protein": {
                    "percentage": str(nutrients.get('protein', {}).get('actual', 0)) if 'protein' in nutrients else "0",
                    "target": str(nutrients.get('protein', {}).get('target', 0)) if 'protein' in nutrients else "0"
                },
                "fat": {
                    "percentage": str(nutrients.get('fat', {}).get('actual', 0)) if 'fat' in nutrients else "0",
                    "target": str(nutrients.get('fat', {}).get('target', 0)) if 'fat' in nutrients else "0"
                }
            },
            "food_consumed": [],
            "food_group_recommendations": {
                "grain_products": {
                    "eaten": "0",
                    "target": "0"
                },
                "vegetables_fruit": {
                    "eaten": "0",
                    "target": "0"
                }
            },
            "nutrient_intake": {
                "carbohydrate": {
                    "eaten": str(nutrients.get('carbs', {}).get('actual', 0)) if 'carbs' in nutrients else "0",
                    "target": str(nutrients.get('carbs', {}).get('target', 0)) if 'carbs' in nutrients else "0"
                },
                "protein": {
                    "eaten": str(nutrients.get('protein', {}).get('actual', 0)) if 'protein' in nutrients else "0",
                    "target": str(nutrients.get('protein', {}).get('target', 0)) if 'protein' in nutrients else "0"
                },
                "fiber": {
                    "eaten": str(nutrients.get('fiber', {}).get('actual', 0)) if 'fiber' in nutrients else "0",
                    "target": str(nutrients.get('fiber', {}).get('target', 0)) if 'fiber' in nutrients else "0"
                }
            }
        },
        "summary": {
            "calories": f"Total calories consumed: {summary.get('total_calories', 0)}",
            "food_items": f"Total food items consumed: {summary.get('total_items_consumed', 0)}",
            "date_range": f"Report period: {summary.get('date_range', {}).get('start', 'N/A')} to {summary.get('date_range', {}).get('end', 'N/A')}",
            "patient_info": f"Patient: {patient.get('name', 'Unknown')} (ID: {patient.get('id', 'Unknown')})"
        }
    }
    
    # Include AI analysis if available
    if 'ai_analysis' in dashboard_data and dashboard_data['ai_analysis']:
        report_data['ai_analysis'] = dashboard_data['ai_analysis']
    
    # Group food items by date to create meals
    meals_by_date = {}
    for item in food_items:
        date = item.get('date', 'Unknown Date')
        if date not in meals_by_date:
            meals_by_date[date] = []
        
        meals_by_date[date].append({
            "food": item.get('name', 'Unknown Food'),
            "quantity": str(item.get('quantity', 1))
        })
    
    # Convert grouped items to meals format
    for date, items in meals_by_date.items():
        meal = {
            "meal": f"Meal on {date}",
            "time": date,
            "items": items
        }
        report_data["nutrition_profile"]["food_consumed"].append(meal)
    
    logger.info(f"Converted dashboard data to report format with {len(meals_by_date)} meal groups")
    return report_data

def get_dashboard_with_analysis(patient_data, patient_id, start_date=None, end_date=None, include_analysis=False):
    """
    Get formatted dashboard data with optional AI analysis
    
    Args:
        patient_data: Raw patient data
        patient_id: Patient identifier
        start_date: Optional start date for filtering (format: YYYY-MM-DD)
        end_date: Optional end date for filtering (format: YYYY-MM-DD)
        include_analysis: Whether to include AI analysis
        
    Returns:
        Formatted dashboard data dictionary
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
    
    logger.info(f"Dashboard data prepared for patient {patient_id} with {len(dashboard_data.get('food_items', []))} food items")
    return dashboard_data