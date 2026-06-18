import React, { useState } from 'react';
import { TextField, Button, CircularProgress, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const URLInput = ({ onSubmit, loading }) => {
    const [url, setUrl] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (url.trim()) {
            onSubmit(url.trim());
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2 }}>
            <TextField
                fullWidth
                variant="outlined"
                placeholder="Enter URL to analyze (e.g., https://example.com)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                sx={{
                    '& .MuiOutlinedInput-root': {
                        backgroundColor: 'white',
                        borderRadius: 2,
                    }
                }}
            />
            <Button
                type="submit"
                variant="contained"
                disabled={loading || !url.trim()}
                sx={{
                    minWidth: 150,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                        background: 'linear-gradient(135deg, #5568d3 0%, #63408b 100%)',
                    }
                }}
            >
                {loading ? <CircularProgress size={24} color="inherit" /> : <><SearchIcon sx={{ mr: 1 }} /> Analyze</>}
            </Button>
        </Box>
    );
};

export default URLInput;