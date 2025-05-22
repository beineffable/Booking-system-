import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  Button, Divider, IconButton, Alert, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, FormControl, InputLabel, Select, MenuItem,
  LinearProgress, Tooltip
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Info, ArrowUpward, ArrowDownward,
  CalendarToday, Refresh, Download, BarChart, PieChart, Timeline
} from '@mui/icons-material';
import { 
  BarChart as ReBarChart, Bar, LineChart, Line, PieChart as RePieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import axios from 'axios';

const SalesAnalytics = () => {
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('30d');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Sample analytics data
  const [analyticsData, setAnalyticsData] = useState({
    overview: {
      totalSales: 24750,
      conversionRate: 8.2,
      averageOrderValue: 325,
      membershipGrowth: 15.3,
      salesTrend: [
        { date: '2025-04-21', amount: 750 },
        { date: '2025-04-28', amount: 850 },
        { date: '2025-05-05', amount: 920 },
        { date: '2025-05-12', amount: 1050 },
        { date: '2025-05-19', amount: 1180 }
      ]
    },
    conversionFunnel: {
      stages: [
        { name: 'Website Visitors', value: 3250 },
        { name: 'Class Page Views', value: 1840 },
        { name: 'Schedule Viewers', value: 920 },
        { name: 'Trial Signups', value: 215 },
        { name: 'Paid Conversions', value: 85 }
      ],
      conversionRates: [
        { stage: 'Visitor to Class View', rate: 56.6 },
        { stage: 'Class View to Schedule', rate: 50.0 },
        { stage: 'Schedule to Trial', rate: 23.4 },
        { stage: 'Trial to Paid', rate: 39.5 },
        { stage: 'Overall (Visitor to Paid)', rate: 2.6 }
      ]
    },
    membershipInsights: {
      distribution: [
        { name: 'Standard', value: 65 },
        { name: 'Premium', value: 35 },
        { name: 'Corporate', value: 15 },
        { name: 'Student', value: 12 }
      ],
      retention: [
        { month: 'January', rate: 82.3 },
        { month: 'February', rate: 79.1 },
        { month: 'March', rate: 80.5 },
        { month: 'April', rate: 76.8 },
        { month: 'May', rate: 78.5 }
      ],
      churnReasons: [
        { reason: 'Price', percentage: 35 },
        { reason: 'Relocation', percentage: 25 },
        { reason: 'Schedule', percentage: 20 },
        { reason: 'Facility', percentage: 10 },
        { reason: 'Other', percentage: 10 }
      ]
    },
    optimizationInsights: {
      recommendations: [
        { 
          id: 1, 
          title: 'Improve Trial Conversion Rate', 
          description: 'Current trial-to-paid conversion rate (39.5%) is below industry average. Consider implementing a structured onboarding process for trial members.',
          impact: 'high',
          difficulty: 'medium'
        },
        { 
          id: 2, 
          title: 'Optimize Class Schedule', 
          description: 'Evening classes (18:00-20:00) have highest attendance and conversion rates. Consider adding more classes during this time slot.',
          impact: 'medium',
          difficulty: 'low'
        },
        { 
          id: 3, 
          title: 'Address Price-Related Churn', 
          description: 'Price is the top reason for membership cancellation (35%). Consider introducing more flexible pricing options or membership tiers.',
          impact: 'high',
          difficulty: 'high'
        },
        { 
          id: 4, 
          title: 'Enhance Mobile Experience', 
          description: 'Mobile conversion rate (6.1%) is significantly lower than desktop (10.3%). Improve mobile booking experience.',
          impact: 'medium',
          difficulty: 'medium'
        }
      ],
      abTests: [
        {
          id: 1,
          name: 'Homepage Hero Image',
          status: 'running',
          startDate: '2025-05-10',
          variants: [
            { name: 'Control', conversionRate: 7.8, visitors: 1250 },
            { name: 'Variant A', conversionRate: 9.2, visitors: 1245 }
          ],
          improvement: 17.9
        },
        {
          id: 2,
          name: 'Pricing Page Layout',
          status: 'completed',
          startDate: '2025-04-15',
          endDate: '2025-05-05',
          variants: [
            { name: 'Control', conversionRate: 4.2, visitors: 2150 },
            { name: 'Variant A', conversionRate: 5.8, visitors: 2180 }
          ],
          improvement: 38.1,
          winner: 'Variant A'
        }
      ]
    }
  });
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
    setIsLoading(true);
    
    // Simulate API call to fetch data for new time range
    setTimeout(() => {
      // In a real app, this would fetch new data
      setIsLoading(false);
    }, 1000);
  };
  
  const handleRefreshData = () => {
    setIsLoading(true);
    
    // Simulate API call to refresh data
    setTimeout(() => {
      // In a real app, this would fetch fresh data
      setIsLoading(false);
      setMessage({ type: 'success', text: 'Data refreshed successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }, 1500);
  };
  
  const handleExportData = () => {
    // In a real app, this would trigger a data export
    setMessage({ type: 'success', text: 'Analytics data export started!' });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };
  
  const getImpactColor = (impact) => {
    switch(impact) {
      case 'high':
        return '#f16c13';
      case 'medium':
        return '#9ed6fe';
      case 'low':
        return '#c8b4a3';
      default:
        return '#9ed6fe';
    }
  };
  
  const getDifficultyColor = (difficulty) => {
    switch(difficulty) {
      case 'high':
        return '#f44336';
      case 'medium':
        return '#ff9800';
      case 'low':
        return '#4caf50';
      default:
        return '#ff9800';
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Sales Analytics
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={handleTimeRangeChange}
              label="Time Range"
            >
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
              <MenuItem value="ytd">Year to Date</MenuItem>
              <MenuItem value="all">All Time</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefreshData}
            disabled={isLoading}
          >
            Refresh
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExportData}
          >
            Export
          </Button>
        </Box>
      </Box>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      {isLoading && (
        <LinearProgress sx={{ mb: 3 }} />
      )}
      
      <Paper sx={{ mb: 3, boxShadow: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Overview" icon={<BarChart />} iconPosition="start" />
          <Tab label="Conversion Funnel" icon={<Timeline />} iconPosition="start" />
          <Tab label="Membership Insights" icon={<PieChart />} iconPosition="start" />
          <Tab label="Optimization" icon={<TrendingUp />} iconPosition="start" />
        </Tabs>
      </Paper>
      
      {/* Overview Tab */}
      {tabValue === 0 && (
        <Box>
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Total Sales (CHF)
                  </Typography>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analyticsData.overview.totalSales.toLocaleString()}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <ArrowUpward sx={{ color: 'success.main', fontSize: '0.9rem', mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      12.5% vs previous period
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Conversion Rate
                  </Typography>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analyticsData.overview.conversionRate}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <ArrowUpward sx={{ color: 'success.main', fontSize: '0.9rem', mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      1.8% vs previous period
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Average Order Value (CHF)
                  </Typography>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analyticsData.overview.averageOrderValue}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <ArrowUpward sx={{ color: 'success.main', fontSize: '0.9rem', mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      5.2% vs previous period
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#f8f9fa', boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Membership Growth
                  </Typography>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analyticsData.overview.membershipGrowth}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <ArrowDownward sx={{ color: 'error.main', fontSize: '0.9rem', mr: 0.5 }} />
                    <Typography variant="body2" color="error.main">
                      2.1% vs previous period
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sales Trend
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart
                data={analyticsData.overview.salesTrend}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#9ed6fe" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#9ed6fe" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <ReTooltip />
                <Area type="monotone" dataKey="amount" stroke="#9ed6fe" fillOpacity={1} fill="url(#colorSales)" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Box>
      )}
      
      {/* Conversion Funnel Tab */}
      {tabValue === 1 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={7}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Conversion Funnel
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={analyticsData.conversionFunnel.stages}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <ReTooltip />
                    <Bar dataKey="value" fill="#f16c13" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={5}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Conversion Rates
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Conversion Stage</TableCell>
                        <TableCell align="right">Rate</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analyticsData.conversionFunnel.conversionRates.map((row) => (
                        <TableRow key={row.stage}>
                          <TableCell component="th" scope="row">
                            {row.stage}
                          </TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                {row.rate}%
                              </Typography>
                              {row.stage === 'Overall (Visitor to Paid)' && (
                                <Tooltip title="Industry average: 3.2%">
                                  <Info fontSize="small" color="primary" sx={{ ml: 1 }} />
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                <Box sx={{ mt: 3, p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Key Insights
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • The largest drop-off occurs between Schedule Viewers and Trial Signups (76.6%)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Trial to Paid conversion (39.5%) is below industry average (45%)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Overall conversion rate is 2.6%, which is below target of 3.5%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
      
      {/* Membership Insights Tab */}
      {tabValue === 2 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={5}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Membership Distribution
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <ResponsiveContainer width="100%" height={300}>
                  <RePieChart>
                    <Pie
                      data={analyticsData.membershipInsights.distribution}
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
                        analyticsData.membershipInsights.distribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={['#9ed6fe', '#f16c13', '#c8b4a3', '#c9dee7'][index % 4]} />
                        ))
                      }
                    </Pie>
                    <ReTooltip />
                  </RePieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={7}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Retention Rate Trend
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={analyticsData.membershipInsights.retention}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis domain={[60, 100]} />
                    <ReTooltip />
                    <Line type="monotone" dataKey="rate" stroke="#9ed6fe" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Churn Reasons
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={analyticsData.membershipInsights.churnReasons}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="reason" />
                        <YAxis />
                        <ReTooltip />
                        <Bar dataKey="percentage" fill="#f16c13" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ p: 2, bgcolor: '#f8f9fa', borderRadius: 1, height: '100%' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Churn Analysis
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Price sensitivity is the leading cause of membership cancellations (35%), followed by relocation (25%) and scheduling conflicts (20%).
                      </Typography>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommendations
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        • Introduce more flexible pricing options or membership tiers
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        • Implement a relocation freeze policy (pause membership for 3 months)
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        • Expand class schedule variety to accommodate different schedules
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        • Conduct exit surveys to gather more detailed feedback
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
      
      {/* Optimization Tab */}
      {tabValue === 3 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Optimization Recommendations
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Recommendation</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="center">Impact</TableCell>
                        <TableCell align="center">Difficulty</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analyticsData.optimizationInsights.recommendations.map((row) => (
                        <TableRow key={row.id}>
                          <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                            {row.title}
                          </TableCell>
                          <TableCell>{row.description}</TableCell>
                          <TableCell align="center">
                            <Chip 
                              label={row.impact.charAt(0).toUpperCase() + row.impact.slice(1)} 
                              sx={{ bgcolor: getImpactColor(row.impact), color: 'white' }}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Chip 
                              label={row.difficulty.charAt(0).toUpperCase() + row.difficulty.slice(1)} 
                              sx={{ bgcolor: getDifficultyColor(row.difficulty), color: 'white' }}
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
            <Grid item xs={12}>
              <Paper sx={{ p: 3, boxShadow: 2 }}>
                <Typography variant="h6" gutterBottom>
                  A/B Tests
                </Typography>
                <Divider sx={{ mb: 3 }} />
                {analyticsData.optimizationInsights.abTests.map((test) => (
                  <Card key={test.id} sx={{ mb: 3, boxShadow: 1 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                          {test.name}
                        </Typography>
                        <Chip 
                          label={test.status.charAt(0).toUpperCase() + test.status.slice(1)} 
                          color={test.status === 'running' ? 'primary' : 'success'}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {test.status === 'running' ? (
                          `Started on ${test.startDate} • Running for ${Math.floor((new Date() - new Date(test.startDate)) / (1000 * 60 * 60 * 24))} days`
                        ) : (
                          `${test.startDate} to ${test.endDate} • Winner: ${test.winner}`
                        )}
                      </Typography>
                      
                      <Grid container spacing={2}>
                        {test.variants.map((variant, index) => (
                          <Grid item xs={12} sm={6} key={variant.name}>
                            <Box sx={{ 
                              p: 2, 
                              bgcolor: '#f8f9fa', 
                              borderRadius: 1,
                              border: variant.name === test.winner ? '2px solid #4caf50' : 'none'
                            }}>
                              <Typography variant="subtitle2" gutterBottom>
                                {variant.name}
                                {variant.name === test.winner && (
                                  <Chip 
                                    label="Winner" 
                                    color="success" 
                                    size="small" 
                                    sx={{ ml: 1 }}
                                  />
                                )}
                              </Typography>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                  Conversion Rate
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                  {variant.conversionRate}%
                                </Typography>
                              </Box>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="body2" color="text.secondary">
                                  Visitors
                                </Typography>
                                <Typography variant="body2">
                                  {variant.visitors.toLocaleString()}
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                      
                      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                          Improvement:
                        </Typography>
                        <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>
                          +{test.improvement}%
                        </Typography>
                        {test.status === 'completed' && (
                          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                            (Statistical Confidence: 95%)
                          </Typography>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default SalesAnalytics;
