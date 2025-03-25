import { fetchClients, fetchDashboardData, generatePdfReport, sendChatMessage, getPatientReports } from './api.js';

// DOM Elements
const clientSelect = document.getElementById('clientSelect');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const generateReportBtn = document.getElementById('generateReport');
const downloadPdfBtn = document.createElement('button');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error');
const reportContainer = document.getElementById('reportContainer');
const healthMetricsContainer = document.getElementById('healthMetrics');
const dietaryInfoContainer = document.getElementById('dietaryInfo');

// Chat Elements
const toggleChatBtn = document.getElementById('toggleChatBtn');
const chatInterface = document.getElementById('chatInterface');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const quickQuestionBtns = document.querySelectorAll('.quick-question-btn');

// Set up download PDF button
downloadPdfBtn.textContent = 'Download PDF Report';
downloadPdfBtn.classList.add('pdf-download-btn');
downloadPdfBtn.style.marginLeft = '10px';
downloadPdfBtn.style.backgroundColor = '#e74c3c';
generateReportBtn.parentNode.appendChild(downloadPdfBtn);
downloadPdfBtn.classList.add('hidden');

// Initialize the dashboard
async function initializeDashboard() {
    try {
        const clients = await fetchClients();

        populateClientSelect(clients);
        
        // Set default dates to current month
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        
        // Format dates as YYYY-MM-DD
        startDateInput.value = formatDate(firstDay);
        endDateInput.value = formatDate(today);
        
    } catch (error) {
        showError('Failed to load clients. Please try again later.');
    }
}

// Helper function to format date as YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Populate client select dropdown
function populateClientSelect(clients) {
    clients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = `${client.first_name} ${client.last_name}` || `Patient ${client.id}`;
        clientSelect.appendChild(option);
    });
}

// Generate dashboard data and display it
async function generateDashboard() {
    const patientId = clientSelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    if (!validateInputs(patientId, startDate, endDate)) {
        return;
    }

    showLoading();
    // Fall back to the legacy dashboard data as last resort
    try {
        const dashboardData = await fetchDashboardData(patientId, startDate, endDate);
        console.log("Dashboard data generateDashboardData", dashboardData)
        displayDashboard(dashboardData);
        downloadPdfBtn.classList.remove('hidden');
    } catch (fallbackError) {
        showError('Failed to generate dashboard. Please try again.');
        downloadPdfBtn.classList.add('hidden');
    } finally {
        hideLoading();
    }
}

// Download PDF report with customization options
async function downloadPdfReport() {
    const patientId = clientSelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    // Show the report customization dialog
    const reportOptions = await showReportCustomizationDialog();
    if (!reportOptions) {
        // User cancelled the dialog
        return;
    }

    // Extract sections and includeAi from options
    const { sections, includeAi } = reportOptions;

    showLoading();
    
    try {
        // Generate a PDF report using the same unified data format for consistency
        // The same data used in the dashboard will be used for the PDF
        const result = await generatePdfReport(patientId, startDate, endDate, sections, includeAi);
        
        // Show success message with more details
        const fileFormat = result.format || 'pdf';
        const title = fileFormat === 'html' ? 'HTML Report Generated' : 'PDF Report Generated';
        const message = `
            ${title} Successfully
            
            Filename: ${result.file}
            Format: ${fileFormat.toUpperCase()}
            ${result.sections_included ? `Sections included: ${result.sections_included.join(', ')}` : ''}
            AI content included: ${includeAi ? 'Yes' : 'No'}
            Renderer: ${result.renderer || 'standard'}
            
            The report has been saved to the server.
            You can access it at: ${result.path}
        `;
        
        showSuccessMessage('Report Generated!', message);
        
        // After generating a report, fetch and display the patient's reports
        await loadPatientReports(patientId);
    } catch (error) {
        showError('Failed to generate PDF report. Please try again.');
    } finally {
        hideLoading();
    }
}

