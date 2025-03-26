# Changelog

All notable changes to the CardWatch Reporting API project will be documented in this file.

## [Unreleased]

### Added
- High-quality JavaScript-rendered PDF reports
  - Integrated Node.js and Puppeteer for server-side PDF generation
  - Created Chart.js-based visualizations for beautiful, modern charts
  - Implemented responsive templates with improved styling
  - Added fallback mechanisms to WeasyPrint if JavaScript rendering fails
  - Enhanced chart styling with better colors, legends, and interactivity

- Automated scheduled report generation
  - Added APScheduler integration for recurring report generation
  - Created scheduling endpoints to configure report schedules
  - Implemented daily, weekly, and monthly scheduling options
  - Added metadata storage for scheduled reports
  - Included manual trigger endpoint for immediate generation

- Enhanced frontend integration
  - Added schedule management UI in the dashboard
  - Created schedule form with frequency, time, and section options
  - Implemented schedule display and cancellation interface
  - Added frontend API methods for scheduling reports

- Containerized frontend and backend
  - Created separate frontend container with Vite.js
  - Updated API container with Node.js support for PDF generation
  - Enhanced Docker configuration for development and production
  - Implemented shared volume for report storage

### Added
- Enhanced PDF Report Generation
  - Created custom DashboardPDF class for modern, visually appealing reports
  - Added responsive metric cards matching dashboard appearance
  - Implemented progress bars to visualize goals vs. actuals
  - Created dashboard-style charts with improved colors and styling
  - Added AI analysis section to PDF reports
  - Organized content into clean, readable sections
  - Improved typography and visual hierarchy
  - Added styled tables with alternating row colors
  - Implemented rounded corners and modern styling elements
  - Added color coding for nutritional status (below/on target/above)
  - Improved page navigation with page numbers
  - Enhanced header and footer with clean design
  
- AI Chat Interface for Dietitians
  - Created ChatContext class for maintaining conversation state with patient context
  - Added a new `/chat` endpoint for interactive AI conversations
  - Implemented an intuitive chat UI component in the dashboard
  - Added message history with styled user and assistant messages
  - Included typing indicators for a professional chat experience
  - Integrated pre-defined quick question buttons for common dietary inquiries
  - Implemented context-aware responses based on patient data
  - Added error handling and fallback mechanisms for reliability

- AI Analysis and Recommendations
  - Integrated OpenAI API for nutritional analysis and recommendations
  - Added new `get_dashboard_analysis` function to generate AI-powered insights
  - Enhanced `/dashboard-data` endpoint with optional AI analysis
  - Added new `include_analysis` query parameter to control AI feature
  - Implemented a beautifully styled AI analysis section in the dashboard
  - Added comprehensive sections for Summary, Analysis, Recommendations, and Health Insights
  - Improved prompt engineering for more accurate and useful nutritional feedback
  - Added error handling for AI-generated content

- Enhanced Report Generation feature
  - Created a report storage system to save and manage generated reports
  - Added customization options for report sections
  - Implemented report metadata tracking for historical access
  - Added a modal dialog for selecting report sections to include
  - Created a report history view to display previously generated reports
  - Added success messages with detailed report information
  - Improved PDF report appearance with better formatting and styling
  - Added support for data-driven charts with visual indicators (color-coding)
  - Implemented better tables and layout in PDF reports
  - Enhanced report header and footer with metadata

- Dashboard integration feature
  - Created new `/dashboard-data` API endpoint with date filtering support
  - Enhanced frontend to visualize patient nutrition data
  - Added progress bars for nutrient target vs. actual comparison
  - Implemented food items table with scrollable container
  - Added "Download PDF Report" button for PDF export
  - Improved styling with responsive grid layout for dashboard
  - Set default date range to current month
  - Added proper error handling for API requests

### Changed
- Major architectural refactoring for improved simplicity and maintainability
  - Implemented a unified data format that works across all services
  - Simplified service interfaces with consistent parameter naming
  - Improved separation of concerns between modules
  - Removed redundant conversion functions and fallback mechanisms
  - Streamlined the JavaScript bridge with cleaner error handling
  - Enhanced the PDF generation pipeline to be more robust
  - Updated frontend API client with more consistent interface
  - Simplified route handlers with better error handling
  - Added comprehensive logging throughout the system
  - Improved type hints and documentation

- Improved AI integration
  - Enhanced prompt.py with lower temperature settings for more consistent results
  - Added proper documentation and type hints to AI-related functions
  - Improved error handling for AI service interactions
  - Added structured JSON response format for AI analysis results

- Refactored codebase for improved modularity and maintainability
  - Combined dashboard.py and dashboard_service.py into a single consolidated module
  - Merged all report-related files (report.py, report_generator.py, report_storage.py) into report_service.py
  - Improved logical separation of concerns with better code organization
  - Enhanced docstrings and function documentation
  - Removed duplicate code and improved parameter descriptions
  - Simplified service imports in routes.py
  - Maintained consistent API while improving internal structure

### Fixed
- Fixed PDF report generation issues
  - Eliminated font loading errors by using standard fonts
  - Improved error handling in report generation
  - Fixed rounded rectangle drawing for better compatibility
  - Enhanced report API endpoint with better error reporting
  - Added fallback to simple PDF when complex reports fail
  - Added granular section-by-section error handling
  - Implemented detailed logging throughout PDF generation
  - Fixed AI analysis integration with report generation
  - Improved PDF UI controls to enable/disable AI features
  - Fixed chart generation to work reliably across different data types

- Fixed syntax error in routes.py
  - Added missing except block in transaction processing code

- Fixed date filtering issues
  - Enhanced date parsing to handle both date objects and string dates
  - Added comprehensive logging for date filter debugging
  - Improved the date comparison logic for filtering transactions
  - Added detailed logging for filtered transactions

- Fixed nutrient data not displaying in dashboard
  - Implemented proper join between food transactions and nutrition reference data
  - Corrected nutrient target calculation
  - Fixed patient name and age display
  - Added proper handling of allergies data
  - Fixed type casting issues with nutrition reference IDs
  - Added extensive logging for debugging data flow
  - Fixed undefined variable error in dashboard data processing
  - Added explicit Decimal to float type conversion for numeric values
  - Enhanced logging for database queries and data processing
  - Fixed data flow between transactions and nutrition reference data
  - Improved error handling to skip invalid transactions
  - Added detailed debugging for nutrition reference lookup
  - Fixed transaction processing loop structure
  - Added better error handling around the nutrition data processing

- Fixed issue with PDF export not displaying values or charts
  - Ensured consistent data format between dashboard and PDF generation
  - Fixed the data structure passed to the report template
  - Enhanced error handling in the PDF generation process
  - Simplified the data transformation pipeline