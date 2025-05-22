import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  Button, Chip, Avatar, List, ListItem, ListItemText,
  ListItemAvatar, Divider, IconButton, Alert, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { 
  Redeem, CardGiftcard, History, Add, 
  ArrowUpward, ArrowDownward, Person
} from '@mui/icons-material';
import axios from 'axios';

const CreditsSystem = () => {
  const [credits, setCredits] = useState(8);
  const [transactions, setTransactions] = useState([
    { 
      id: 1, 
      type: 'earned', 
      amount: 1, 
      description: 'Referral: Sarah Johnson attended first class', 
      date: '2025-05-15' 
    },
    { 
      id: 2, 
      type: 'earned', 
      amount: 2, 
      description: 'Admin gift: Loyalty bonus', 
      date: '2025-05-10' 
    },
    { 
      id: 3, 
      type: 'spent', 
      amount: 1, 
      description: 'Booked: Evening HIIT on May 20', 
      date: '2025-05-08' 
    },
    { 
      id: 4, 
      type: 'earned', 
      amount: 5, 
      description: 'Membership renewal: 6 months', 
      date: '2025-05-01' 
    }
  ]);
  
  const [showGiftDialog, setShowGiftDialog] = useState(false);
  const [giftRecipient, setGiftRecipient] = useState('');
  const [giftAmount, setGiftAmount] = useState(1);
  const [giftMessage, setGiftMessage] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [availableUsers, setAvailableUsers] = useState([
    { id: 1, name: 'Sarah Johnson', email: 'sarah.j@example.com' },
    { id: 2, name: 'Michael Brown', email: 'michael.b@example.com' },
    { id: 3, name: 'Emma Davis', email: 'emma.d@example.com' }
  ]);
  
  const handleOpenGiftDialog = () => {
    if (credits < 1) {
      setMessage({ type: 'error', text: 'You need at least 1 credit to gift' });
      return;
    }
    setShowGiftDialog(true);
  };
  
  const handleCloseGiftDialog = () => {
    setShowGiftDialog(false);
    setGiftRecipient('');
    setGiftAmount(1);
    setGiftMessage('');
  };
  
  const handleSendGift = () => {
    if (!giftRecipient) {
      setMessage({ type: 'error', text: 'Please select a recipient' });
      return;
    }
    
    if (giftAmount < 1) {
      setMessage({ type: 'error', text: 'Gift amount must be at least 1 credit' });
      return;
    }
    
    if (giftAmount > credits) {
      setMessage({ type: 'error', text: 'You don\'t have enough credits' });
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Update credits
      setCredits(credits - giftAmount);
      
      // Add transaction
      const recipient = availableUsers.find(user => user.id.toString() === giftRecipient);
      const newTransaction = {
        id: transactions.length + 1,
        type: 'spent',
        amount: giftAmount,
        description: `Gift to ${recipient ? recipient.name : 'Friend'}: ${giftMessage || 'Enjoy!'}`,
        date: new Date().toISOString().split('T')[0]
      };
      
      setTransactions([newTransaction, ...transactions]);
      
      setIsLoading(false);
      handleCloseGiftDialog();
      setMessage({ type: 'success', text: 'Gift sent successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }, 1500);
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Credits & Rewards
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your class credits, view transaction history, and gift credits to friends.
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Your Credits
            </Typography>
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="h1" color="primary" sx={{ fontWeight: 'bold' }}>
                {credits}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Available Credits
              </Typography>
              
              <Button
                variant="contained"
                startIcon={<CardGiftcard />}
                onClick={handleOpenGiftDialog}
                color="primary"
                sx={{ mt: 3 }}
                disabled={credits < 1}
              >
                Gift Credits
              </Button>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              How to Earn More Credits
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="Refer Friends" 
                  secondary="Earn 1 credit when they attend their first class" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Membership Renewal" 
                  secondary="Earn 5 credits for 6-month renewals, 12 for annual" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Loyalty Rewards" 
                  secondary="Earn credits for consistent attendance" 
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Transaction History
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="center">Type</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>{transaction.date}</TableCell>
                      <TableCell>{transaction.description}</TableCell>
                      <TableCell align="right">{transaction.amount}</TableCell>
                      <TableCell align="center">
                        <Chip 
                          icon={transaction.type === 'earned' ? <ArrowUpward fontSize="small" /> : <ArrowDownward fontSize="small" />}
                          label={transaction.type === 'earned' ? 'Earned' : 'Spent'} 
                          color={transaction.type === 'earned' ? 'success' : 'primary'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Gift Dialog */}
      <Dialog open={showGiftDialog} onClose={handleCloseGiftDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Gift Credits</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              Share your credits with friends. They can use them to book classes.
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Recipient</InputLabel>
              <Select
                value={giftRecipient}
                onChange={(e) => setGiftRecipient(e.target.value)}
                label="Recipient"
              >
                {availableUsers.map(user => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.name} ({user.email})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Amount</InputLabel>
              <Select
                value={giftAmount}
                onChange={(e) => setGiftAmount(Number(e.target.value))}
                label="Amount"
              >
                {[...Array(Math.min(credits, 5))].map((_, i) => (
                  <MenuItem key={i+1} value={i+1}>
                    {i+1} {i === 0 ? 'credit' : 'credits'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="Personal Message (Optional)"
              fullWidth
              margin="normal"
              value={giftMessage}
              onChange={(e) => setGiftMessage(e.target.value)}
              placeholder="Add a personal message"
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseGiftDialog}>Cancel</Button>
          <Button 
            onClick={handleSendGift} 
            variant="contained" 
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Send Gift'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CreditsSystem;
