import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './pages/Dashboard';

const theme = createTheme({
    palette: {
        primary: {
            main: '#667eea',
        },
        secondary: {
            main: '#764ba2',
        },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 600,
                },
            },
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Toaster 
                position="top-right"
                toastOptions={{
                    duration: 3000,
                    style: {
                        borderRadius: '10px',
                        background: '#333',
                        color: '#fff',
                    },
                }}
            />
            <Router>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                </Routes>
            </Router>
        </ThemeProvider>
    );
}

export default App;