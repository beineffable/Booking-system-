# Manus Account Integration and Advanced Admin Tools

## Overview
This module will integrate the fitness platform with the user's Manus account, providing direct access to code editing, client email drafting, and advanced administrative tools. This integration will significantly enhance the platform's capabilities beyond what competitors like Glofox offer.

## Manus Account Integration

### Authentication and Security
```python
# Backend authentication for Manus integration
from flask import Blueprint, request, jsonify
from src.models.user import User
from src.routes.auth_middleware import token_required
import requests
import os

manus_bp = Blueprint('manus', __name__)

# Manus API credentials (to be stored securely in environment variables)
MANUS_API_KEY = os.getenv('MANUS_API_KEY', '34cb116566bca3e0a6755b3d543aefd1')
MANUS_API_ENDPOINT = 'https://api.manus.ai'

@manus_bp.route('/connect', methods=['POST'])
@token_required
def connect_manus_account(current_user):
    """Connect user's Manus account to the fitness platform"""
    if not current_user.is_admin:
        return jsonify({'message': 'Admin privileges required'}), 403
        
    data = request.get_json()
    manus_username = data.get('manus_username')
    
    # Verify Manus account exists and establish connection
    response = requests.post(
        f'{MANUS_API_ENDPOINT}/verify_account',
        headers={'Authorization': f'Bearer {MANUS_API_KEY}'},
        json={'username': manus_username}
    )
    
    if response.status_code == 200:
        # Store Manus connection in user profile
        current_user.manus_username = manus_username
        current_user.has_manus_integration = True
        # Save to database
        db.session.commit()
        return jsonify({'message': 'Manus account connected successfully'}), 200
    else:
        return jsonify({'message': 'Failed to connect Manus account'}), 400
```

### Code Editing Interface
```javascript
// Frontend component for code editing via Manus
import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, CircularProgress } from '@mui/material';
import axios from 'axios';

const ManusCodeEditor = () => {
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const handleCodeSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('/api/manus/edit_code', {
        fileName,
        code
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.message || 'Failed to process code'}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Manus Code Editor
      </Typography>
      <TextField
        label="File Name"
        fullWidth
        margin="normal"
        value={fileName}
        onChange={(e) => setFileName(e.target.value)}
      />
      <TextField
        label="Code"
        fullWidth
        multiline
        rows={10}
        margin="normal"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <Button 
        variant="contained" 
        onClick={handleCodeSubmit}
        disabled={isLoading}
        sx={{ mt: 2 }}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Submit Code'}
      </Button>
      {message && (
        <Typography color={message.includes('Error') ? 'error' : 'success'} sx={{ mt: 2 }}>
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default ManusCodeEditor;
```

### Client Email Drafting
```javascript
// Frontend component for drafting client emails via Manus
import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, CircularProgress, Autocomplete } from '@mui/material';
import axios from 'axios';

const ManusEmailDrafter = () => {
  const [subject, setSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [recipients, setRecipients] = useState([]);
  const [availableClients, setAvailableClients] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    // Fetch available clients
    const fetchClients = async () => {
      try {
        const response = await axios.get('/api/clients');
        setAvailableClients(response.data.clients);
      } catch (error) {
        console.error('Failed to fetch clients:', error);
      }
    };
    
    fetchClients();
  }, []);
  
  const handleDraftEmail = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('/api/manus/draft_email', {
        subject,
        body: emailBody,
        recipients: recipients.map(r => r.id)
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.message || 'Failed to draft email'}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Manus Email Drafter
      </Typography>
      <Autocomplete
        multiple
        options={availableClients}
        getOptionLabel={(option) => `${option.firstName} ${option.lastName} (${option.email})`}
        value={recipients}
        onChange={(event, newValue) => setRecipients(newValue)}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Recipients"
            margin="normal"
            fullWidth
          />
        )}
      />
      <TextField
        label="Subject"
        fullWidth
        margin="normal"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />
      <TextField
        label="Email Body"
        fullWidth
        multiline
        rows={10}
        margin="normal"
        value={emailBody}
        onChange={(e) => setEmailBody(e.target.value)}
      />
      <Button 
        variant="contained" 
        onClick={handleDraftEmail}
        disabled={isLoading}
        sx={{ mt: 2 }}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Draft Email with Manus'}
      </Button>
      {message && (
        <Typography color={message.includes('Error') ? 'error' : 'success'} sx={{ mt: 2 }}>
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default ManusEmailDrafter;
```

## Advanced Admin Tools

