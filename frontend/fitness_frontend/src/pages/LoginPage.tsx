import React from 'react';
import { styled } from '@mui/material/styles';
import { Box, Container, Typography, Button, Grid, Card, CardContent, TextField, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import theme from '../styles/theme';

// Styled components using Training Club branding
const LoginContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  background: theme.gradients.landingPage,
  padding: theme.spacing.xl,
  '@media (max-width: 600px)': {
    padding: theme.spacing.md,
  },
}));

const LoginCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.borderRadius.lg,
  boxShadow: theme.shadows.lg,
  overflow: 'hidden',
  width: '100%',
  maxWidth: '450px',
  margin: '0 auto',
}));

const LoginHeader = styled(Box)(({ theme }) => ({
  background: theme.colors.primary.main,
  padding: theme.spacing.lg,
  textAlign: 'center',
  color: 'white',
}));

const LoginForm = styled(Box)(({ theme }) => ({
  padding: theme.spacing.xl,
}));

const FormField = styled(TextField)(({ theme }) => ({
  marginBottom: theme.spacing.lg,
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.borderRadius.md,
    '&:hover fieldset': {
      borderColor: theme.colors.primary.main,
    },
    '&.Mui-focused fieldset': {
      borderColor: theme.colors.primary.main,
    },
  },
  '& .MuiFormLabel-root.Mui-focused': {
    color: theme.colors.primary.main,
  },
}));

const LoginButton = styled(Button)(({ theme }) => ({
  ...theme.buttonStyles.onWhite,
  padding: '12px',
  width: '100%',
  marginTop: theme.spacing.md,
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.md,
}));

const ForgotPasswordLink = styled(Typography)(({ theme }) => ({
  textAlign: 'center',
  marginTop: theme.spacing.lg,
  color: theme.colors.primary.main,
  cursor: 'pointer',
  '&:hover': {
    textDecoration: 'underline',
  },
}));

const SignUpButton = styled(Button)(({ theme }) => ({
  ...theme.buttonStyles.outlined,
  padding: '12px',
  width: '100%',
  marginTop: theme.spacing.lg,
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.md,
}));

const LoginPage = () => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // Handle login logic here
    console.log('Login attempt with:', { email, password });
  };

  return (
    <LoginContainer>
      <Container maxWidth="sm">
        <LoginCard>
          <LoginHeader>
            <Typography variant="h4" component="h1" sx={{ 
              fontWeight: theme.typography.fontWeights.bold,
            }}>
              Training Club
            </Typography>
            <Typography variant="body1">
              Sign in to your account
            </Typography>
          </LoginHeader>
          <LoginForm component="form" onSubmit={handleSubmit}>
            <FormField
              label="Email"
              variant="outlined"
              fullWidth
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <FormField
              label="Password"
              variant="outlined"
              fullWidth
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      onMouseDown={handleMouseDownPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <LoginButton type="submit" variant="contained">
              Sign In
            </LoginButton>
            <ForgotPasswordLink variant="body2">
              Forgot your password?
            </ForgotPasswordLink>
            <Box sx={{ textAlign: 'center', margin: `${theme.spacing.lg} 0` }}>
              <Typography variant="body2" color="text.secondary">
                Don't have an account?
              </Typography>
            </Box>
            <SignUpButton variant="outlined">
              Create Account
            </SignUpButton>
          </LoginForm>
        </LoginCard>
      </Container>
    </LoginContainer>
  );
};

export default LoginPage;
