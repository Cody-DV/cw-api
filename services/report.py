"""
Simplified report generation module focusing on HTML and WeasyPrint PDF generation.
"""
import os
import logging
import json
import math
from datetime import datetime
from io import BytesIO
from services.report_storage import ensure_reports_directory, get_report_filename, store_report_metadata, REPORTS_DIR
from services.prompt import get_dashboard_analysis

# Define global flags for available PDF generators
WEASYPRINT_AVAILABLE = False

# Import WeasyPrint conditionally
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    logging.warning("WeasyPrint not available due to missing system dependencies")

# Define custom colors to match the dashboard
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'background': '#f5f6fa',
    'text': '#2c3e50',
    'border': '#dcdde1',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'card_bg': '#f8f9fa',
    'progress_bg': '#f1f1f1',
    'progress_fill': '#3498db'
}

# Define report section options
REPORT_SECTIONS = {
    "calories": "Caloric Intake",
    "macronutrients": "Macronutrient Distribution",
    "food_consumed": "Food Items Consumed",
    "food_group_recommendations": "Food Group Recommendations",
    "nutrient_intake": "Detailed Nutrient Intake",
    "summary": "Nutrition Summary",
    "ai_analysis": "AI Nutritional Analysis"
}

def create_simple_bar_chart_svg(actual, target, label="Value", width=300, height=100, 
                              color_actual="#3498db", color_target="#2ecc71"):
    """Create a simple SVG bar chart comparing actual vs target."""
    # Calculate max for scaling
    max_value = max(actual, target) * 1.2  # Add 20% for headroom
    
    # Calculate bar widths based on values
    actual_width = (actual / max_value) * (width - 20)
    target_width = (target / max_value) * (width - 20)
    
    # Bar heights and positions
    bar_height = 25
    actual_bar_y = 10
    target_bar_y = 45
    
    svg = f"""
    <svg width="{width}" height="{height}">
        <!-- Actual value bar -->
        <rect x="10" y="{actual_bar_y}" width="{actual_width}" height="{bar_height}" fill="{color_actual}" />
        <text x="{actual_width + 15}" y="{actual_bar_y + bar_height/2 + 5}" font-size="12">Actual: {actual}</text>
        
        <!-- Target value bar -->
        <rect x="10" y="{target_bar_y}" width="{target_width}" height="{bar_height}" fill="{color_target}" />
        <text x="{target_width + 15}" y="{target_bar_y + bar_height/2 + 5}" font-size="12">Target: {target}</text>
        
        <!-- Labels -->
        <text x="10" y="90" font-size="12" font-weight="bold">{label}</text>
    </svg>
    """
    return svg

def create_progress_bar_svg(percentage, width=300, height=40, show_percentage=True):
    """Create a simple SVG progress bar."""
    # Determine color based on percentage (using dashboard style)
    if percentage < 90:
        color = COLORS['warning']  # Yellow for below target
    elif percentage > 110:
        color = COLORS['danger']   # Red for way over target
    else:
        color = COLORS['success']  # Green for on target
    
    # Calculate the progress width (cap at 100%)
    progress_width = min(percentage, 100) * (width - 20) / 100
    
    svg = f"""
    <svg width="{width}" height="{height}">
        <!-- Background track -->
        <rect x="10" y="10" width="{width - 20}" height="20" fill="{COLORS['progress_bg']}" rx="5" ry="5" />
        
        <!-- Progress bar -->
        <rect x="10" y="10" width="{progress_width}" height="20" fill="{color}" rx="5" ry="5" />
        
        <!-- Percentage text -->
        {f'<text x="{width/2}" y="24" text-anchor="middle" font-size="12" font-weight="bold" fill="#ffffff">{percentage}%</text>' if show_percentage else ''}
    </svg>
    """
    return svg

