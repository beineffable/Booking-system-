import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import MemberDashboard from './pages/MemberDashboard';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './styles/theme';

// Create MUI theme from our custom theme configuration
const muiTheme = createTheme({
  palette: {
    primary: {
      main: theme.colors.primary.main,
      light: theme.colors.primary.light,
      dark: theme.colors.primary.dark,
      contrastText: theme.colors.primary.contrastText,
    },
    secondary: {
      main: theme.colors.secondary.main,
      light: theme.colors.secondary.light,
      dark: theme.colors.secondary.dark,
      contrastText: theme.colors.secondary.contrastText,
    },
    background: {
      default: theme.colors.background.default,
      paper: theme.colors.background.paper,
    },
    text: {
      primary: theme.colors.text.primary,
      secondary: theme.colors.text.secondary,
    },
  },
  typography: {
    fontFamily: theme.typography.fontFamily,
    fontWeightLight: theme.typography.fontWeights.light,
    fontWeightRegular: theme.typography.fontWeights.regular,
    fontWeightMedium: theme.typography.fontWeights.medium,
    fontWeightBold: theme.typography.fontWeights.bold,
  },
  shape: {
    borderRadius: parseInt(theme.borderRadius.md),
  },
  shadows: [
    'none',
    theme.shadows.sm,
    theme.shadows.md,
    theme.shadows.lg,
    theme.shadows.xl,
    ...Array(20).fill(theme.shadows.xl), // Fill remaining shadows
  ],
});

function App() {
  // Mock authentication state for demonstration
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? 
                <MemberDashboard /> : 
                <Navigate to="/login" replace />
            } 
          />
          {/* Add more routes as needed */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
