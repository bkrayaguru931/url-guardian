import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Tabs, Tab } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import URLInput from '../components/URLInput';
import ResultCard from '../components/ResultCard';
import StatsCard from '../components/StatsCard';
import BatchChecker from '../components/BatchChecker';
import { urlService } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({
        totalScans: 0,
        threatsDetected: 0,
        avgResponseTime: 0,
        accuracy: 0
    });
    const [tabValue, setTabValue] = useState(0);

    useEffect(() => {
        fetchStats();
        // Refresh stats every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async () => {
        try {
            const response = await urlService.getHistory(100);
            const scans = response.data;
            const maliciousCount = scans.filter(s => s.is_malicious).length;
            
            setStats({
                totalScans: scans.length,
                threatsDetected: maliciousCount,
                avgResponseTime: 45, // ms (mock)
                accuracy: maliciousCount > 0 ? ((maliciousCount / scans.length) * 100).toFixed(1) : 100
            });
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    };

    const handleUrlCheck = async (url) => {
        setLoading(true);
        try {
            const response = await urlService.checkUrl(url);
            setResult(response.data);
            toast.success('Analysis complete!');
            fetchStats(); // Refresh stats
        } catch (error) {
            toast.error('Failed to analyze URL');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4, textAlign: 'center' }}>
                <Typography 
                    variant="h3" 
                    component="h1" 
                    sx={{ 
                        fontWeight: 700, 
                        mb: 1,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}
                >
                    🛡️ URL Guardian
                </Typography>
                <Typography variant="h6" color="text.secondary">
                    Advanced URL Threat Detection System
                </Typography>
            </Box>

            {/* Stats Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Total Scans"
                        value={stats.totalScans}
                        icon={<ShieldIcon sx={{ color: '#667eea' }} />}
                        color="#667eea"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Threats Detected"
                        value={stats.threatsDetected}
                        icon={<SecurityIcon sx={{ color: '#dc3545' }} />}
                        color="#dc3545"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Avg Response Time"
                        value={`${stats.avgResponseTime}ms`}
                        icon={<SpeedIcon sx={{ color: '#28a745' }} />}
                        color="#28a745"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Detection Rate"
                        value={`${stats.accuracy}%`}
                        icon={<TrendingUpIcon sx={{ color: '#ffc107' }} />}
                        color="#ffc107"
                    />
                </Grid>
            </Grid>

            {/* Main Content */}
            <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
                <Tabs 
                    value={tabValue} 
                    onChange={(e, v) => setTabValue(v)}
                    sx={{ mb: 3 }}
                >
                    <Tab label="Single URL Check" />
                    <Tab label="Batch Analysis" />
                </Tabs>

                {tabValue === 0 && (
                    <Box>
                        <URLInput onSubmit={handleUrlCheck} loading={loading} />
                        <ResultCard result={result} />
                    </Box>
                )}

                {tabValue === 1 && (
                    <BatchChecker onComplete={fetchStats} />
                )}
            </Paper>
        </Container>
    );
};

export default Dashboard;