def create_macronutrient_pie_chart_svg(carbs, protein, fat, size=150):
    """Create a simple SVG pie chart for macronutrients."""
    total = carbs + protein + fat
    if total == 0:
        # Empty chart if no data
        return f'<svg width="{size}" height="{size}"><text x="{size/2}" y="{size/2}" text-anchor="middle">No data</text></svg>'
    
    # Calculate angles in degrees
    carb_angle = (carbs / total) * 360
    protein_angle = (protein / total) * 360
    fat_angle = (fat / total) * 360
    
    # Convert to radians for SVG
    carb_end_angle = carb_angle * (math.pi / 180)
    protein_end_angle = (carb_angle + protein_angle) * (math.pi / 180)
    
    # Calculate end coordinates for arcs
    center = size / 2
    radius = size / 2 - 10  # Leave room for border
    
    # Carbs segment (blue)
    carb_end_x = center + radius * math.sin(carb_end_angle)
    carb_end_y = center - radius * math.cos(carb_end_angle)
    
    # Protein segment (green)
    protein_end_x = center + radius * math.sin(protein_end_angle)
    protein_end_y = center - radius * math.cos(protein_end_angle)
    
    # Calculate path fragments for pie segments
    carb_path = f"M {center} {center} L {center} {center - radius} A {radius} {radius} 0 {1 if carb_angle > 180 else 0} 1 {carb_end_x} {carb_end_y} Z"
    protein_path = f"M {center} {center} L {carb_end_x} {carb_end_y} A {radius} {radius} 0 {1 if protein_angle > 180 else 0} 1 {protein_end_x} {protein_end_y} Z"
    fat_path = f"M {center} {center} L {protein_end_x} {protein_end_y} A {radius} {radius} 0 {1 if fat_angle > 180 else 0} 1 {center} {center - radius} Z"
    
    svg = f"""
    <svg width="{size}" height="{size + 60}">
        <!-- Pie segments -->
        <path d="{carb_path}" fill="#3498db" stroke="white" stroke-width="1" />
        <path d="{protein_path}" fill="#2ecc71" stroke="white" stroke-width="1" />
        <path d="{fat_path}" fill="#e74c3c" stroke="white" stroke-width="1" />
        
        <!-- Legend -->
        <rect x="10" y="{size + 10}" width="15" height="15" fill="#3498db" />
        <text x="30" y="{size + 22}" font-size="12">Carbs: {int(carbs)}%</text>
        
        <rect x="10" y="{size + 30}" width="15" height="15" fill="#2ecc71" />
        <text x="30" y="{size + 42}" font-size="12">Protein: {int(protein)}%</text>
        
        <rect x="{size/2 + 10}" y="{size + 10}" width="15" height="15" fill="#e74c3c" />
        <text x="{size/2 + 30}" y="{size + 22}" font-size="12">Fat: {int(fat)}%</text>
    </svg>
    """
    return svg

