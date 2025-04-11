import { fetchClients, generateReport, sendChatMessage, getPatientReports } from './api.js';
import { marked } from 'https://cdn.jsdelivr.net/npm/marked@9.0.3/lib/marked.esm.js';

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

// Download PDF report with customization options
async function downloadReport() {
    const patientId = clientSelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;


    const sections = [
        { id: 'calories', name: 'Calories' },
        { id: 'macronutrients', name: 'Macronutrients' },
        { id: 'food_consumed', name: 'Food Consumed' },
        { id: 'food_group_recommendations', name: 'Food Group Recommendations' },
        { id: 'nutrient_intake', name: 'Nutrient Intake' },
        { id: 'ai_analysis', name: 'AI Nutritional Analysis' },
        { id: 'summary', name: 'Summary' }
    ];

    showLoading();
    
    try {
        const result = await generateReport(patientId, startDate, endDate, sections);
        
        // Show success message with more details
        const fileFormat = result.format || 'pdf';
        const title = fileFormat === 'html' ? 'HTML Report Generated' : 'PDF Report Generated';
        const message = `
            ${title} Successfully
            
            Filename: ${result.file}
            Format: ${fileFormat.toUpperCase()}
            ${result.sections_included ? `Sections included: ${result.sections_included.join(', ')}` : ''}
            
            Renderer: ${result.renderer || 'standard'}
            
            The report has been saved to the server.
            You can access it at: ${result.path}
        `;
        
        loadReportIframe(result.file)
        
        // After generating a report, fetch and display the patient's reports
        await loadPatientReports(patientId);
    } catch (error) {
        showError('Failed to generate PDF report. Please try again.');
    } finally {
        hideLoading();
    }
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
        // Example date: "generated_at": "20250406_011246",
        const dateString = report.generated_at;
        
        const year = dateString.slice(0, 4);
        const month = dateString.slice(4, 6);
        const day = dateString.slice(6, 8);
        const hour = dateString.slice(9, 11);
        const minute = dateString.slice(11, 13);
        const second = dateString.slice(13, 15);
    
        // Create a Date object
        const formattedDate = `${year}-${month}-${day} ${hour}:${minute}:${second}`;

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
                <button class="download-button" data-filename="${report.filename}" data-format="${'html'}">
                    View Report
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

// Display the report
function displayReport(data) {
    reportContainer.classList.remove('hidden');
    errorElement.classList.add('hidden');
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

    // Convert markdown content to HTML
    const htmlContent = marked(content);

    messageDiv.innerHTML = `
        <div class="message-sender">${senderName}</div>
        <div class="message-content">${htmlContent}</div>
    `;

    // Append to chat
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


function loadReportIframe(filename, format = 'html') {
    const iframe = document.getElementById('report-iframe');

    if (format === 'pdf') {
        iframe.src = `http://localhost:5174/reports/${filename}`;
    } else {
        iframe.src = `http://localhost:5174/reports/${filename.replace('.pdf', '.html')}`;
    }

    iframe.style.display = 'block';
    iframe.scrollIntoView({ behavior: 'smooth' });

    console.log("Iframe SRC:", iframe.src);
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
generateReportBtn.addEventListener('click', downloadReport);
downloadPdfBtn.addEventListener('click', displayReport);

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

        // Hide the iframe when changing patients
        const iframe = document.getElementById('report-iframe');
        if (iframe) {
            iframe.style.display = 'none';
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('download-button')) {
            const filename = event.target.getAttribute('data-filename');
            loadReportIframe(filename, 'html'); // or 'pdf' if needed
        }
    });
});

document.getElementById('edit-report-button').addEventListener('click', () => {
    const iframe = document.getElementById('report-iframe');

    iframe.contentWindow.postMessage({ type: 'enable-edit-mode' }, '*');
});

window.addEventListener('message', async (event) => {
    if (event.data?.type === 'save-ai-edits') {
        const updatedFields = event.data.data;

        const response = await fetch('/api/update-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patientId: currentPatientId,
                updatedAiSections: updatedFields
            })
        });

        if (response.ok) {
            // Regenerate and reload report
            const iframe = document.getElementById('report-iframe');
            iframe.src = iframe.src; // reload the same report
        }
    }
});