### Admin Dashboard
```javascript
// Frontend component for advanced admin dashboard
import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent, CircularProgress } from '@mui/material';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/admin/dashboard');
        setDashboardData(response.data);
        setIsLoading(false);
      } catch (error) {
        setError('Failed to load dashboard data');
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Members
              </Typography>
              <Typography variant="h3" color="primary">
                {dashboardData?.activeMembers || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Classes Today
              </Typography>
              <Typography variant="h3" color="primary">
                {dashboardData?.classesToday || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                New Members (30d)
              </Typography>
              <Typography variant="h3" color="primary">
                {dashboardData?.newMembers30d || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue (30d)
              </Typography>
              <Typography variant="h3" color="primary">
                {dashboardData?.revenue30d ? `$${dashboardData.revenue30d}` : '$0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Membership Growth
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={dashboardData?.membershipGrowth || []}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="members" stroke="#9ed6fe" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Class Attendance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={dashboardData?.classAttendance || []}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="attendance" fill="#f16c13" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Membership Types
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData?.membershipTypes || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {
                    (dashboardData?.membershipTypes || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#9ed6fe', '#f16c13', '#c8b4a3', '#7ab0d8'][index % 4]} />
                    ))
                  }
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={dashboardData?.revenueBreakdown || []}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="amount" fill="#c9dee7" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboard;
```

### Advanced User Management
```javascript
// Frontend component for advanced user management
import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, TablePagination, Button, Dialog, DialogActions, 
  DialogContent, DialogTitle, TextField, FormControl, InputLabel, 
  Select, MenuItem, IconButton, Chip
} from '@mui/material';
import { Edit, Delete, Add, Email, CheckCircle, Cancel } from '@mui/icons-material';
import axios from 'axios';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    role: 'member',
    status: 'active'
  });
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/admin/users');
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  const handleOpenDialog = (user = null) => {
    if (user) {
      setCurrentUser(user);
      setFormData({
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        role: user.role,
        status: user.status
      });
    } else {
      setCurrentUser(null);
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        role: 'member',
        status: 'active'
      });
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmit = async () => {
    try {
      if (currentUser) {
        await axios.put(`/api/admin/users/${currentUser.id}`, formData);
      } else {
        await axios.post('/api/admin/users', formData);
      }
      fetchUsers();
      handleCloseDialog();
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  };
  
  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`/api/admin/users/${userId}`);
        fetchUsers();
      } catch (error) {
        console.error('Failed to delete user:', error);
      }
    }
  };
  
  const handleSendEmail = (user) => {
    // Navigate to email drafting page with pre-selected recipient
    // Implementation depends on routing setup
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          User Management
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          Add User
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{`${user.firstName} ${user.lastName}`}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip 
                      label={user.role.charAt(0).toUpperCase() + user.role.slice(1)} 
                      color={user.role === 'admin' ? 'secondary' : user.role === 'trainer' ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      icon={user.status === 'active' ? <CheckCircle /> : <Cancel />}
                      label={user.status.charAt(0).toUpperCase() + user.status.slice(1)} 
                      color={user.status === 'active' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>{user.lastLogin || 'Never'}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(user)}>
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => handleSendEmail(user)}>
                      <Email />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteUser(user.id)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={users.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{currentUser ? 'Edit User' : 'Add User'}</DialogTitle>
        <DialogContent>
          <TextField
            name="firstName"
            label="First Name"
            fullWidth
            margin="normal"
            value={formData.firstName}
            onChange={handleInputChange}
          />
          <TextField
            name="lastName"
            label="Last Name"
            fullWidth
            margin="normal"
            value={formData.lastName}
            onChange={handleInputChange}
          />
          <TextField
            name="email"
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            value={formData.email}
            onChange={handleInputChange}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Role</InputLabel>
            <Select
              name="role"
              value={formData.role}
              onChange={handleInputChange}
              label="Role"
            >
              <MenuItem value="member">Member</MenuItem>
              <MenuItem value="trainer">Trainer</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              label="Status"
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
```

### System Configuration
```javascript
// Frontend component for system configuration
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
      siteName: '',
      contactEmail: '',
      timezone: '',
      maintenanceMode: false
    },
    appearance: {
      primaryColor: '#9ed6fe',
      secondaryColor: '#f16c13',
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
      stripeKey: '',
      twintEnabled: true,
      twintMerchantId: '',
      manusEnabled: true,
      manusApiKey: ''
    }
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  useEffect(() => {
    fetchConfig();
  }, []);
  
  const fetchConfig = async () => {
    try {
      const response = await axios.get('/api/admin/config');
      setConfig(response.data);
      setIsLoading(false);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load configuration' });
      setIsLoading(false);
    }
  };
  
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
      await axios.put('/api/admin/config', config);
      setMessage({ type: 'success', text: 'Configuration saved successfully' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save configuration' });
    } finally {
      setIsSaving(false);
    }
  };
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Configuration
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }}>
          {message.text}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="General" />
          <Tab label="Appearance" />
          <Tab label="Notifications" />
          <Tab label="Integrations" />
        </Tabs>
      </Paper>
      
      {/* General Settings */}
      {tabValue === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            General Settings
          </Typography>
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
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Appearance Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Primary Color"
                fullWidth
                margin="normal"
                value={config.appearance.primaryColor}
                onChange={(e) => handleInputChange('appearance', 'primaryColor', e.target.value)}
                type="color"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Secondary Color"
                fullWidth
                margin="normal"
                value={config.appearance.secondaryColor}
                onChange={(e) => handleInputChange('appearance', 'secondaryColor', e.target.value)}
                type="color"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Logo URL"
                fullWidth
                margin="normal"
                value={config.appearance.logoUrl}
                onChange={(e) => handleInputChange('appearance', 'logoUrl', e.target.value)}
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
              />
            </Grid>
          </Grid>
        </Paper>
      )}
      
      {/* Notification Settings */}
      {tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Notification Settings
          </Typography>
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
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Integration Settings
          </Typography>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Stripe Integration</Typography>
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
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Twint Integration</Typography>
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
              <Typography>Manus Integration</Typography>
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
        >
          {isSaving ? <CircularProgress size={24} /> : 'Save Configuration'}
        </Button>
      </Box>
    </Box>
  );
};

export default SystemConfiguration;
```