def generate_html_report(input_data, patient_id=None, start_date=None, end_date=None, include_ai_analysis=True):
    """
    Generate an HTML report based on nutrition data.
    
    Args:
        input_data: Dictionary containing nutrition data
        patient_id: Patient identifier (optional)
        start_date: Start of report period (optional)
        end_date: End of report period (optional)
        include_ai_analysis: Whether to include AI analysis section
        
    Returns:
        HTML content as a string
    """
    try:
        logging.info(f"Generating HTML report for patient: {patient_id}")
        
        # Get patient info
        patient_info = input_data.get('patient_info', {})
        patient_name = f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}"
        
        # Get nutrition data
        nutrition_profile = input_data.get('nutrition_profile', {})
        foods_consumed = input_data.get('foods_consumed', [])
        
        # Get date range
        report_start = start_date if start_date else input_data.get('start_date', 'Not specified')
        report_end = end_date if end_date else input_data.get('end_date', 'Not specified')
        
        # Get AI analysis if requested
        ai_analysis = None
        if include_ai_analysis:
            try:
                ai_analysis = get_dashboard_analysis(input_data)
            except Exception as e:
                logging.error(f"Error getting AI analysis: {str(e)}")
                ai_analysis = None
        
        # Generate HTML with inline CSS for consistent rendering
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nutrition Report: {patient_name}</title>
            <style>
                * {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    background-color: {COLORS['background']};
                    color: {COLORS['text']};
                    line-height: 1.6;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1, h2, h3 {{
                    color: {COLORS['primary']};
                    margin-bottom: 10px;
                }}
                h1 {{
                    border-bottom: 2px solid {COLORS['border']};
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    margin-top: 30px;
                    border-bottom: 1px solid {COLORS['border']};
                    padding-bottom: 5px;
                }}
                p {{
                    margin-bottom: 10px;
                }}
                .card {{
                    background-color: {COLORS['card_bg']};
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                    border: 1px solid {COLORS['border']};
                }}
                .patient-info {{
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                table, th, td {{
                    border: 1px solid {COLORS['border']};
                }}
                th, td {{
                    padding: 10px;
                    text-align: left;
                }}
                th {{
                    background-color: {COLORS['card_bg']};
                }}
                tr:nth-child(even) {{
                    background-color: {COLORS['background']};
                }}
                .success {{
                    color: {COLORS['success']};
                }}
                .warning {{
                    color: {COLORS['warning']};
                }}
                .danger {{
                    color: {COLORS['danger']};
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Nutrition Report</h1>
                
                <div class="patient-info card">
                    <h3>Patient Information</h3>
                    <p><strong>Name:</strong> {patient_name}</p>
                    <p><strong>Patient ID:</strong> {patient_id if patient_id else 'Not specified'}</p>
                    <p><strong>Report Period:</strong> {report_start} to {report_end}</p>
                </div>
        """
        
        # Calories Section
        html += """
                <h2>Caloric Intake</h2>
        """
        
        calories = nutrition_profile.get("calories", {})
        eaten = calories.get("eaten", 'na')
        target = calories.get("target", 'na')
        
        if eaten != 'na' and target != 'na':
            # Add calorie data
            percentage = round((float(eaten) / float(target)) * 100, 1)
            status = "below" if percentage < 100 else "above" if percentage > 100 else "at"
            status_color = (
                COLORS['warning'] if percentage < 85 else 
                COLORS['danger'] if percentage > 115 else 
                COLORS['success']
            )
            
            html += f"""
                <div class="card">
                    <p><strong>Consumed:</strong> {eaten} calories</p>
                    <p><strong>Target:</strong> {target} calories</p>
                    <p><strong>Status:</strong> <span style="color: {status_color}">{percentage}% of target ({status} target)</span></p>
                    
                    {create_progress_bar_svg(percentage)}
                </div>
            """
        else:
            html += """
                <div class="card">
                    <p>Calorie data not available</p>
                </div>
            """
        
        # Macronutrients Section
        html += """
                <h2>Macronutrient Distribution</h2>
        """
        
        macronutrients = nutrition_profile.get("macronutrients", {})
        
        if macronutrients:
            # Create macronutrient pie chart
            try:
                carbs = float(macronutrients.get("carbs", {}).get("percentage", 0))
                protein = float(macronutrients.get("protein", {}).get("percentage", 0))
                fat = float(macronutrients.get("fat", {}).get("percentage", 0))
                pie_chart = create_macronutrient_pie_chart_svg(carbs, protein, fat)
            except Exception as e:
                logging.error(f"Error creating macronutrient pie chart: {str(e)}")
                pie_chart = "<p>Error generating chart</p>"
            
            html += f"""
                <div class="card">
                    <div style="display: flex; justify-content: center;">
                        {pie_chart}
                    </div>
                    
                    <table>
                        <tr>
                            <th>Nutrient</th>
                            <th>Actual (%)</th>
                            <th>Target (%)</th>
                            <th>Status</th>
                        </tr>
            """
            
            for nutrient, values in macronutrients.items():
                percentage = values.get("percentage", 'na')
                target_range = values.get("target_range", values.get("target", 'na'))
                
                if percentage != 'na' and target_range != 'na':
                    try:
                        percentage_float = float(percentage)
                        target_float = float(target_range)
                        
                        # Determine status and color
                        if percentage_float < target_float * 0.9:
                            status = "Low"
                            status_color = COLORS['warning']
                        elif percentage_float > target_float * 1.1:
                            status = "High"
                            status_color = COLORS['danger']
                        else:
                            status = "Optimal"
                            status_color = COLORS['success']
                        
                        html += f"""
                        <tr>
                            <td>{nutrient.capitalize()}</td>
                            <td>{percentage}%</td>
                            <td>{target_range}%</td>
                            <td style="color: {status_color}">{status}</td>
                        </tr>
                        """
                    except (ValueError, TypeError):
                        continue
            
            html += """
                    </table>
                </div>
            """
        else:
            html += """
                <div class="card">
                    <p>Macronutrient data not available</p>
                </div>
            """
        
        # Food Consumed Section
        html += """
                <h2>Foods Consumed</h2>
        """
        
        if foods_consumed:
            html += """
                <div class="card">
                    <table>
                        <tr>
                            <th>Food</th>
                            <th>Calories</th>
                            <th>Servings</th>
                            <th>Date</th>
                        </tr>
            """
            
            for food in foods_consumed:
                food_name = food.get("name", "Unknown")
                calories = food.get("calories", "N/A")
                servings = food.get("servings", "1")
                date = food.get("date", "N/A")
                
                html += f"""
                <tr>
                    <td>{food_name}</td>
                    <td>{calories}</td>
                    <td>{servings}</td>
                    <td>{date}</td>
                </tr>
                """
            
            html += """
                    </table>
                </div>
            """
        else:
            html += """
                <div class="card">
                    <p>No food consumption data available</p>
                </div>
            """
        
        # AI Analysis Section (if available)
        if include_ai_analysis and ai_analysis:
            html += """
                <h2>AI Nutritional Analysis</h2>
                <div class="card">
            """
            
            # Format the AI analysis with proper HTML
            if isinstance(ai_analysis, str):
                # Replace newlines with paragraph breaks
                formatted_analysis = ""
                for paragraph in ai_analysis.split('\n\n'):
                    if paragraph.strip():
                        formatted_analysis += f"<p>{paragraph}</p>"
                
                html += formatted_analysis
            else:
                html += "<p>AI analysis data is not in the expected format.</p>"
            
            html += """
                </div>
            """
        
        # Footer Section
        html += f"""
                <div class="footer">
                    <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>CardWatch Nutritional Monitoring System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    except Exception as e:
        logging.error(f"Error generating HTML report: {str(e)}")
        # Return a minimal error HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error Generating Report</h1>
            <p>An error occurred: {str(e)}</p>
        </body>
        </html>
        """

def generate_pdf_from_html(input_data, patient_id=None, start_date=None, end_date=None, 
                          sections=None, filename=None, include_ai_analysis=True):
    """
    Generate a PDF report from nutrition data using HTML and WeasyPrint.
    
    Args:
        input_data: The nutrition data to include in the report
        patient_id: The ID of the patient (for filename and metadata)
        start_date: Start date of the report period (for metadata)
        end_date: End date of the report period (for metadata)
        sections: List of sections to include (currently ignored in HTML version)
        filename: Custom filename (if None, will be auto-generated)
        include_ai_analysis: Whether to include AI analysis section
        
    Returns:
        Dictionary with report status and file information
    """
    try:
        logging.info(f"Generating HTML-based PDF report for patient: {patient_id}")
        
        # Set up the report directory
        ensure_reports_directory()
        
        # Generate filename if not provided
        if not filename and patient_id:
            filename = get_report_filename(patient_id, format="pdf")
        elif not filename:
            filename = f"nutrition_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Generate HTML content
        html_content = generate_html_report(
            input_data,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            include_ai_analysis=include_ai_analysis
        )
        
        logging.info("HTML content generated successfully")
        
        # Try to generate PDF with WeasyPrint
        if WEASYPRINT_AVAILABLE:
            try:
                logging.info("Generating PDF with WeasyPrint")
                import weasyprint
                
                pdf = weasyprint.HTML(string=html_content).write_pdf()
                
                with open(filepath, 'wb') as f:
                    f.write(pdf)
                    
                logging.info(f"PDF created with WeasyPrint and saved to {filepath}")
                
                # Store metadata about this report
                if patient_id:
                    metadata = store_report_metadata(
                        patient_id, 
                        filename, 
                        "nutrition", 
                        start_date, 
                        end_date,
                        format="pdf",
                        renderer="weasyprint"
                    )
                
                return {
                    "status": "Report generated",
                    "file": filename,
                    "path": filepath,
                    "format": "pdf",
                    "renderer": "weasyprint"
                }
            except Exception as e:
                error_message = str(e)
                logging.error(f"WeasyPrint generation failed: {error_message}")
                # Fall back to HTML
        
        # If PDF generation failed, save HTML as fallback
        html_filepath = os.path.join(REPORTS_DIR, f"{os.path.splitext(filename)[0]}.html")
        try:
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"Saved HTML version as fallback to {html_filepath}")
            
            # Store metadata about this HTML report
            if patient_id:
                metadata = store_report_metadata(
                    patient_id, 
                    os.path.basename(html_filepath), 
                    "nutrition", 
                    start_date, 
                    end_date,
                    format="html",
                    renderer="html-only"
                )
            
            # Formatted error message for user
            error_message = """PDF generation failed. 

To enable PDF generation, install WeasyPrint with:
   uv pip install weasyprint

Note: WeasyPrint requires additional system dependencies. For Docker environment,
these dependencies are already installed.

An HTML version of the report has been saved instead."""

            return {
                "status": "Warning: " + error_message,
                "file": os.path.basename(html_filepath),
                "path": html_filepath,
                "format": "html",
                "renderer": "html-only"
            }
        except Exception as html_error:
            error_message = f"Failed to create PDF with WeasyPrint and HTML fallback also failed: {str(html_error)}"
            logging.error(error_message)
            return {
                "status": "Error",
                "error": error_message,
                "file": None,
                "path": None
            }
    
    except Exception as e:
        logging.error(f"Critical error generating report: {str(e)}")
        # Return error information instead of raising exception
        return {
            "status": "Error",
            "error": str(e),
            "file": None,
            "path": None
        }

# For backwards compatibility
generate_pdf_report = generate_pdf_from_html