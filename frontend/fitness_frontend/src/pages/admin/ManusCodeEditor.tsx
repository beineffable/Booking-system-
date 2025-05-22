import React, { useState } from 'react';
import { Box, Typography, TextField, Button, CircularProgress, Alert, Paper } from '@mui/material';
import axios from 'axios';

const ManusCodeEditor = () => {
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const handleCodeSubmit = async () => {
    if (!fileName || !code) {
      setMessage({ type: 'error', text: 'File name and code content are required' });
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await axios.post('/api/manus/edit_code', {
        fileName,
        code
      });
      setMessage({ type: 'success', text: response.data.message });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.message || 'Failed to process code' 
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Manus Code Editor
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Use this interface to edit code directly through your Manus account. Changes will be processed and applied to your platform.
        </Typography>
        
        {message.text && (
          <Alert severity={message.type} sx={{ mb: 3 }}>
            {message.text}
          </Alert>
        )}
        
        <TextField
          label="File Name"
          fullWidth
          margin="normal"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          placeholder="e.g., src/components/Header.js"
        />
        
        <TextField
          label="Code"
          fullWidth
          multiline
          rows={15}
          margin="normal"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="// Enter your code here"
          sx={{ 
            fontFamily: 'monospace',
            '& .MuiInputBase-input': {
              fontFamily: 'monospace'
            }
          }}
        />
        
        <Button 
          variant="contained" 
          onClick={handleCodeSubmit}
          disabled={isLoading}
          sx={{ mt: 2 }}
          color="primary"
        >
          {isLoading ? <CircularProgress size={24} /> : 'Submit Code to Manus'}
        </Button>
      </Paper>
    </Box>
  );
};

export default ManusCodeEditor;
