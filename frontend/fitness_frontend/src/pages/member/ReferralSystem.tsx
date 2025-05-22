import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  TextField, Button, FormControl, InputLabel, Select,
  MenuItem, Chip, Avatar, List, ListItem, ListItemText,
  ListItemAvatar, Divider, IconButton, Alert, CircularProgress
} from '@mui/material';
import { 
  CheckCircle, Cancel, PersonAdd, Share, QrCode,
  ContentCopy, WhatsApp, Email, Facebook
} from '@mui/icons-material';
import axios from 'axios';

const ReferralSystem = () => {
  const [referralCode, setReferralCode] = useState('TC-JOHN-2025');
  const [referralLink, setReferralLink] = useState('https://trainingclub.ch/join?ref=TC-JOHN-2025');
  const [referralStats, setReferralStats] = useState({
    sent: 12,
    registered: 5,
    attended: 3,
    creditsEarned: 3
  });
  const [referralHistory, setReferralHistory] = useState([
    { id: 1, name: 'Sarah Johnson', email: 'sarah.j@example.com', status: 'attended', date: '2025-05-10' },
    { id: 2, name: 'Michael Brown', email: 'michael.b@example.com', status: 'registered', date: '2025-05-15' },
    { id: 3, name: 'Emma Davis', email: 'emma.d@example.com', status: 'invited', date: '2025-05-18' }
  ]);
  const [showQRCode, setShowQRCode] = useState(false);
  const [showShareOptions, setShowShareOptions] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  
  const handleCopyLink = () => {
    navigator.clipboard.writeText(referralLink)
      .then(() => {
        setMessage({ type: 'success', text: 'Referral link copied to clipboard!' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      })
      .catch(() => {
        setMessage({ type: 'error', text: 'Failed to copy link. Please try again.' });
      });
  };
  
  const handleSendInvite = () => {
    if (!inviteEmail) {
      setMessage({ type: 'error', text: 'Please enter an email address' });
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Add to history
      const newInvite = {
        id: referralHistory.length + 1,
        name: 'Friend',
        email: inviteEmail,
        status: 'invited',
        date: new Date().toISOString().split('T')[0]
      };
      
      setReferralHistory([newInvite, ...referralHistory]);
      setReferralStats({
        ...referralStats,
        sent: referralStats.sent + 1
      });
      
      setInviteEmail('');
      setIsLoading(false);
      setMessage({ type: 'success', text: 'Invitation sent successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }, 1500);
  };
  
  const getStatusColor = (status) => {
    switch(status) {
      case 'attended':
        return 'success';
      case 'registered':
        return 'primary';
      case 'invited':
        return 'default';
      default:
        return 'default';
    }
  };
  
  const getStatusIcon = (status) => {
    switch(status) {
      case 'attended':
        return <CheckCircle fontSize="small" />;
      case 'registered':
        return <PersonAdd fontSize="small" />;
      case 'invited':
        return <Share fontSize="small" />;
      default:
        return null;
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Bring a Friend Program
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Invite your friends to join Training Club. When they attend their first class, you'll earn a free class credit!
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Your Referral Link
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TextField
                fullWidth
                value={referralLink}
                variant="outlined"
                size="small"
                InputProps={{
                  readOnly: true,
                }}
                sx={{ mr: 1 }}
              />
              <IconButton 
                color="primary" 
                onClick={handleCopyLink}
                title="Copy link"
              >
                <ContentCopy />
              </IconButton>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                variant="outlined"
                startIcon={<QrCode />}
                onClick={() => setShowQRCode(!showQRCode)}
              >
                {showQRCode ? 'Hide QR Code' : 'Show QR Code'}
              </Button>
              
              <Button
                variant="contained"
                startIcon={<Share />}
                onClick={() => setShowShareOptions(!showShareOptions)}
                color="primary"
              >
                Share
              </Button>
            </Box>
            
            {showQRCode && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                {/* Placeholder for QR code image */}
                <Box 
                  sx={{ 
                    width: 200, 
                    height: 200, 
                    bgcolor: '#f5f5f5', 
                    border: '1px solid #ddd',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    QR Code Placeholder
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Scan this code to join Training Club
                </Typography>
              </Box>
            )}
            
            {showShareOptions && (
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
                <IconButton color="primary" sx={{ bgcolor: '#25D366', color: 'white', '&:hover': { bgcolor: '#128C7E' } }}>
                  <WhatsApp />
                </IconButton>
                <IconButton color="primary" sx={{ bgcolor: '#DB4437', color: 'white', '&:hover': { bgcolor: '#C53929' } }}>
                  <Email />
                </IconButton>
                <IconButton color="primary" sx={{ bgcolor: '#4267B2', color: 'white', '&:hover': { bgcolor: '#365899' } }}>
                  <Facebook />
                </IconButton>
              </Box>
            )}
          </Paper>
          
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Send Direct Invitation
            </Typography>
            <TextField
              label="Friend's Email"
              fullWidth
              margin="normal"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="Enter your friend's email"
            />
            <Button 
              variant="contained" 
              color="primary"
              fullWidth
              sx={{ mt: 2 }}
              onClick={handleSendInvite}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Send Invitation'}
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Your Referral Stats
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#f8f9fa' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                      {referralStats.sent}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Invitations Sent
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#f8f9fa' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                      {referralStats.registered}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Registered
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#f8f9fa' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                      {referralStats.attended}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Attended
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#f8f9fa' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" color="#f16c13" sx={{ fontWeight: 'bold' }}>
                      {referralStats.creditsEarned}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Credits Earned
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom>
              Referral History
            </Typography>
            <List>
              {referralHistory.map((referral, index) => (
                <React.Fragment key={referral.id}>
                  {index > 0 && <Divider component="li" />}
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar>{referral.name.charAt(0)}</Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={referral.name}
                      secondary={
                        <React.Fragment>
                          <Typography
                            component="span"
                            variant="body2"
                            color="text.primary"
                          >
                            {referral.email}
                          </Typography>
                          {` — Invited on ${referral.date}`}
                        </React.Fragment>
                      }
                    />
                    <Chip 
                      icon={getStatusIcon(referral.status)}
                      label={referral.status.charAt(0).toUpperCase() + referral.status.slice(1)} 
                      color={getStatusColor(referral.status)}
                      size="small"
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ReferralSystem;