// Show report customization dialog
function showReportCustomizationDialog() {
    return new Promise((resolve) => {
        // Create modal backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        document.body.appendChild(backdrop);
        
        // Create modal dialog
        const modal = document.createElement('div');
        modal.className = 'modal-dialog';
        
        // Available sections
        const availableSections = [
            { id: 'calories', name: 'Calories' },
            { id: 'macronutrients', name: 'Macronutrients' },
            { id: 'food_consumed', name: 'Food Consumed' },
            { id: 'food_group_recommendations', name: 'Food Group Recommendations' },
            { id: 'nutrient_intake', name: 'Nutrient Intake' },
            { id: 'ai_analysis', name: 'AI Nutritional Analysis' },
            { id: 'summary', name: 'Summary' }
        ];
        
        // Modal content
        modal.innerHTML = `
            <div class="modal-header">
                <h3>Customize Report</h3>
            </div>
            <div class="modal-body">
                <p>Select the sections to include in your report:</p>
                <div class="checkbox-list">
                    ${availableSections.map(section => `
                        <div class="checkbox-item">
                            <input type="checkbox" id="${section.id}" value="${section.id}" checked>
                            <label for="${section.id}">${section.name}</label>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="modal-footer">
                <button class="cancel-button">Cancel</button>
                <button class="generate-button">Generate Report</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        const closeButton = modal.querySelector('.close-button');
        const cancelButton = modal.querySelector('.cancel-button');
        const generateButton = modal.querySelector('.generate-button');
        
        // Close/cancel handlers
        const closeModal = () => {
            document.body.removeChild(backdrop);
            document.body.removeChild(modal);
            resolve(null);
        };
        
        // closeButton.addEventListener('click', closeModal);
        cancelButton.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);
        
        // Generate handler
        generateButton.addEventListener('click', () => {
            const checkboxes = modal.querySelectorAll('input[type="checkbox"]:checked');
            
            // Filter out the include_ai checkbox which isn't a section
            const selectedSections = Array.from(checkboxes)
                .filter(cb => cb.id !== 'include_ai')
                .map(cb => cb.value);
            
            document.body.removeChild(backdrop);
            document.body.removeChild(modal);
            
            // Return both the sections and the includeAi flag
            resolve({
                sections: selectedSections,
            });
        });
        
        // Add modal styles dynamically if not already added
        if (!document.getElementById('modal-styles')) {
            const modalStyles = document.createElement('style');
            modalStyles.id = 'modal-styles';
            modalStyles.textContent = `
                .modal-backdrop {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                }
                
                .modal-dialog {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                    width: 500px;
                    max-width: 90%;
                    z-index: 1001;
                }
                
                .modal-header {
                    padding: 15px;
                    border-bottom: 1px solid #ddd;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .modal-header h3 {
                    margin: 0;
                }
                
                .close-button {
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                }
                
                .modal-body {
                    padding: 15px;
                    overflow-y: auto;
                }
                
                .checkbox-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .checkbox-item {
                    display: flex;
                    align-items: center; /* Aligns items vertically in the center */
                    margin-bottom: 5px; /* Consistent spacing between checkbox items */
                }
                
                .checkbox-item input {
                    margin-right: 10px; /* Space out the checkbox from its label */
                    max-width: fit-content;
                }
                
                .modal-footer {
                    padding: 15px;
                    border-top: 1px solid #ddd;
                    display: flex;
                    justify-content: flex-end;
                    gap: 10px;
                }
                
                .cancel-button {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                .generate-button {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(modalStyles);
        }
    });
}

// Show success message
function showSuccessMessage(title, message) {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    document.body.appendChild(backdrop);
    
    const modal = document.createElement('div');
    modal.className = 'modal-dialog';
    modal.innerHTML = `
        <div class="modal-header">
            <h3>${title}</h3>
            <button class="close-button">&times;</button>
        </div>
        <div class="modal-body">
            <pre class="success-message">${message}</pre>
        </div>
        <div class="modal-footer">
            <button class="ok-button">OK</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add styles for success message
    if (!document.getElementById('success-message-styles')) {
        const styles = document.createElement('style');
        styles.id = 'success-message-styles';
        styles.textContent = `
            .success-message {
                white-space: pre-wrap;
                word-wrap: break-word;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                border-left: 4px solid #2ecc71;
                font-family: monospace;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .ok-button {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
        `;
        document.head.appendChild(styles);
    }
    
    const closeModal = () => {
        document.body.removeChild(backdrop);
        document.body.removeChild(modal);
    };
    
    modal.querySelector('.close-button').addEventListener('click', closeModal);
    modal.querySelector('.ok-button').addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);
}

// Load patient's previous reports
async function loadPatientReports(patientId) {
    if (!patientId) return;
    
    try {
        const { reports } = await getPatientReports(patientId);
        
        // Display reports if there are any
        if (reports && reports.length > 0) {
            displayPreviousReports(reports);
        }
    } catch (error) {
        console.error('Error loading patient reports:', error);
    }
}

// Display previous reports
function displayPreviousReports(reports) {
    // Create or get the previous reports container
    let reportsSection = document.getElementById('previousReports');
    
    if (!reportsSection) {
        reportsSection = document.createElement('div');
        reportsSection.id = 'previousReports';
        reportsSection.className = 'report-section';
        
        // Add header
        const header = document.createElement('h2');
        header.textContent = 'Previous Reports';
        reportsSection.appendChild(header);
        
        // Create container for report list
        const reportsContainer = document.createElement('div');
        reportsContainer.id = 'reportsContainer';
        reportsSection.appendChild(reportsContainer);
        
        // Add the section to the page
        const dashboardContent = document.querySelector('.dashboard-content');
        dashboardContent.appendChild(reportsSection);
    }
    
    // Get the reports container
    const reportsContainer = document.getElementById('reportsContainer');
    
    // Clear existing content
    reportsContainer.innerHTML = '';
    
    // Add each report as a card
    reports.forEach(report => {
        const reportCard = document.createElement('div');
        reportCard.className = 'report-card';
        
        // Format the date for display
        const generatedDate = new Date(report.generated_at);
        const formattedDate = generatedDate.toLocaleString();
        
        // Create date range text
        const dateRange = report.date_range && (report.date_range.start || report.date_range.end)
            ? `<p><strong>Period:</strong> ${report.date_range.start || 'N/A'} to ${report.date_range.end || 'N/A'}</p>`
            : '';
        
        reportCard.innerHTML = `
            <div class="report-info">
                <h3>Report: ${report.report_type}</h3>
                <p><strong>Generated:</strong> ${formattedDate}</p>
                ${dateRange}
                <p><strong>Filename:</strong> ${report.filename}</p>
            </div>
            <div class="report-actions">
                <button class="download-button" data-filename="${report.filename}" data-format="${report.format || 'pdf'}">
                    ${report.format === 'html' ? 'View HTML' : 'View PDF'}
                </button>
            </div>
        `;
        
        reportsContainer.appendChild(reportCard);
    });
    
    // Add styles for report cards
    if (!document.getElementById('report-card-styles')) {
        const styles = document.createElement('style');
        styles.id = 'report-card-styles';
        styles.textContent = `
            #previousReports {
                margin-top: 30px;
            }
            
            .report-card {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .report-card h3 {
                margin-top: 0;
                margin-bottom: 10px;
            }
            
            .report-card p {
                margin: 5px 0;
            }
            
            .download-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Make the section visible
    reportsSection.classList.remove('hidden');
}

function displayPromptResponse(data) {
    reportContainer.classList.remove('hidden');
    errorElement.classList.add('hidden');

    // Display prompt response data as text
    dietaryInfoContainer.innerHTML = `
        <div class="metric-card">
            <div>
                <h3>Prompt Response</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        </div>
    `;
}

// Validate user inputs
function validateInputs(patientId, startDate, endDate) {
    if (!patientId) {
        showError('Please select a patient');
        return false;
    }
    if (!startDate || !endDate) {
        showError('Please select both start and end dates');
        return false;
    }
    if (new Date(startDate) > new Date(endDate)) {
        showError('Start date must be before end date');
        return false;
    }
    return true;
}

// Display the dashboard data
function displayDashboard(data) {
    reportContainer.classList.remove('hidden');
    errorElement.classList.add('hidden');

    // Display patient information
    const patientInfo = data.patient || {};
    const allergyList = patientInfo.allergies && patientInfo.allergies.length 
        ? `<p><strong>Allergies:</strong> ${patientInfo.allergies.join(', ')}</p>` 
        : '<p><strong>Allergies:</strong> None recorded</p>';
    
    healthMetricsContainer.innerHTML = `
        <div class="metric-card">
            <h3>Patient Information</h3>
            <p><strong>Name:</strong> ${patientInfo.name || 'N/A'}</p>
            <p><strong>Age:</strong> ${patientInfo.age || 'N/A'}</p>
            ${allergyList}
        </div>
    `;

    // Display nutrient information
    const nutrients = data.nutrients || {};
    const nutrientHtml = Object.entries(nutrients).map(([nutrient, values]) => `
        <div class="metric-card">
            <h3>${nutrient.charAt(0).toUpperCase() + nutrient.slice(1)}</h3>
            <p><strong>Target:</strong> ${values.target || 0}</p>
            <p><strong>Actual:</strong> ${values.actual || 0}</p>
            <div class="progress-bar">
                <div class="progress" style="width: ${calculatePercentage(values.actual, values.target)}%"></div>
            </div>
            <p class="percentage">${calculatePercentage(values.actual, values.target)}%</p>
        </div>
    `).join('');

    // Display food items
    const foodItems = data.food_items || [];
    const foodItemsHtml = foodItems.length ? foodItems.map(item => `
        <tr>
            <td>${item.name || 'Unknown'}</td>
            <td>${item.quantity || 1}</td>
            <td>${item.date || 'N/A'}</td>
        </tr>
    `).join('') : '<tr><td colspan="3">No food items recorded</td></tr>';

    // Summary
    const summary = data.summary || {};
    
    // AI Analysis Section HTML
    let aiAnalysisHtml = '';
    if (data.ai_analysis) {
        const analysis = data.ai_analysis;
        aiAnalysisHtml = `
            <div class="ai-analysis-section">
                <h3>AI Nutritional Analysis</h3>
                <div class="ai-analysis-content">
                    ${analysis.SUMMARY ? `
                        <div class="analysis-card">
                            <h4>Summary</h4>
                            <p>${analysis.SUMMARY}</p>
                        </div>
                    ` : ''}
                    
                    ${analysis.ANALYSIS ? `
                        <div class="analysis-card">
                            <h4>Detailed Analysis</h4>
                            <p>${analysis.ANALYSIS}</p>
                        </div>
                    ` : ''}
                    
                    ${analysis.RECOMMENDATIONS ? `
                        <div class="analysis-card">
                            <h4>Recommendations</h4>
                            <p>${analysis.RECOMMENDATIONS}</p>
                        </div>
                    ` : ''}
                    
                    ${analysis.HEALTH_INSIGHTS ? `
                        <div class="analysis-card">
                            <h4>Health Insights</h4>
                            <p>${analysis.HEALTH_INSIGHTS}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    dietaryInfoContainer.innerHTML = `
        <div class="report-grid">
            <div class="nutrients-section">
                <h3>Nutrient Information</h3>
                <div class="nutrient-cards">
                    ${nutrientHtml || '<p>No nutrient data available</p>'}
                </div>
            </div>
            
            <div class="food-items-section">
                <h3>Food Items Consumed</h3>
                <p>Total Items: ${summary.total_items_consumed || 0}</p>
                <p>Total Calories: ${summary.total_calories || 0}</p>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Quantity</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${foodItemsHtml}
                        </tbody>
                    </table>
                </div>
            </div>
            
            ${aiAnalysisHtml}
        </div>
    `;

    // Add CSS for the new elements
    addDashboardStyles();
}

// Calculate percentage for progress bars
function calculatePercentage(actual, target) {
    if (!target || !actual) return 0;
    const percentage = (actual / target) * 100;
    return Math.min(Math.round(percentage), 100); // Cap at 100%
}

// Add dynamic styles for dashboard
function addDashboardStyles() {
    // Check if styles already exist
    if (!document.getElementById('dashboard-dynamic-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'dashboard-dynamic-styles';
        styleElement.textContent = `
            .report-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            @media (min-width: 768px) {
                .report-grid {
                    grid-template-columns: 1fr 1fr;
                }
            }
            
            .nutrient-cards {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .progress-bar {
                height: 10px;
                background-color: #f1f1f1;
                border-radius: 5px;
                margin: 5px 0;
            }
            
            .progress {
                height: 100%;
                background-color: #3498db;
                border-radius: 5px;
            }
            
            .percentage {
                font-size: 0.9rem;
                text-align: right;
                margin: 0;
            }
            
            .table-container {
                max-height: 300px;
                overflow-y: auto;
                margin-top: 10px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
            }
            
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            
            th {
                background-color: #f2f2f2;
                position: sticky;
                top: 0;
            }
            
            tr:hover {
                background-color: #f5f5f5;
            }
            
            /* AI Analysis Styles */
            .ai-analysis-section {
                grid-column: 1 / -1;
                margin-top: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .ai-analysis-content {
                display: grid;
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            @media (min-width: 768px) {
                .ai-analysis-content {
                    grid-template-columns: 1fr 1fr;
                }
            }
            
            .analysis-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .analysis-card h4 {
                color: #3498db;
                margin-top: 0;
                margin-bottom: 10px;
                border-bottom: 1px solid #f1f1f1;
                padding-bottom: 5px;
            }
            
            .analysis-card p {
                margin: 0;
                line-height: 1.5;
            }
        `;
        document.head.appendChild(styleElement);
    }
}

// UI Helper functions
function showLoading() {
    loadingElement.classList.remove('hidden');
    reportContainer.classList.add('hidden');
}

function hideLoading() {
    loadingElement.classList.add('hidden');
}

function showError(message) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

// Chat state
let chatHistory = [];
let isTyping = false;

// Chat functions
function toggleChat() {
    chatInterface.classList.toggle('hidden');
    toggleChatBtn.textContent = chatInterface.classList.contains('hidden') ? 'Open Chat' : 'Close Chat';
    
    // If opening chat and no messages yet, show a welcome message
    if (!chatInterface.classList.contains('hidden') && chatMessages.children.length === 0) {
        addSystemMessage("Hello! I'm your AI nutrition assistant. How can I help you analyze this patient's data?");
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const senderName = role === 'user' ? 'You' : 'AI Nutritionist';
    messageDiv.innerHTML = `
        <div class="message-sender">${senderName}</div>
        <div class="message-content">${content}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.innerHTML = `
        <div class="message-sender">CardWatch AI</div>
        <div class="message-content">${content}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = `
        <span></span><span></span><span></span>
    `;
    
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    isTyping = false;
    const indicator = chatMessages.querySelector('.typing-indicator');
    if (indicator) {
        chatMessages.removeChild(indicator);
    }
}

async function sendMessage(message) {
    if (!message.trim()) return;
    
    const patientId = clientSelect.value;
    if (!patientId) {
        showError('Please select a patient before starting a chat');
        return;
    }
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input field
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to API
        const response = await sendChatMessage(patientId, message, chatHistory);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add AI response to chat
        addMessage('assistant', response.response);
        
        // Update chat history
        chatHistory = response.chat_history;
    } catch (error) {
        hideTypingIndicator();
        addSystemMessage(`Error: ${error.message || 'Failed to get response'}`);
        console.error('Error sending message:', error);
    }
}

// Event listener for the toggle chat button
toggleChatBtn.addEventListener('click', toggleChat);

// Event listener for the send button
sendChatBtn.addEventListener('click', () => {
    sendMessage(chatInput.value);
});

// Function to handle chat integration with the iframe report
function setupChatReportIntegration() {
    // This will be used to integrate chat with the iframe report in the future
    // For now, we'll just update the chat section to mention the connection
    
    const chatHeader = document.querySelector('.chat-header h2');
    if (chatHeader) {
        chatHeader.textContent = 'Ask the AI Nutritionist about this Report';
    }
    
    const quickQuestions = document.querySelectorAll('.quick-question-btn');
    if (quickQuestions.length > 0) {
        // Update quick questions to be more report-specific
        const questions = [
            {
                button: quickQuestions[0],
                question: "What does this report tell me about my nutrition?"
            },
            {
                button: quickQuestions[1], 
                question: "How can I improve my macronutrient balance?"
            },
            {
                button: quickQuestions[2],
                question: "What's the most concerning part of this report?"
            },
            {
                button: quickQuestions[3],
                question: "Can you suggest a meal plan based on this report?"
            },
            {
                button: quickQuestions[4],
                question: "What nutritional deficiencies does this report suggest?"
            },
            {
                button: quickQuestions[5],
                question: "How do I reach my nutritional targets shown in this report?"
            }
        ];
        
        // Update the quick questions
        questions.forEach(item => {
            if (item.button) {
                item.button.setAttribute('data-question', item.question);
                item.button.textContent = item.question.split('?')[0] + '?';
            }
        });
    }
}

// Event listener for the enter key in chat input
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

// Event listeners for quick question buttons
quickQuestionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        if (question) {
            chatInput.value = question;
            sendMessage(question);
        }
    });
});

// Event Listeners
generateReportBtn.addEventListener('click', generateDashboard);
downloadPdfBtn.addEventListener('click', downloadPdfReport);

// Initialize the dashboard when the page loads
initializeDashboard();

// Add event listener to load patient reports when a patient is selected
clientSelect.addEventListener('change', () => {
    const patientId = clientSelect.value;
    if (patientId) {
        loadPatientReports(patientId);
        // Reset chat when patient changes
        chatHistory = [];
        chatMessages.innerHTML = '';
    }
});