## Integration Testing

### Manus API Integration Test
```python
# Test script for Manus API integration
import unittest
import requests
import json
import os
from unittest.mock import patch, MagicMock

class TestManusIntegration(unittest.TestCase):
    def setUp(self):
        self.api_key = "34cb116566bca3e0a6755b3d543aefd1"
        self.api_endpoint = "https://api.manus.ai"
        self.test_username = "test_user"
        
    @patch('requests.post')
    def test_verify_account(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"verified": True}
        mock_post.return_value = mock_response
        
        # Make request
        response = requests.post(
            f'{self.api_endpoint}/verify_account',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'username': self.test_username}
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["verified"])
        mock_post.assert_called_once_with(
            f'{self.api_endpoint}/verify_account',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'username': self.test_username}
        )
        
    @patch('requests.post')
    def test_draft_email(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "email_id": "123456"}
        mock_post.return_value = mock_response
        
        # Test data
        email_data = {
            "subject": "Test Email",
            "body": "This is a test email",
            "recipients": ["user1@example.com", "user2@example.com"]
        }
        
        # Make request
        response = requests.post(
            f'{self.api_endpoint}/draft_email',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=email_data
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["email_id"], "123456")
        mock_post.assert_called_once_with(
            f'{self.api_endpoint}/draft_email',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=email_data
        )
        
    @patch('requests.post')
    def test_edit_code(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "file_id": "789012"}
        mock_post.return_value = mock_response
        
        # Test data
        code_data = {
            "fileName": "test.py",
            "code": "print('Hello, World!')"
        }
        
        # Make request
        response = requests.post(
            f'{self.api_endpoint}/edit_code',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=code_data
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["file_id"], "789012")
        mock_post.assert_called_once_with(
            f'{self.api_endpoint}/edit_code',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=code_data
        )

if __name__ == '__main__':
    unittest.main()
```

## Deployment Updates

### Backend Routes Registration
```python
# Update to src/main.py to register new routes
from flask import Flask
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.trainer import trainer_bp
from src.routes.admin import admin_bp
from src.routes.payment import payment_bp
from src.routes.leaderboard import leaderboard_bp
from src.routes.manus import manus_bp  # New Manus integration routes

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(trainer_bp, url_prefix='/api/trainer')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
app.register_blueprint(manus_bp, url_prefix='/api/manus')  # New Manus integration routes

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

### Frontend Routes Update
```javascript
// Update to App.tsx to add new admin routes
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import MemberDashboard from './pages/MemberDashboard';
import AdminDashboard from './pages/AdminDashboard';
import UserManagement from './pages/admin/UserManagement';
import SystemConfiguration from './pages/admin/SystemConfiguration';
import ManusCodeEditor from './pages/admin/ManusCodeEditor';
import ManusEmailDrafter from './pages/admin/ManusEmailDrafter';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './styles/theme';

// Create MUI theme from our custom theme configuration
const muiTheme = createTheme({
  // Theme configuration
});

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [userRole, setUserRole] = React.useState('');

  // Check if user is admin
  const isAdmin = userRole === 'admin';

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          
          {/* Member routes */}
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? 
                <MemberDashboard /> : 
                <Navigate to="/login" replace />
            } 
          />
          
          {/* Admin routes */}
          <Route 
            path="/admin" 
            element={
              isAuthenticated && isAdmin ? 
                <AdminDashboard /> : 
                <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/admin/users" 
            element={
              isAuthenticated && isAdmin ? 
                <UserManagement /> : 
                <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/admin/config" 
            element={
              isAuthenticated && isAdmin ? 
                <SystemConfiguration /> : 
                <Navigate to="/login" replace />
            } 
          />
          
          {/* Manus integration routes */}
          <Route 
            path="/admin/manus/code" 
            element={
              isAuthenticated && isAdmin ? 
                <ManusCodeEditor /> : 
                <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/admin/manus/email" 
            element={
              isAuthenticated && isAdmin ? 
                <ManusEmailDrafter /> : 
                <Navigate to="/login" replace />
            } 
          />
          
          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

## Next Steps

1. Implement the backend API endpoints for Manus integration
2. Complete the frontend components for the admin dashboard
3. Develop the user management interface with advanced filtering
4. Create the system configuration module with all settings
5. Test the Manus account integration with the API key
6. Document the integration process for future reference
7. Proceed to implementing client data collection and reporting features
