// Import API functions
import { scheduleReport, getScheduledReports, cancelScheduledReport } from './api.js';

// Initialize the scheduled reports UI
export function initScheduledReports() {
    // DOM Elements - we'll create these dynamically
    let scheduledReportsSection = null;
    let scheduleFormContainer = null;
    
    // Function to create the scheduled reports UI
    function createScheduledReportsUI() {
        // If already exists, return
        if (scheduledReportsSection) return;
        
        // Check if we're on the dashboard container
        const dashboardContainer = document.querySelector('.dashboard-container');
        if (!dashboardContainer) return;
        
        // Create the section
        scheduledReportsSection = document.createElement('div');
        scheduledReportsSection.className = 'report-section scheduled-reports-section';
        scheduledReportsSection.style.marginTop = '30px';
        
        // Add header with button
        const headerContainer = document.createElement('div');
        headerContainer.className = 'scheduled-reports-header';
        headerContainer.style.display = 'flex';
        headerContainer.style.justifyContent = 'space-between';
        headerContainer.style.alignItems = 'center';
        headerContainer.style.marginBottom = '15px';
        
        const header = document.createElement('h2');
        header.textContent = 'Scheduled Reports';
        
        const scheduleButton = document.createElement('button');
        scheduleButton.textContent = 'Schedule New Report';
        scheduleButton.className = 'schedule-btn';
        scheduleButton.style.backgroundColor = '#27ae60';
        
        headerContainer.appendChild(header);
        headerContainer.appendChild(scheduleButton);
        
        // Add form container (initially hidden)
        scheduleFormContainer = document.createElement('div');
        scheduleFormContainer.className = 'schedule-form-container hidden';
        scheduleFormContainer.style.marginBottom = '20px';
        scheduleFormContainer.style.padding = '15px';
        scheduleFormContainer.style.backgroundColor = '#f8f9fa';
        scheduleFormContainer.style.borderRadius = '8px';
        scheduleFormContainer.style.border = '1px solid #dcdde1';
        
        // Add reports container
        const reportsContainer = document.createElement('div');
        reportsContainer.id = 'scheduledReportsContainer';
        
        // Assemble the section
        scheduledReportsSection.appendChild(headerContainer);
        scheduledReportsSection.appendChild(scheduleFormContainer);
        scheduledReportsSection.appendChild(reportsContainer);
        
        // Add to document
        dashboardContainer.appendChild(scheduledReportsSection);
        
        // Add event listener to the schedule button
        scheduleButton.addEventListener('click', toggleScheduleForm);
        
        // Create the form
        createScheduleForm();
        
        // Add styles
        addScheduleStyles();
        
        // Load scheduled reports
        loadScheduledReports();
    }
    
    // Function to create the schedule form
    function createScheduleForm() {
        const form = document.createElement('form');
        form.id = 'scheduleReportForm';
        
        form.innerHTML = `
            <h3>Schedule a Recurring Report</h3>
            <div class="form-row">
                <div class="form-group">
                    <label for="scheduleFrequency">Frequency:</label>
                    <select id="scheduleFrequency" required>
                        <option value="daily">Daily</option>
                        <option value="weekly" selected>Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>
                </div>
                
                <div class="form-group" id="weekdayGroup">
                    <label for="scheduleWeekday">Day:</label>
                    <select id="scheduleWeekday">
                        <option value="0">Monday</option>
                        <option value="1">Tuesday</option>
                        <option value="2">Wednesday</option>
                        <option value="3">Thursday</option>
                        <option value="4">Friday</option>
                        <option value="5">Saturday</option>
                        <option value="6">Sunday</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="scheduleTime">Time:</label>
                    <input type="time" id="scheduleTime" value="02:00" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group" style="flex-grow: 1;">
                    <label>Include AI Analysis:</label>
                    <div>
                        <input type="checkbox" id="scheduleIncludeAi" checked>
                        <label for="scheduleIncludeAi">Yes, include AI analysis</label>
                    </div>
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" id="cancelScheduleBtn">Cancel</button>
                <button type="submit" id="submitScheduleBtn">Schedule Report</button>
            </div>
        `;
        
        scheduleFormContainer.appendChild(form);
        
        // Add event listeners
        const frequencySelect = document.getElementById('scheduleFrequency');
        const weekdayGroup = document.getElementById('weekdayGroup');
        const cancelBtn = document.getElementById('cancelScheduleBtn');
        
        frequencySelect.addEventListener('change', function() {
            // Toggle weekday selector based on frequency
            if (this.value === 'weekly') {
                weekdayGroup.style.display = 'block';
            } else {
                weekdayGroup.style.display = 'none';
            }
        });
        
        cancelBtn.addEventListener('click', toggleScheduleForm);
        
        // Form submission
        form.addEventListener('submit', handleScheduleFormSubmit);
    }
    
    // Toggle the schedule form visibility
    function toggleScheduleForm() {
        scheduleFormContainer.classList.toggle('hidden');
    }
    
    // Handle form submission
    async function handleScheduleFormSubmit(e) {
        e.preventDefault();
        
        // Get the client ID from the main select
        const clientSelect = document.getElementById('clientSelect');
        if (!clientSelect || !clientSelect.value) {
            alert('Please select a patient first');
            return;
        }
        
        const patientId = clientSelect.value;
        const frequency = document.getElementById('scheduleFrequency').value;
        const weekday = frequency === 'weekly' ? parseInt(document.getElementById('scheduleWeekday').value) : 0;
        
        // Format time from the time input
        const timeInput = document.getElementById('scheduleTime');
        const timeValue = timeInput.value || '02:00';
        
        const includeAi = document.getElementById('scheduleIncludeAi').checked;
        
        try {
            // Show loading
            const submitBtn = document.getElementById('submitScheduleBtn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Scheduling...';
            submitBtn.disabled = true;
            
            // Schedule the report
            const result = await scheduleReport(
                patientId,
                frequency,
                weekday,
                timeValue,
                null,  // sections - use default
                includeAi
            );
            
            // Hide the form
            toggleScheduleForm();
            
            // Show success message
            alert(`Report scheduled successfully! ${result.message}`);
            
            // Reload the scheduled reports
            loadScheduledReports();
        } catch (error) {
            alert(`Failed to schedule report: ${error.message}`);
        } finally {
            // Reset button
            const submitBtn = document.getElementById('submitScheduleBtn');
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }
    
    // Load scheduled reports
    async function loadScheduledReports() {
        const container = document.getElementById('scheduledReportsContainer');
        if (!container) return;
        
        try {
            // Clear existing content
            container.innerHTML = '<div class="loading-indicator">Loading scheduled reports...</div>';
            
            // Fetch reports
            const result = await getScheduledReports();
            const reports = result.scheduled_reports || [];
            
            // Clear loading
            container.innerHTML = '';
            
            if (reports.length === 0) {
                container.innerHTML = '<p>No scheduled reports configured.</p>';
                return;
            }
            
            // Format and display each report
            reports.forEach(report => {
                const reportCard = document.createElement('div');
                reportCard.className = 'scheduled-report-card';
                
                // Format weekday if applicable
                let weekdayText = '';
                if (report.frequency === 'weekly' && report.weekday !== null) {
                    const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                    weekdayText = weekdays[report.weekday];
                }
                
                // Format frequency with weekday
                let frequencyText = report.frequency.charAt(0).toUpperCase() + report.frequency.slice(1);
                if (weekdayText) {
                    frequencyText += ` (${weekdayText})`;
                }
                
                reportCard.innerHTML = `
                    <div class="report-info">
                        <h3>Patient ${report.patient_id}</h3>
                        <p><strong>Frequency:</strong> ${frequencyText}</p>
                        <p><strong>Time:</strong> ${report.time || '02:00'}</p>
                        <p><strong>Include AI:</strong> ${report.include_ai ? 'Yes' : 'No'}</p>
                    </div>
                    <div class="report-actions">
                        <button class="cancel-schedule-btn" data-patient="${report.patient_id}" data-frequency="${report.frequency}">
                            Cancel Schedule
                        </button>
                    </div>
                `;
                
                container.appendChild(reportCard);
                
                // Add event listener to cancel button
                const cancelBtn = reportCard.querySelector('.cancel-schedule-btn');
                cancelBtn.addEventListener('click', async function() {
                    const patientId = this.getAttribute('data-patient');
                    const frequency = this.getAttribute('data-frequency');
                    
                    if (confirm(`Are you sure you want to cancel the ${frequency} report for patient ${patientId}?`)) {
                        try {
                            await cancelScheduledReport(patientId, frequency);
                            alert('Schedule cancelled successfully');
                            loadScheduledReports();
                        } catch (error) {
                            alert(`Failed to cancel schedule: ${error.message}`);
                        }
                    }
                });
            });
        } catch (error) {
            container.innerHTML = `<p class="error">Error loading scheduled reports: ${error.message}</p>`;
        }
    }
    
    // Add styles for the scheduled reports section
    function addScheduleStyles() {
        if (document.getElementById('scheduled-reports-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'scheduled-reports-styles';
        styles.textContent = `
            .scheduled-reports-section h3 {
                margin-top: 0;
                margin-bottom: 15px;
                color: #2c3e50;
            }
            
            .schedule-form-container {
                margin-bottom: 20px;
            }
            
            .form-row {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
            }
            
            .form-group {
                flex: 1;
                min-width: 0;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }
            
            .form-group select,
            .form-group input {
                width: 100%;
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
            
            .form-actions {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                margin-top: 20px;
            }
            
            #cancelScheduleBtn {
                background-color: #e74c3c;
            }
            
            #submitScheduleBtn {
                background-color: #27ae60;
            }
            
            .scheduled-report-card {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .scheduled-report-card h3 {
                margin-top: 0;
                margin-bottom: 10px;
            }
            
            .scheduled-report-card p {
                margin: 5px 0;
            }
            
            .cancel-schedule-btn {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            
            .loading-indicator {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
            }
            
            .error {
                color: #e74c3c;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    // Initialize when a client is selected
    function initOnClientChange() {
        const clientSelect = document.getElementById('clientSelect');
        if (clientSelect) {
            clientSelect.addEventListener('change', function() {
                // Create UI if not already created
                createScheduledReportsUI();
                
                // If a client is selected, refresh the reports
                if (this.value) {
                    loadScheduledReports();
                }
            });
            
            // If a client is already selected, create the UI
            if (clientSelect.value) {
                createScheduledReportsUI();
            }
        }
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', initOnClientChange);
    
    // Return public methods
    return {
        createUI: createScheduledReportsUI,
        loadReports: loadScheduledReports
    };
}