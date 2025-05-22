import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  CircularProgress, Alert, Divider, Button
} from '@mui/material';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import axios from 'axios';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // In a real implementation, this would fetch from the API
        // const response = await axios.get('/api/admin/dashboard');
        // setDashboardData(response.data);
        
        // Mock data for now
        setDashboardData({
          activeMembers: 127,
          classesToday: 8,
          newMembers30d: 15,
          revenue30d: 12450,
          membershipGrowth: [
            { month: 'Jan', members: 85 },
            { month: 'Feb', members: 92 },
            { month: 'Mar', members: 99 },
            { month: 'Apr', members: 108 },
            { month: 'May', members: 127 }
          ],
          classAttendance: [
            { day: 'Mon', attendance: 42 },
            { day: 'Tue', attendance: 38 },
            { day: 'Wed', attendance: 45 },
            { day: 'Thu', attendance: 40 },
            { day: 'Fri', attendance: 48 },
            { day: 'Sat', attendance: 52 },
            { day: 'Sun', attendance: 25 }
          ],
          membershipTypes: [
            { name: 'Standard', value: 65 },
            { name: 'Premium', value: 35 },
            { name: 'Corporate', value: 15 },
            { name: 'Student', value: 12 }
          ],
          revenueBreakdown: [
            { category: 'Memberships', amount: 9200 },
            { category: 'One-time Classes', amount: 1850 },
            { category: 'Private Sessions', amount: 1200 },
            { category: 'Merchandise', amount: 200 }
          ]
        });
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
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Admin Dashboard
        </Typography>
        <Box>
          <Button 
            variant="outlined" 
            color="primary" 
            sx={{ mr: 1 }}
            onClick={() => window.location.href = '/admin/manus/code'}
          >
            Manus Code Editor
          </Button>
          <Button 
            variant="outlined" 
            color="primary"
            onClick={() => window.location.href = '/admin/manus/email'}
          >
            Manus Email Drafter
          </Button>
        </Box>
      </Box>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Active Members
              </Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.activeMembers || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Classes Today
              </Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.classesToday || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                New Members (30d)
              </Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.newMembers30d || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Revenue (30d)
              </Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.revenue30d ? `${dashboardData.revenue30d} CHF` : '0 CHF'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Membership Growth
            </Typography>
            <Divider sx={{ mb: 2 }} />
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
                <Line type="monotone" dataKey="members" stroke="#9ed6fe" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Class Attendance
            </Typography>
            <Divider sx={{ mb: 2 }} />
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
          <Paper sx={{ p: 2, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Membership Types
            </Typography>
            <Divider sx={{ mb: 2 }} />
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
                      <Cell key={`cell-${index}`} fill={['#9ed6fe', '#f16c13', '#c8b4a3', '#c9dee7'][index % 4]} />
                    ))
                  }
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Breakdown
            </Typography>
            <Divider sx={{ mb: 2 }} />
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
