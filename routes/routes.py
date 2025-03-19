import json
from flask import Blueprint, jsonify, request, current_app as app
from datetime import datetime, date

from services.aggregator import get_customer_data, collect_reporting_data
from services.prompt import get_ai_prompt_response, get_dashboard_analysis, chat_with_patient_context
from services.report import generate_pdf_report, generate_pdf_from_html
from data_access.main import get_patients, get_food_transactions, get_nutrient_targets
from utils.utils import clean_prompt_response

def calculate_age(birth_date):
    """Calculate age from birthdate"""
    if not birth_date:
        return ''
    
    try:
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, TypeError):
        return ''

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

@routes_bp.route("/dashboard-data", methods=["GET"])
def get_dashboard_data():
    """
    Get dashboard data for a specific patient with optional date filtering.
    Query parameters:
    - patient_id: ID of the patient (required)
    - start_date: Start date for filtering data (optional, format: YYYY-MM-DD)
    - end_date: End date for filtering data (optional, format: YYYY-MM-DD)
    - include_analysis: Whether to include AI analysis (optional, default=false)
    """
    patient_id = request.args.get('patient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    include_analysis = request.args.get('include_analysis', 'false').lower() == 'true'
    
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    
    try:
        # Collect all patient data
        patient_data = collect_reporting_data(int(patient_id))
        
        # Log the patient data structure for debugging
        app.logger.info(f"Patient data structure: {json.dumps(patient_data, default=str)}")
        
        # Format data for dashboard display
        dashboard_data = format_dashboard_data(patient_data, start_date, end_date)
        
        # Add AI-generated analysis if requested
        if include_analysis:
            try:
                from services.prompt import get_dashboard_analysis
                app.logger.info("Generating AI analysis for dashboard...")
                
                # Generate analysis and parse JSON response
                analysis_json = get_dashboard_analysis(patient_data)
                analysis_data = json.loads(analysis_json)
                
                # Add analysis to dashboard data
                dashboard_data['ai_analysis'] = analysis_data
                app.logger.info("AI analysis successfully generated and added to dashboard data")
            except Exception as analysis_error:
                app.logger.error(f"Error generating AI analysis: {str(analysis_error)}")
                dashboard_data['ai_analysis'] = {
                    "SUMMARY": "AI analysis could not be generated at this time.",
                    "ANALYSIS": "",
                    "RECOMMENDATIONS": "",
                    "HEALTH_INSIGHTS": ""
                }
        
        # Log the final dashboard data
        app.logger.info(f"Final dashboard food items: {dashboard_data.get('food_items', [])}")
        app.logger.info(f"Final dashboard nutrients: {dashboard_data.get('nutrients', {})}")
        
        return jsonify(dashboard_data)
    except Exception as e:
        app.logger.error(f"Error generating dashboard data: {str(e)}")
        return jsonify({"error": "Failed to generate dashboard data"}), 500

def format_dashboard_data(patient_data, start_date=None, end_date=None):
    """Format patient data for dashboard display with optional date filtering."""
    # Extract patient info
    patient_info = patient_data.get('patient_info', {})
    patient_id = patient_info.get('id', 'unknown')
    
    # Extract and format allergies
    allergies = [allergy.get('allergen', '') for allergy in patient_data.get('allergies', [])]
    
    # Extract food transactions
    transactions = patient_data.get('food_transactions', [])
    app.logger.info(f"Found {len(transactions)} transactions for patient: {patient_id}")
    
    # Get nutrition reference data for joining with transactions
    from data_access.main import get_nutrition_reference
    
    # Get all nutrition references for easier lookup
    nutrition_refs = get_nutrition_reference()
    
    # Create a lookup dictionary with proper type conversion for IDs
    nutrition_ref_dict = {}
    for ref in nutrition_refs:
        try:
            ref_id = int(ref['id'])
            nutrition_ref_dict[ref_id] = ref
            app.logger.info(f"Added nutrition ref ID {ref_id} to lookup: {ref.get('food_name', 'Unknown')}")
        except (ValueError, TypeError) as e:
            app.logger.error(f"Failed to process nutrition reference ID: {e}")
    
    app.logger.info(f"Successfully loaded {len(nutrition_ref_dict)} nutrition references for lookup")
    
    # Let's debug the ref IDs we're looking for versus what we have
    transaction_ref_ids = [t.get('nutrition_ref_id') for t in transactions if 'nutrition_ref_id' in t]
    app.logger.info(f"Transaction ref IDs needed: {transaction_ref_ids}")
    app.logger.info(f"Available ref IDs: {sorted(list(nutrition_ref_dict.keys()))}")
    
    # Filter transactions by date if start_date and end_date are provided
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            app.logger.info(f"Filtering transactions by date: {start_date_obj} to {end_date_obj}")
            
            filtered_transactions = []
            for transaction in transactions:
                if 'consumption_date' in transaction:
                    try:
                        # Handle both string and date object types for consumption_date
                        transaction_date = transaction['consumption_date']
                        if isinstance(transaction_date, str):
                            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                        
                        app.logger.info(f"Transaction date: {transaction_date} (type: {type(transaction_date).__name__})")
                        
                        if start_date_obj <= transaction_date <= end_date_obj:
                            app.logger.info(f"Transaction within date range: {transaction}")
                            filtered_transactions.append(transaction)
                        else:
                            app.logger.info(f"Transaction outside date range: {transaction_date}")
                    except (ValueError, TypeError) as e:
                        app.logger.error(f"Error parsing transaction date: {e}")
                        continue
            
            app.logger.info(f"After date filtering: {len(filtered_transactions)} of {len(transactions)} transactions remain")
            transactions = filtered_transactions
        except (ValueError, TypeError) as e:
            app.logger.error(f"Error parsing filter dates: {e}")
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
            app.logger.error(f"Error converting target values: {e}")
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
    app.logger.info(f"Starting to process {len(transactions)} transactions. Initial nutrients: {total_nutrients_before}")
    
    # Double-check transaction data
    if not transactions:
        app.logger.warning("No transactions to process!")

    # Process each transaction
    for i, transaction in enumerate(transactions):
        app.logger.info(f"Processing transaction {i+1} of {len(transactions)}: {transaction}")
        
        try:
            # Extract nutrition reference ID as an integer
            nutrition_ref_id = int(transaction.get('nutrition_ref_id', 0))
            servings = float(transaction.get('servings', 1))
            
            # Look up the nutrition data for this reference ID
            nutrition_data = nutrition_ref_dict.get(nutrition_ref_id, {})
            
            # Log details about what we found
            app.logger.info(f"Looking up nutrition reference ID: {nutrition_ref_id}")
            app.logger.info(f"Nutrition data keys: {list(nutrition_data.keys()) if nutrition_data else 'None'}")
            
            # If we found nutrition data for this transaction
            if nutrition_data:
                app.logger.info(f"Found nutrition data for ID {nutrition_ref_id}: {nutrition_data.get('food_name', 'Unknown')}, {servings} servings")
                
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
                    app.logger.error(f"Error converting nutrition values: {e}")
                    calories = protein = carbs = fat = fiber = 0
                
                # Log detailed nutrition data
                app.logger.info(f"Nutrition values for {nutrition_data.get('food_name', 'Unknown')}: " + 
                               f"calories={calories}, protein={protein}, carbs={carbs}, fat={fat}, fiber={fiber}")
                
                # Add to nutrient totals, multiplying by servings
                total_nutrients['calories'] += (calories * servings)
                total_nutrients['protein'] += (protein * servings)
                total_nutrients['carbs'] += (carbs * servings)
                total_nutrients['fat'] += (fat * servings)
                total_nutrients['fiber'] += (fiber * servings)
                
                app.logger.info(f"Running totals after adding {servings} servings: " +
                               f"calories={total_nutrients['calories']}, protein={total_nutrients['protein']}, " +
                               f"carbs={total_nutrients['carbs']}, fat={total_nutrients['fat']}, fiber={total_nutrients['fiber']}")
            else:
                app.logger.warning(f"No nutrition data found for ID {nutrition_ref_id}")
        except (ValueError, TypeError) as e:
            app.logger.error(f"Error processing transaction data: {e}")
    
    app.logger.info(f"Finished processing transactions. Final nutrients: {total_nutrients}")
    
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

@routes_bp.route("/generate-report", methods=["GET"])
def generate_report():
    """
    Generate a PDF report for a patient with optional parameters.
    Query parameters:
    - patient_id: ID of the patient (optional)
    - start_date: Start date for report period (optional, format: YYYY-MM-DD)
    - end_date: End date for report period (optional, format: YYYY-MM-DD)
    - sections: Comma-separated list of sections to include (optional)
    - include_ai: Whether to include AI analysis (optional, default=true)
    """
    patient_id = request.args.get('patient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sections_param = request.args.get('sections')
    include_ai = request.args.get('include_ai', 'true').lower() == 'true'
    
    # Parse sections if provided
    sections = None
    if sections_param:
        sections = [s.strip() for s in sections_param.split(',')]
    
    app.logger.info(f"Generating report for patient {patient_id} from {start_date} to {end_date}")
    app.logger.info(f"Sections: {sections}, Include AI: {include_ai}")
    
    try:
        # If patient_id is provided, get real data
        if patient_id:
            # Collect patient data
            patient_data = collect_reporting_data(int(patient_id))
            
            # Format data for report
            dashboard_data = format_dashboard_data(patient_data, start_date, end_date)
            
            # If AI analysis is requested, include it in the dashboard data
            if include_ai and not dashboard_data.get('ai_analysis'):
                try:
                    from services.prompt import get_dashboard_analysis
                    app.logger.info("Generating AI analysis for dashboard data...")
                    
                    # Generate analysis and parse JSON response
                    analysis_json = get_dashboard_analysis(patient_data)
                    analysis_data = json.loads(analysis_json)
                    
                    # Add analysis to dashboard data
                    dashboard_data['ai_analysis'] = analysis_data
                    app.logger.info("AI analysis successfully generated and added to dashboard data")
                except Exception as analysis_error:
                    app.logger.error(f"Error generating AI analysis: {str(analysis_error)}")
                    # Continue without AI analysis
            
            # Generate report data format from dashboard data
            report_data = convert_dashboard_to_report_format(dashboard_data)
            
            # Include AI analysis if it was generated
            if dashboard_data.get('ai_analysis'):
                report_data['ai_analysis'] = dashboard_data['ai_analysis']
                app.logger.info("AI analysis included in report data")
        else:
            # Use mock data if no patient_id
            try:
                with open("services/report_generation/mock_report_data.json", "r") as file:
                    report_data = json.load(file)
                app.logger.info("Using mock data for report")
            except Exception as mock_error:
                app.logger.error(f"Error loading mock data: {str(mock_error)}")
                return jsonify({"error": "Failed to load mock data", "details": str(mock_error)}), 500
        
        # Generate the PDF report using the HTML-to-PDF method
        try:
            report_result = generate_pdf_from_html(
                report_data,
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                sections=sections,
                include_ai_analysis=include_ai
            )
        except Exception as e:
            # If the new HTML method fails, fall back to the old method
            app.logger.warning(f"HTML-to-PDF generation failed: {str(e)}, falling back to legacy method")
            report_result = generate_pdf_report(
                report_data,
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                sections=sections,
                include_ai_analysis=include_ai
            )
        
        # Check if report generation was successful
        if report_result.get("status") == "Error":
            app.logger.error(f"Report generation failed: {report_result.get('error')}")
            return jsonify({"error": "Failed to generate report", "details": report_result.get('error')}), 500
            
        app.logger.info(f"Report generated successfully: {report_result.get('file')}")
        
        return jsonify(report_result)
    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": "Failed to generate report", "details": str(e)}), 500

def convert_dashboard_to_report_format(dashboard_data):
    """Convert dashboard data format to the format expected by the report generator."""
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
                "carbohydrate": {
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
    
    return report_data

@routes_bp.route("/get-patient-reports", methods=["GET"])
def get_patient_reports():
    """
    Get a list of previously generated reports for a patient.
    Query parameters:
    - patient_id: ID of the patient (required)
    """
    from services.report_storage import get_reports_for_patient
    
    patient_id = request.args.get('patient_id')
    
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    
    try:
        reports = get_reports_for_patient(patient_id)
        return jsonify({"patient_id": patient_id, "reports": reports})
    except Exception as e:
        app.logger.error(f"Error retrieving reports: {str(e)}")
        return jsonify({"error": "Failed to retrieve reports"}), 500

@routes_bp.route("/clients", methods=["GET"])
def get_clients():
    patients = get_patients()
    print(f"Patients: {patients}")

    return jsonify(patients)

@routes_bp.route("/chat", methods=["POST"])
def chat():
    """
    AI chat endpoint for dietitians to ask questions about patient data.
    
    Request body:
    - patient_id: ID of the patient (required)
    - message: The dietitian's question or message (required)
    - chat_history: Optional array of previous messages in the conversation
    
    Returns:
    - response: The AI's response to the message
    - chat_history: Updated chat history including the new message and response
    """
    # Get request data
    request_data = request.json
    
    if not request_data:
        return jsonify({"error": "No request data provided"}), 400
    
    patient_id = request_data.get('patient_id')
    message = request_data.get('message')
    chat_history = request_data.get('chat_history', [])
    
    # Validate required fields
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        # Get patient data for context
        patient_data = collect_reporting_data(int(patient_id))
        
        # Log that we're processing a chat message
        app.logger.info(f"Processing chat message for patient {patient_id}: {message[:50]}...")
        
        # Get response from AI
        chat_response = chat_with_patient_context(
            patient_data=patient_data,
            message=message,
            chat_history=chat_history
        )
        
        app.logger.info(f"Chat response generated successfully")
        
        # Return the response and updated chat history
        return jsonify({
            "response": chat_response.get("response", ""),
            "chat_history": chat_response.get("chat_history", [])
        })
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Failed to process chat message", 
            "details": str(e)
        }), 500