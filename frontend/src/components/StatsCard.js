import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

const StatsCard = ({ title, value, icon, color }) => {
    return (
        <Card elevation={2} sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ 
                        backgroundColor: `${color}20`,
                        borderRadius: 2,
                        p: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        {icon}
                    </Box>
                </Box>
                <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 1 }}>
                    {value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    {title}
                </Typography>
            </CardContent>
        </Card>
    );
};

export default StatsCard;