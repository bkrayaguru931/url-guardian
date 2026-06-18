// URL validation
export const isValidUrl = (string) => {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
};

// Format timestamp
export const formatDate = (dateString) => {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
};

// Get risk level color
export const getRiskColor = (level) => {
    switch(level) {
        case 'HIGH': return '#dc3545';
        case 'MEDIUM': return '#ffc107';
        case 'LOW': return '#17a2b8';
        default: return '#28a745';
    }
};

// Truncate URL for display
export const truncateUrl = (url, maxLength = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
};

// Export scan results to CSV
export const exportToCSV = (results) => {
    const headers = ['URL', 'Is Malicious', 'Confidence Score', 'Risk Level'];
    const rows = results.map(r => [
        r.url,
        r.is_malicious,
        r.confidence_score,
        r.risk_level || 'N/A'
    ]);
    
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `url-scan-results-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
};