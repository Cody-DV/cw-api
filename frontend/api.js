const API_BASE_URL = 'http://localhost:5174';

// Fetch list of clients
export async function fetchClients() {
    try {
        const response = await fetch(`${API_BASE_URL}/clients`, {
            mode: 'cors',
        });
        if (!response.ok) {
            throw new Error('Failed to fetch clients');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching clients:', error);
        throw error;
    }
}

// Send a chat message and get AI response
export async function sendChatMessage(patientId, message, chatHistory = []) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: patientId,
                message,
                chat_history: chatHistory
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to send chat message');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error sending chat message:', error);
        throw error;
    }
}

// Fetch dashboard data for a specific patient and date range
export async function fetchDashboardData(patientId, startDate, endDate, includeAnalysis = true) {
    try {
        const params = new URLSearchParams({
            patient_id: patientId,
            include_analysis: includeAnalysis
        });
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(
            `${API_BASE_URL}/dashboard-data?${params}`, {
                mode: 'cors',
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        throw error;
    }
}

// Fetch health data for a specific client and date range (legacy endpoint)
export async function fetchHealthData(clientId, startDate, endDate) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/health-data?` +
            new URLSearchParams({
                clientId,
                startDate,
                endDate
            }), {
                mode: 'cors',
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch health data');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching health data:', error);
        throw error;
    }
}

export async function fetchPromptResponse() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/prompt`, {
                mode: 'cors',
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch prompt response');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching prompt response:', error);
        throw error;
    }
}

// Generate PDF report
export async function generatePdfReport(patientId, startDate, endDate, sections = null, includeAi = true) {
    try {
        const params = new URLSearchParams();
        if (patientId) params.append('patient_id', patientId);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (sections && sections.length > 0) params.append('sections', sections.join(','));
        params.append('include_ai', includeAi.toString());  // Add the includeAi parameter
        
        const response = await fetch(
            `${API_BASE_URL}/generate-report?${params}`, {
                mode: 'cors',
            }
        );

        if (!response.ok) {
            throw new Error('Failed to generate PDF report');
        }

        return await response.json();
    } catch (error) {
        console.error('Error generating PDF report:', error);
        throw error;
    }
}

// Get patient's previously generated reports
export async function getPatientReports(patientId) {
    try {
        const params = new URLSearchParams({
            patient_id: patientId
        });
        
        const response = await fetch(
            `${API_BASE_URL}/get-patient-reports?${params}`, {
                mode: 'cors',
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch patient reports');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching patient reports:', error);
        throw error;
    }
}
