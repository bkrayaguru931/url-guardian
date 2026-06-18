import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for API key
api.interceptors.request.use(
    (config) => {
        const apiKey = localStorage.getItem('api_key');
        if (apiKey) {
            config.headers['X-API-Key'] = apiKey;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            switch (error.response.status) {
                case 429:
                    console.error('Rate limit exceeded');
                    break;
                case 401:
                    console.error('Invalid API key');
                    break;
                default:
                    console.error('API Error:', error.response.data);
            }
        }
        return Promise.reject(error);
    }
);

export const urlService = {
    // Check single URL
    checkUrl: (url) => api.post('/url/check', { url }),
    
    // Check multiple URLs
    checkBatch: (urls) => api.post('/batch/check', { urls }),
    
    // Get scan history
    getHistory: (limit = 10) => api.get('/url/history', { params: { limit } }),
    
    // Get API usage statistics
    getStats: () => api.get('/stats'),
};

export default api;