import React, { useState } from 'react';
import { 
    Box, TextField, Button, CircularProgress, 
    List, ListItem, ListItemIcon, ListItemText, 
    Chip, Typography 
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import { urlService } from '../services/api';
import toast from 'react-hot-toast';

const BatchChecker = ({ onComplete }) => {
    const [urls, setUrls] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleBatchCheck = async () => {
        const urlList = urls.split('\n').filter(url => url.trim());
        
        if (urlList.length === 0) {
            toast.error('Please enter at least one URL');
            return;
        }
        
        if (urlList.length > 50) {
            toast.error('Maximum 50 URLs allowed per batch');
            return;
        }

        setLoading(true);
        try {
            const response = await urlService.checkBatch(urlList);
            setResults(response.data);
            toast.success(`Analyzed ${urlList.length} URLs successfully!`);
            if (onComplete) onComplete();
        } catch (error) {
            toast.error('Batch analysis failed');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (isMalicious) => {
        if (isMalicious) {
            return <ErrorIcon color="error" />;
        }
        return <CheckCircleIcon color="success" />;
    };

    const getRiskColor = (score) => {
        if (score >= 0.7) return 'error';
        if (score >= 0.4) return 'warning';
        return 'success';
    };

    return (
        <Box>
            <TextField
                fullWidth
                multiline
                rows={6}
                variant="outlined"
                placeholder={"Enter multiple URLs (one per line):\nhttps://google.com\nhttp://suspicious-site.tk/login\nhttps://github.com"}
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                disabled={loading}
                sx={{ 
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                        backgroundColor: 'white',
                        fontFamily: 'monospace',
                    }
                }}
            />
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3 }}>
                <Button
                    variant="contained"
                    onClick={handleBatchCheck}
                    disabled={loading || !urls.trim()}
                    sx={{
                        minWidth: 200,
                        borderRadius: 2,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #5568d3 0%, #63408b 100%)',
                        }
                    }}
                >
                    {loading ? (
                        <CircularProgress size={24} color="inherit" />
                    ) : (
                        'Analyze All URLs'
                    )}
                </Button>
                
                {results.length > 0 && (
                    <Typography variant="body2" color="text.secondary">
                        {results.length} URLs analyzed • 
                        {results.filter(r => r.is_malicious).length} threats detected
                    </Typography>
                )}
            </Box>

            {results.length > 0 && (
                <List>
                    {results.map((result, index) => (
                        <ListItem 
                            key={index}
                            sx={{
                                mb: 1,
                                backgroundColor: result.is_malicious ? '#fff5f5' : '#f0fff4',
                                borderRadius: 2,
                                border: '1px solid',
                                borderColor: result.is_malicious ? '#ffcdd2' : '#c8e6c9',
                                flexDirection: 'column',
                                alignItems: 'stretch',
                                p: 2
                            }}
                        >
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <ListItemIcon sx={{ minWidth: 40 }}>
                                    {getStatusIcon(result.is_malicious)}
                                </ListItemIcon>
                                <ListItemText 
                                    primary={
                                        <Typography 
                                            variant="body2" 
                                            sx={{ 
                                                fontFamily: 'monospace', 
                                                wordBreak: 'break-all',
                                                fontWeight: 500
                                            }}
                                        >
                                            {result.url}
                                        </Typography>
                                    }
                                    sx={{ flex: 1 }}
                                />
                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', ml: 2 }}>
                                    <Chip
                                        label={result.is_malicious ? 'MALICIOUS' : 'SAFE'}
                                        color={result.is_malicious ? 'error' : 'success'}
                                        size="small"
                                        sx={{ fontWeight: 600 }}
                                    />
                                    <Typography variant="body2" color="text.secondary">
                                        {(result.confidence_score * 100).toFixed(1)}% confidence
                                    </Typography>
                                </Box>
                            </Box>
                        </ListItem>
                    ))}
                </List>
            )}
        </Box>
    );
};

export default BatchChecker;