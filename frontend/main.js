import { fetchClients, fetchHealthData, fetchPromptResponse } from './api.js';

// DOM Elements
const clientSelect = document.getElementById('clientSelect');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const generateReportBtn = document.getElementById('generateReport');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error');
const reportContainer = document.getElementById('reportContainer');
const healthMetricsContainer = document.getElementById('healthMetrics');
const dietaryInfoContainer = document.getElementById('dietaryInfo');

// Initialize the dashboard
async function initializeDashboard() {
    try {
        const clients = await fetchClients();
        populateClientSelect(clients);
    } catch (error) {
        showError('Failed to load clients. Please try again later.');
    }
}

// Populate client select dropdown
function populateClientSelect(clients) {
    clients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = client.name;
        clientSelect.appendChild(option);
    });
}

// Generate report handler
async function generateReport() {
    const clientId = clientSelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    if (!validateInputs(clientId, startDate, endDate)) {
        return;
    }

    showLoading();
    try {
        const healthData = await fetchHealthData(clientId, startDate, endDate);
        displayReport(healthData);
    } catch (error) {
        showError('Failed to generate report. Please try again.');
    } finally {
        hideLoading();
    }
}

async function fetchAndDisplayPromptResponse() {
    showLoading();
    try {
        const promptResponse = await fetchPromptResponse();
        displayPromptResponse(promptResponse);
    } catch (error) {
        showError('Failed to fetch prompt response. Please try again.');
    } finally {
        hideLoading();
    }
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
function validateInputs(clientId, startDate, endDate) {
    if (!clientId) {
        showError('Please select a client');
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

// Display the health report
function displayReport(data) {
    reportContainer.classList.remove('hidden');
    errorElement.classList.add('hidden');

    // Display health metrics
    healthMetricsContainer.innerHTML = `
        <div class="metric-card">
            <h3>Average Heart Rate</h3>
            <p>${data.health.averageHeartRate} BPM</p>
        </div>
        <div class="metric-card">
            <h3>Average Blood Pressure</h3>
            <p>${data.health.bloodPressure.systolic}/${data.health.bloodPressure.diastolic} mmHg</p>
        </div>
        <div class="metric-card">
            <h3>Average Sleep</h3>
            <p>${data.health.averageSleep} hours</p>
        </div>
    `;

    // Display dietary information
    dietaryInfoContainer.innerHTML = `
        <div class="metric-card">
            <h3>Average Daily Calories</h3>
            <p>${data.dietary.averageCalories} kcal</p>
        </div>
        <div class="metric-card">
            <h3>Macronutrient Distribution</h3>
            <p>Protein: ${data.dietary.macros.protein}g</p>
            <p>Carbs: ${data.dietary.macros.carbs}g</p>
            <p>Fat: ${data.dietary.macros.fat}g</p>
        </div>
    `;
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

// Event Listeners
generateReportBtn.addEventListener('click', fetchAndDisplayPromptResponse);

// Initialize the dashboard when the page loads
initializeDashboard();