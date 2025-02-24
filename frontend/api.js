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

// Fetch health data for a specific client and date range
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
