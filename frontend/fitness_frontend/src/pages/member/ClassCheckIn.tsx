import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  Button, Chip, Avatar, List, ListItem, ListItemText,
  ListItemAvatar, Divider, IconButton, Alert, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import { 
  CheckCircle, QrCodeScanner, EventAvailable, 
  AccessTime, Person, CalendarToday, LocationOn
} from '@mui/icons-material';
import axios from 'axios';

const ClassCheckIn = () => {
  const [upcomingClasses, setUpcomingClasses] = useState([
    { 
      id: 1, 
      name: 'Morning HIIT', 
      trainer: 'Alex Johnson', 
      time: '06:30 - 07:30', 
      date: '2025-05-22', 
      location: 'Main Studio',
      capacity: 12,
      registered: 8,
      status: 'upcoming'
    },
    { 
      id: 2, 
      name: 'Power Yoga', 
      trainer: 'Maria Garcia', 
      time: '12:00 - 13:00', 
      date: '2025-05-22', 
      location: 'Yoga Room',
      capacity: 15,
      registered: 12,
      status: 'upcoming'
    },
    { 
      id: 3, 
      name: 'Evening Strength', 
      trainer: 'Thomas Lee', 
      time: '18:30 - 19:30', 
      date: '2025-05-22', 
      location: 'Weight Room',
      capacity: 10,
      registered: 9,
      status: 'upcoming'
    }
  ]);
  
  const [attendanceHistory, setAttendanceHistory] = useState([
    { 
      id: 101, 
      name: 'Morning HIIT', 
      trainer: 'Alex Johnson', 
      date: '2025-05-21', 
      status: 'attended',
      checkinTime: '06:25'
    },
    { 
      id: 102, 
      name: 'Power Yoga', 
      trainer: 'Maria Garcia', 
      date: '2025-05-20', 
      status: 'attended',
      checkinTime: '12:05'
    },
    { 
      id: 103, 
      name: 'Evening Strength', 
      trainer: 'Thomas Lee', 
      date: '2025-05-19', 
      status: 'missed',
      checkinTime: null
    }
  ]);
  
  const [showQRScanner, setShowQRScanner] = useState(false);
  const [showManualCheckIn, setShowManualCheckIn] = useState(false);
  const [selectedClass, setSelectedClass] = useState(null);
  const [checkInCode, setCheckInCode] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);
  
  const handleQRScan = () => {
    setShowQRScanner(true);
  };
  
  const handleCloseQRScanner = () => {
    setShowQRScanner(false);
  };
  
  const handleManualCheckIn = (classItem) => {
    setSelectedClass(classItem);
    setShowManualCheckIn(true);
  };
  
  const handleCloseManualCheckIn = () => {
    setShowManualCheckIn(false);
    setCheckInCode('');
  };
  
  const handleSubmitCheckIn = () => {
    if (!checkInCode) {
      setMessage({ type: 'error', text: 'Please enter a check-in code' });
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Simulate successful check-in
      if (checkInCode === '1234' || checkInCode.toLowerCase() === 'checkin') {
        // Update class status
        const updatedClasses = upcomingClasses.map(c => 
          c.id === selectedClass.id ? { ...c, status: 'checked-in' } : c
        );
        setUpcomingClasses(updatedClasses);
        
        // Add to attendance history
        const now = new Date();
        const checkinTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        const newAttendance = {
          id: Date.now(),
          name: selectedClass.name,
          trainer: selectedClass.trainer,
          date: selectedClass.date,
          status: 'attended',
          checkinTime: checkinTime
        };
        
        setAttendanceHistory([newAttendance, ...attendanceHistory]);
        
        setMessage({ type: 'success', text: 'Check-in successful!' });
        handleCloseManualCheckIn();
      } else {
        setMessage({ type: 'error', text: 'Invalid check-in code. Please try again.' });
      }
      
      setIsLoading(false);
    }, 1500);
  };
  
  const getStatusColor = (status) => {
    switch(status) {
      case 'attended':
      case 'checked-in':
        return 'success';
      case 'upcoming':
        return 'primary';
      case 'missed':
        return 'error';
      default:
        return 'default';
    }
  };
  
  const getStatusIcon = (status) => {
    switch(status) {
      case 'attended':
      case 'checked-in':
        return <CheckCircle fontSize="small" />;
      case 'upcoming':
        return <AccessTime fontSize="small" />;
      case 'missed':
        return <EventAvailable fontSize="small" />;
      default:
        return null;
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Class Check-In
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Check in to your upcoming classes or view your attendance history.
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, mb: 3, boxShadow: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Upcoming Classes
              </Typography>
              <Button
                variant="contained"
                startIcon={<QrCodeScanner />}
                onClick={handleQRScan}
                color="primary"
              >
                Scan QR Code
              </Button>
            </Box>
            
            {upcomingClasses.length === 0 ? (
              <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                You have no upcoming classes scheduled.
              </Typography>
            ) : (
              <List>
                {upcomingClasses.map((classItem, index) => (
                  <React.Fragment key={classItem.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem 
                      alignItems="flex-start"
                      secondaryAction={
                        classItem.status === 'checked-in' ? (
                          <Chip 
                            icon={<CheckCircle />}
                            label="Checked In" 
                            color="success"
                            size="small"
                          />
                        ) : (
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleManualCheckIn(classItem)}
                          >
                            Check In
                          </Button>
                        )
                      }
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: '#9ed6fe' }}>
                          {classItem.name.charAt(0)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={classItem.name}
                        secondary={
                          <React.Fragment>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mt: 0.5 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Person fontSize="small" sx={{ mr: 0.5, fontSize: '0.875rem', color: 'text.secondary' }} />
                                <Typography variant="body2" color="text.secondary">
                                  {classItem.trainer}
                                </Typography>
                              </Box>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <CalendarToday fontSize="small" sx={{ mr: 0.5, fontSize: '0.875rem', color: 'text.secondary' }} />
                                <Typography variant="body2" color="text.secondary">
                                  {classItem.date}, {classItem.time}
                                </Typography>
                              </Box>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <LocationOn fontSize="small" sx={{ mr: 0.5, fontSize: '0.875rem', color: 'text.secondary' }} />
                                <Typography variant="body2" color="text.secondary">
                                  {classItem.location} ({classItem.registered}/{classItem.capacity})
                                </Typography>
                              </Box>
                            </Box>
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Attendance History
            </Typography>
            
            {attendanceHistory.length === 0 ? (
              <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No attendance history available.
              </Typography>
            ) : (
              <List>
                {attendanceHistory.map((attendance, index) => (
                  <React.Fragment key={attendance.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: attendance.status === 'attended' ? '#9ed6fe' : '#f5f5f5' }}>
                          {attendance.name.charAt(0)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={attendance.name}
                        secondary={
                          <React.Fragment>
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.primary"
                            >
                              {attendance.trainer}
                            </Typography>
                            {` — ${attendance.date}`}
                            {attendance.checkinTime && ` (Checked in at ${attendance.checkinTime})`}
                          </React.Fragment>
                        }
                      />
                      <Chip 
                        icon={getStatusIcon(attendance.status)}
                        label={attendance.status.charAt(0).toUpperCase() + attendance.status.slice(1)} 
                        color={getStatusColor(attendance.status)}
                        size="small"
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {/* QR Scanner Dialog */}
      <Dialog open={showQRScanner} onClose={handleCloseQRScanner} maxWidth="sm" fullWidth>
        <DialogTitle>Scan QR Code</DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 3 }}>
            {/* Placeholder for QR scanner */}
            <Box 
              sx={{ 
                width: '100%', 
                height: 250, 
                bgcolor: '#f5f5f5', 
                border: '1px solid #ddd',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Camera access required for QR scanning
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Position the QR code within the frame to scan
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseQRScanner}>Cancel</Button>
        </DialogActions>
      </Dialog>
      
      {/* Manual Check-in Dialog */}
      <Dialog open={showManualCheckIn} onClose={handleCloseManualCheckIn} maxWidth="sm" fullWidth>
        <DialogTitle>Manual Check-in</DialogTitle>
        <DialogContent>
          {selectedClass && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="subtitle1" gutterBottom>
                {selectedClass.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {selectedClass.date}, {selectedClass.time} with {selectedClass.trainer}
              </Typography>
              
              <TextField
                label="Check-in Code"
                fullWidth
                margin="normal"
                value={checkInCode}
                onChange={(e) => setCheckInCode(e.target.value)}
                placeholder="Enter the code displayed at the gym"
                helperText="Ask your trainer for the check-in code"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseManualCheckIn}>Cancel</Button>
          <Button 
            onClick={handleSubmitCheckIn} 
            variant="contained" 
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Check In'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ClassCheckIn;
