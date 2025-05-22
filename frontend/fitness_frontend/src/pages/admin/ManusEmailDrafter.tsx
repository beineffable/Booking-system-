import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, CircularProgress, Alert, Paper, Autocomplete, Chip } from '@mui/material';
import axios from 'axios';

const ManusEmailDrafter = () => {
  const [subject, setSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [recipients, setRecipients] = useState([]);
  const [availableClients, setAvailableClients] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  useEffect(() => {
    // Fetch available clients
    const fetchClients = async () => {
      try {
        // In a real implementation, this would fetch from the API
        // const response = await axios.get('/api/clients');
        // setAvailableClients(response.data.clients);
        
        // Mock data for now
        setAvailableClients([
          { id: 1, firstName: 'John', lastName: 'Doe', email: 'john.doe@example.com' },
          { id: 2, firstName: 'Jane', lastName: 'Smith', email: 'jane.smith@example.com' },
          { id: 3, firstName: 'Michael', lastName: 'Johnson', email: 'michael.johnson@example.com' },
          { id: 4, firstName: 'Sarah', lastName: 'Williams', email: 'sarah.williams@example.com' },
          { id: 5, firstName: 'David', lastName: 'Brown', email: 'david.brown@example.com' }
        ]);
      } catch (error) {
        console.error('Failed to fetch clients:', error);
      }
    };
    
    fetchClients();
  }, []);
  
  const handleDraftEmail = async () => {
    if (!subject || !emailBody || recipients.length === 0) {
      setMessage({ type: 'error', text: 'Subject, email body, and at least one recipient are required' });
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await axios.post('/api/manus/draft_email', {
        subject,
        body: emailBody,
        recipients: recipients.map(r => r.id)
      });
      setMessage({ type: 'success', text: response.data.message });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.message || 'Failed to draft email' 
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Manus Email Drafter
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Use this interface to draft emails to your clients through your Manus account. Drafts will be saved and can be edited before sending.
        </Typography>
        
        {message.text && (
          <Alert severity={message.type} sx={{ mb: 3 }}>
            {message.text}
          </Alert>
        )}
        
        <Autocomplete
          multiple
          options={availableClients}
          getOptionLabel={(option) => `${option.firstName} ${option.lastName} (${option.email})`}
          value={recipients}
          onChange={(event, newValue) => setRecipients(newValue)}
          renderTags={(value, getTagProps) =>
            value.map((option, index) => (
              <Chip
                label={`${option.firstName} ${option.lastName}`}
                {...getTagProps({ index })}
                color="primary"
                variant="outlined"
              />
            ))
          }
          renderInput={(params) => (
            <TextField
              {...params}
              label="Recipients"
              margin="normal"
              fullWidth
              placeholder="Select clients"
            />
          )}
        />
        
        <TextField
          label="Subject"
          fullWidth
          margin="normal"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Email subject"
        />
        
        <TextField
          label="Email Body"
          fullWidth
          multiline
          rows={10}
          margin="normal"
          value={emailBody}
          onChange={(e) => setEmailBody(e.target.value)}
          placeholder="Enter your email content here..."
        />
        
        <Button 
          variant="contained" 
          onClick={handleDraftEmail}
          disabled={isLoading}
          sx={{ mt: 2 }}
          color="primary"
        >
          {isLoading ? <CircularProgress size={24} /> : 'Draft Email with Manus'}
        </Button>
      </Paper>
    </Box>
  );
};

export default ManusEmailDrafter;
