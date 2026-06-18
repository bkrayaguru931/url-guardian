import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Chip, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const ResultCard = ({ result }) => {
    if (!result) return null;

    const { is_malicious, risk_score, risk_level, confidence_score, reasons, url } = result;
    
    const getRiskColor = (level) => {
        switch(level) {
            case 'HIGH': return 'error';
            case 'MEDIUM': return 'warning';
            case 'LOW': return 'info';
            default: return 'success';
        }
    };

    const getRiskIcon = (level) => {
        switch(level) {
            case 'HIGH': return <ErrorIcon color="error" sx={{ fontSize: 40 }} />;
            case 'MEDIUM': return <WarningIcon color="warning" sx={{ fontSize: 40 }} />;
            default: return <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />;
        }
    };

    return (
        <Card 
            elevation={3}
            sx={{
                mt: 3,
                borderLeft: 6,
                borderColor: `${getRiskColor(risk_level)}.main`,
                backgroundColor: is_malicious ? '#fff5f5' : '#f0fff4'
            }}
        >
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getRiskIcon(risk_level)}
                    <Box sx={{ ml: 2, flex: 1 }}>
                        <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
                            {is_malicious ? '⚠️ Potential Threat Detected' : '✅ URL Appears Safe'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, wordBreak: 'break-all' }}>
                            {url}
                        </Typography>
                    </Box>
                    <Chip
                        label={risk_level}
                        color={getRiskColor(risk_level)}
                        sx={{ fontWeight: 600, fontSize: '1rem', px: 2 }}
                    />
                </Box>

                <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Risk Score</Typography>
                        <Typography variant="body2" fontWeight={600}>
                            {(risk_score * 100).toFixed(1)}%
                        </Typography>
                    </Box>
                    <LinearProgress 
                        variant="determinate" 
                        value={risk_score * 100}
                        color={getRiskColor(risk_level)}
                        sx={{ height: 10, borderRadius: 5 }}
                    />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        Confidence: {(confidence_score * 100).toFixed(1)}%
                    </Typography>
                </Box>

                {reasons && reasons.length > 0 && (
                    <Box>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                            Detection Reasons:
                        </Typography>
                        <List dense>
                            {reasons.map((reason, index) => (
                                <ListItem key={index}>
                                    <ListItemIcon sx={{ minWidth: 30 }}>
                                        <WarningIcon color="warning" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={reason} />
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default ResultCard;