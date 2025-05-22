import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Tabs, Tab, TextField, Button, 
  FormControlLabel, Switch, Divider, Grid, Alert, CircularProgress,
  Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { ExpandMore, Save } from '@mui/icons-material';
import axios from 'axios';

const SystemConfiguration = () => {
  const [tabValue, setTabValue] = useState(0);
  const [config, setConfig] = useState({
    general: {
      siteName: 'Training Club Fitness Platform',
      contactEmail: 'admin@trainingclub.ch',
      timezone: 'Europe/Zurich',
      maintenanceMode: false
    },
    appearance: {
      primaryColor: '#9ed6fe',
      secondaryColor: '#f16c13',
      neutralColor: '#c8b4a3',
      logoUrl: '',
      customCss: ''
    },
    notifications: {
      emailNotifications: true,
      smsNotifications: false,
      reminderHours: 24
    },
    integrations: {
      stripeEnabled: true,
      stripeKey: 'sk_test_*****',
      twintEnabled: true,
      twintMerchantId: 'twint_merchant_*****',
      manusEnabled: true,
      manusApiKey: '34cb116566bca3e0a6755b3d543aefd1'
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleInputChange = (section, field, value) => {
    setConfig({
      ...config,
      [section]: {
        ...config[section],
        [field]: value
      }
    });
  };
  
  const handleSaveConfig = async () => {
    setIsSaving(true);
    try {
      // In a real implementation, this would save via API
      // await axios.put('/api/admin/config', config);
      
      // Mock save for now
      setTimeout(() => {
        setMessage({ type: 'success', text: 'Configuration saved successfully' });
        setIsSaving(false);
      }, 1000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save configuration' });
      setIsSaving(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Configuration
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3, boxShadow: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab label="General" />
          <Tab label="Appearance" />
          <Tab label="Notifications" />
          <Tab label="Integrations" />
        </Tabs>
      </Paper>
      
      {/* General Settings */}
      {tabValue === 0 && (
        <Paper sx={{ p: 3, boxShadow: 2 }}>
          <Typography variant="h6" gutterBottom>
            General Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Site Name"
                fullWidth
                margin="normal"
                value={config.general.siteName}
                onChange={(e) => handleInputChange('general', 'siteName', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Contact Email"
                fullWidth
                margin="normal"
                value={config.general.contactEmail}
                onChange={(e) => handleInputChange('general', 'contactEmail', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Timezone"
                fullWidth
                margin="normal"
                value={config.general.timezone}
                onChange={(e) => handleInputChange('general', 'timezone', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.general.maintenanceMode}
                    onChange={(e) => handleInputChange('general', 'maintenanceMode', e.target.checked)}
                  />
                }
                label="Maintenance Mode"
              />
            </Grid>
          </Grid>
        </Paper>
      )}
      
      {/* Appearance Settings */}
      {tabValue === 1 && (
        <Paper sx={{ p: 3, boxShadow: 2 }}>
          <Typography variant="h6" gutterBottom>
            Appearance Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Primary Color"
                fullWidth
                margin="normal"
                value={config.appearance.primaryColor}
                onChange={(e) => handleInputChange('appearance', 'primaryColor', e.target.value)}
                type="color"
              />
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 20, height: 20, bgcolor: config.appearance.primaryColor, mr: 1, borderRadius: 1 }} />
                <Typography variant="body2">{config.appearance.primaryColor}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Secondary Color"
                fullWidth
                margin="normal"
                value={config.appearance.secondaryColor}
                onChange={(e) => handleInputChange('appearance', 'secondaryColor', e.target.value)}
                type="color"
              />
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 20, height: 20, bgcolor: config.appearance.secondaryColor, mr: 1, borderRadius: 1 }} />
                <Typography variant="body2">{config.appearance.secondaryColor}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Neutral Color"
                fullWidth
                margin="normal"
                value={config.appearance.neutralColor}
                onChange={(e) => handleInputChange('appearance', 'neutralColor', e.target.value)}
                type="color"
              />
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 20, height: 20, bgcolor: config.appearance.neutralColor, mr: 1, borderRadius: 1 }} />
                <Typography variant="body2">{config.appearance.neutralColor}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Logo URL"
                fullWidth
                margin="normal"
                value={config.appearance.logoUrl}
                onChange={(e) => handleInputChange('appearance', 'logoUrl', e.target.value)}
                placeholder="https://trainingclub.ch/logo.png"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Custom CSS"
                fullWidth
                multiline
                rows={6}
                margin="normal"
                value={config.appearance.customCss}
                onChange={(e) => handleInputChange('appearance', 'customCss', e.target.value)}
                placeholder="/* Add custom CSS here */"
                sx={{ 
                  fontFamily: 'monospace',
                  '& .MuiInputBase-input': {
                    fontFamily: 'monospace'
                  }
                }}
              />
            </Grid>
          </Grid>
        </Paper>
      )}
      
      {/* Notification Settings */}
      {tabValue === 2 && (
        <Paper sx={{ p: 3, boxShadow: 2 }}>
          <Typography variant="h6" gutterBottom>
            Notification Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.notifications.emailNotifications}
                    onChange={(e) => handleInputChange('notifications', 'emailNotifications', e.target.checked)}
                  />
                }
                label="Email Notifications"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.notifications.smsNotifications}
                    onChange={(e) => handleInputChange('notifications', 'smsNotifications', e.target.checked)}
                  />
                }
                label="SMS Notifications"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Reminder Hours Before Class"
                fullWidth
                margin="normal"
                type="number"
                value={config.notifications.reminderHours}
                onChange={(e) => handleInputChange('notifications', 'reminderHours', parseInt(e.target.value))}
              />
            </Grid>
          </Grid>
        </Paper>
      )}
      
      {/* Integration Settings */}
      {tabValue === 3 && (
        <Paper sx={{ p: 3, boxShadow: 2 }}>
          <Typography variant="h6" gutterBottom>
            Integration Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Accordion defaultExpanded sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1">Stripe Integration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.integrations.stripeEnabled}
                        onChange={(e) => handleInputChange('integrations', 'stripeEnabled', e.target.checked)}
                      />
                    }
                    label="Enable Stripe"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Stripe API Key"
                    fullWidth
                    margin="normal"
                    value={config.integrations.stripeKey}
                    onChange={(e) => handleInputChange('integrations', 'stripeKey', e.target.value)}
                    type="password"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          <Accordion sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1">Twint Integration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.integrations.twintEnabled}
                        onChange={(e) => handleInputChange('integrations', 'twintEnabled', e.target.checked)}
                      />
                    }
                    label="Enable Twint"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Twint Merchant ID"
                    fullWidth
                    margin="normal"
                    value={config.integrations.twintMerchantId}
                    onChange={(e) => handleInputChange('integrations', 'twintMerchantId', e.target.value)}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1">Manus Integration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.integrations.manusEnabled}
                        onChange={(e) => handleInputChange('integrations', 'manusEnabled', e.target.checked)}
                      />
                    }
                    label="Enable Manus"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Manus API Key"
                    fullWidth
                    margin="normal"
                    value={config.integrations.manusApiKey}
                    onChange={(e) => handleInputChange('integrations', 'manusApiKey', e.target.value)}
                    type="password"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Paper>
      )}
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          startIcon={<Save />}
          onClick={handleSaveConfig}
          disabled={isSaving}
          color="primary"
          size="large"
        >
          {isSaving ? <CircularProgress size={24} /> : 'Save Configuration'}
        </Button>
      </Box>
    </Box>
  );
};

export default SystemConfiguration;
