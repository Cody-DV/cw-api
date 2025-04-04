/**
 * CardWatch Reporting API Client
 * 
 * Provides a standardized interface for interacting with the reporting API
 */

// Get API URL from environment or use default
const API_BASE_URL = window.API_URL || 'http://localhost:5174';

/**
 * Fetch list of clients/patients
 * @returns {Promise<Array>} Array of patient objects
 */
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

/**
 * Fetch dashboard data for a specific patient
 * 
 * @param {string|number} patientId - ID of the patient
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)
 * @param {boolean} includeAnalysis - Whether to include AI analysis
 * @param {boolean} useUnifiedFormat - Whether to use the unified data format
 * @returns {Promise<Object>} Dashboard data
 */
// export async function fetchDashboardData(patientId, startDate, endDate, includeAnalysis = true) {
//     try {
//         const params = new URLSearchParams({
//             patient_id: patientId,
//             include_analysis: includeAnalysis
//         });
        
//         if (startDate) params.append('start_date', startDate);
//         if (endDate) params.append('end_date', endDate);
        
//         const response = await fetch(
//             `${API_BASE_URL}/dashboard-data?${params}`, {
//                 mode: 'cors',
//             }
//         );

//         if (!response.ok) {
//             throw new Error('Failed to fetch dashboard data');
//         }

//         return await response.json();
//     } catch (error) {
//         console.error('Error fetching dashboard data:', error);
//         throw error;
//     }
// }


/**
 * Generate a PDF report for a patient
 * 
 * @param {string|number} patientId - ID of the patient
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)ß
 * @param {Array<string>} sections - List of sßections to include
 * @param {boolean} includeAi - Whether to include AI analysis
 * @returns {Promise<Object>} Report generation result
 */
export async function generateReport(patientId, startDate, endDate, sections = null, includeAi = true) {
    try {
        const params = new URLSearchParams();
        if (patientId) params.append('patient_id', patientId);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (sections && sections.length > 0) params.append('sections', sections.join(','));
        params.append('include_ai', includeAi.toString());
        
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

/**
 * Get all reports for a patient
 * 
 * @param {string|number} patientId - ID of the patient
 * @returns {Promise<Object>} Object with patient ID and reports array
 */
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

/**
 * Send a chat message and get AI response
 * 
 * @param {string|number} patientId - ID of the patient
 * @param {string} message - The message to send
 * @param {Array} chatHistory - Previous chat history
 * @returns {Promise<Object>} Chat response
 */
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