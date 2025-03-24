"""
JavaScript Bridge Service for CardWatch Reporting API

This module provides a clean interface between Python and Node.js for generating
HTML and PDF reports with JavaScript-rendered charts.
"""
import os
import json
import logging
import tempfile
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date objects"""
    def default(self, obj):
        # if isinstance(obj, (datetime.date, datetime)):
        #     return obj.isoformat()
        return obj.isoformat()

def check_node_installed() -> bool:
    """Check if Node.js is installed and working"""
    try:
        process = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if process.returncode == 0:
            logger.info(f"Node.js is installed: {process.stdout.strip()}")
            return True
        else:
            logger.warning(f"Node.js check failed: {process.stderr}")
            return False
    except Exception as e:
        logger.warning(f"Error checking Node.js: {str(e)}")
        return False

def generate_html_file(
    data: Dict[str, Any],
    output_html_path: str,
    template_path: str
) -> str:
    """Generate an HTML file with data embedded"""
    logger.info(f"Generating HTML file at {output_html_path}")
    
    # Read the template
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Replace the data placeholder
        html_content = template_content.replace(
            '/* DATA_PLACEHOLDER */',
            f'const reportData = {json.dumps(data, cls=DateTimeEncoder)};'
        )
        
        # Write to output file
        with open(output_html_path, 'w') as f:
            f.write(html_content)
            
        logger.info(f"HTML file generated at {output_html_path}")
        return output_html_path
    except Exception as e:
        logger.error(f"Error generating HTML file: {str(e)}")
        raise

def generate_pdf(
    data: Dict[str, Any],
    output_path: str,
    template_path: Optional[str] = None
) -> str:
    """
    Generate a PDF using Node.js and Puppeteer with JavaScript charts
    
    Args:
        data: Dictionary containing the report data
        output_path: Path where the PDF will be stored
        template_path: Path to the HTML template (optional, uses default if None)
        
    Returns:
        Path to the generated PDF file
    """
    logger.info(f"Generating PDF to {output_path}")
    
    # Check if Node.js is installed
    if not check_node_installed():
        raise RuntimeError("Node.js is not available. PDF generation requires Node.js.")
    
    # Use default template if not provided
    if template_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, "js", "templates", "report-template.html")
    
    logger.info(f"Using template: {template_path}")
    
    # Create temp file for data, using the custom encoder for dates
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_data_path = temp_file.name
        json.dump(data, temp_file, cls=DateTimeEncoder)
    
    try:
        # Get the script path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        node_script_path = os.path.join(base_dir, "js", "pdf-generator.js")
        
        cmd = [
            "node",
            node_script_path,
            template_path,
            temp_data_path,
            output_path
        ]
        
        logger.info(f"Running PDF generator: {' '.join(cmd)}")
        
        # Execute the Node.js script
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Log output
        if process.stdout:
            logger.info(f"PDF Generator stdout: {process.stdout}")
        
        if process.stderr:
            logger.warning(f"PDF Generator stderr: {process.stderr}")
            
        # Check for errors
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, 
                cmd, 
                output=process.stdout, 
                stderr=process.stderr
            )
        
        # Verify file exists
        if os.path.exists(output_path):
            logger.info(f"PDF generated successfully at {output_path}")
            return output_path
        else:
            error_msg = f"PDF file was not created at {output_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
    except subprocess.CalledProcessError as e:
        logger.error(f"PDF generation failed with error code {e.returncode}: {e.stderr}")
        raise RuntimeError(f"PDF generation failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF generation: {str(e)}")
        raise
    finally:
        # Clean up the temporary data file
        try:
            if os.path.exists(temp_data_path):
                os.unlink(temp_data_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary data file: {str(e)}")