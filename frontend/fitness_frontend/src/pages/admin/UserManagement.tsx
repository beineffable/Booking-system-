import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, TablePagination, Button, Dialog, DialogActions, 
  DialogContent, DialogTitle, TextField, FormControl, InputLabel, 
  Select, MenuItem, IconButton, Chip, Alert
} from '@mui/material';
import { Edit, Delete, Add, Email, CheckCircle, Cancel } from '@mui/icons-material';
import axios from 'axios';

const UserManagement = () => {
  const [users, setUsers] = useState([
    { id: 1, firstName: 'John', lastName: 'Doe', email: 'john.doe@example.com', role: 'admin', status: 'active', lastLogin: '2025-05-20 14:30' },
    { id: 2, firstName: 'Jane', lastName: 'Smith', email: 'jane.smith@example.com', role: 'trainer', status: 'active', lastLogin: '2025-05-21 09:15' },
    { id: 3, firstName: 'Michael', lastName: 'Johnson', email: 'michael.johnson@example.com', role: 'member', status: 'active', lastLogin: '2025-05-19 18:45' },
    { id: 4, firstName: 'Sarah', lastName: 'Williams', email: 'sarah.williams@example.com', role: 'member', status: 'inactive', lastLogin: '2025-04-30 11:20' },
    { id: 5, firstName: 'David', lastName: 'Brown', email: 'david.brown@example.com', role: 'member', status: 'active', lastLogin: '2025-05-21 08:05' }
  ]);
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
  const [message, setMessage] = useState({ type: '', text: '' });
  
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
        // In a real implementation, this would update via API
        // await axios.put(`/api/admin/users/${currentUser.id}`, formData);
        
        // Mock update for now
        const updatedUsers = users.map(user => 
          user.id === currentUser.id ? { ...user, ...formData } : user
        );
        setUsers(updatedUsers);
        setMessage({ type: 'success', text: 'User updated successfully' });
      } else {
        // In a real implementation, this would create via API
        // const response = await axios.post('/api/admin/users', formData);
        
        // Mock create for now
        const newUser = {
          id: users.length + 1,
          ...formData,
          lastLogin: 'Never'
        };
        setUsers([...users, newUser]);
        setMessage({ type: 'success', text: 'User created successfully' });
      }
      handleCloseDialog();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save user' });
    }
  };
  
  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        // In a real implementation, this would delete via API
        // await axios.delete(`/api/admin/users/${userId}`);
        
        // Mock delete for now
        const filteredUsers = users.filter(user => user.id !== userId);
        setUsers(filteredUsers);
        setMessage({ type: 'success', text: 'User deleted successfully' });
      } catch (error) {
        setMessage({ type: 'error', text: 'Failed to delete user' });
      }
    }
  };
  
  const handleSendEmail = (user) => {
    // Navigate to email drafting page with pre-selected recipient
    window.location.href = `/admin/manus/email?recipient=${user.id}`;
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
          color="primary"
        >
          Add User
        </Button>
      </Box>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <TableContainer component={Paper} sx={{ boxShadow: 2 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell><Typography variant="subtitle2">Name</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Email</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Role</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Status</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Last Login</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Actions</Typography></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((user) => (
                <TableRow key={user.id} hover>
                  <TableCell>{`${user.firstName} ${user.lastName}`}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip 
                      label={user.role.charAt(0).toUpperCase() + user.role.slice(1)} 
                      color={user.role === 'admin' ? 'secondary' : user.role === 'trainer' ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      icon={user.status === 'active' ? <CheckCircle fontSize="small" /> : <Cancel fontSize="small" />}
                      label={user.status.charAt(0).toUpperCase() + user.status.slice(1)} 
                      color={user.status === 'active' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{user.lastLogin || 'Never'}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(user)} size="small" color="primary">
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => handleSendEmail(user)} size="small" color="primary">
                      <Email />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteUser(user.id)} size="small" color="error">
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
            required
          />
          <TextField
            name="lastName"
            label="Last Name"
            fullWidth
            margin="normal"
            value={formData.lastName}
            onChange={handleInputChange}
            required
          />
          <TextField
            name="email"
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            value={formData.email}
            onChange={handleInputChange}
            required
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
          <Button onClick={handleSubmit} variant="contained" color="primary">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
