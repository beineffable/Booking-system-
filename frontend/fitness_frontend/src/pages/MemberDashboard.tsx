import React from 'react';
import { styled } from '@mui/material/styles';
import { Box, Container, Typography, Button, Grid, Card, CardContent, Avatar, Tabs, Tab, CircularProgress } from '@mui/material';
import theme from '../styles/theme';

// Styled components using Training Club branding
const DashboardContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  background: theme.colors.background.default,
}));

const Header = styled(Box)(({ theme }) => ({
  background: theme.colors.primary.main,
  padding: theme.spacing.md,
  color: 'white',
}));

const SideNav = styled(Box)(({ theme }) => ({
  width: '250px',
  background: 'white',
  height: '100%',
  position: 'fixed',
  left: 0,
  top: '64px',
  borderRight: `1px solid ${theme.colors.ui.divider}`,
  padding: theme.spacing.md,
  '@media (max-width: 960px)': {
    display: 'none',
  },
}));

const MainContent = styled(Box)(({ theme }) => ({
  marginLeft: '250px',
  padding: theme.spacing.xl,
  '@media (max-width: 960px)': {
    marginLeft: 0,
    padding: theme.spacing.md,
  },
}));

const NavItem = styled(Box)(({ theme, active }) => ({
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.md,
  marginBottom: theme.spacing.sm,
  cursor: 'pointer',
  backgroundColor: active ? 'rgba(158, 214, 254, 0.1)' : 'transparent',
  color: active ? theme.colors.primary.main : theme.colors.text.primary,
  fontWeight: active ? theme.typography.fontWeights.semiBold : theme.typography.fontWeights.regular,
  '&:hover': {
    backgroundColor: 'rgba(158, 214, 254, 0.1)',
  },
}));

const StatsCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.borderRadius.lg,
  boxShadow: theme.shadows.md,
  height: '100%',
}));

const StatsCardContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing.lg,
  textAlign: 'center',
}));

const StatValue = styled(Typography)(({ theme }) => ({
  fontSize: theme.typography.fontSize['3xl'],
  fontWeight: theme.typography.fontWeights.bold,
  color: theme.colors.primary.main,
  marginBottom: theme.spacing.sm,
}));

const UpcomingClassCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.borderRadius.lg,
  boxShadow: theme.shadows.md,
  marginBottom: theme.spacing.md,
  overflow: 'hidden',
}));

const ClassCardHeader = styled(Box)(({ theme, classType }) => {
  // Determine color based on class type
  let bgColor = theme.colors.primary.main;
  if (classType === 'Yoga') bgColor = '#4caf50';
  if (classType === 'HIIT') bgColor = '#f44336';
  if (classType === 'Strength') bgColor = '#ff9800';
  
  return {
    background: bgColor,
    padding: theme.spacing.md,
    color: 'white',
  };
});

const ClassCardContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing.md,
}));

const ActionButton = styled(Button)(({ theme }) => ({
  ...theme.buttonStyles.action,
  padding: '8px 16px',
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.sm,
}));

const PrimaryButton = styled(Button)(({ theme }) => ({
  ...theme.buttonStyles.onWhite,
  padding: '8px 16px',
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.sm,
}));

const StyledTabs = styled(Tabs)(({ theme }) => ({
  marginBottom: theme.spacing.lg,
  '& .MuiTabs-indicator': {
    backgroundColor: theme.colors.primary.main,
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  textTransform: 'none',
  fontWeight: theme.typography.fontWeights.medium,
  fontSize: theme.typography.fontSize.md,
  '&.Mui-selected': {
    color: theme.colors.primary.main,
    fontWeight: theme.typography.fontWeights.semiBold,
  },
}));

const ProgressCircle = styled(Box)(({ theme }) => ({
  position: 'relative',
  display: 'inline-flex',
  marginBottom: theme.spacing.md,
}));

const ProgressLabel = styled(Box)(({ theme }) => ({
  top: 0,
  left: 0,
  bottom: 0,
  right: 0,
  position: 'absolute',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const MemberDashboard = () => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Mock data for demonstration
  const userStats = {
    classesAttended: 24,
    streak: 7,
    remainingCredits: 12,
    membershipDays: 45,
  };

  const upcomingClasses = [
    {
      id: 1,
      type: 'HIIT',
      name: 'High Intensity Interval Training',
      trainer: 'Alex Johnson',
      date: 'Today',
      time: '18:00 - 19:00',
      location: 'Studio A',
    },
    {
      id: 2,
      type: 'Yoga',
      name: 'Power Yoga',
      trainer: 'Sarah Miller',
      date: 'Tomorrow',
      time: '10:00 - 11:00',
      location: 'Studio B',
    },
    {
      id: 3,
      type: 'Strength',
      name: 'Full Body Strength',
      trainer: 'Mike Williams',
      date: 'Friday, May 24',
      time: '17:30 - 18:30',
      location: 'Main Hall',
    },
  ];

  const achievements = [
    { name: 'First Class', completed: true, progress: 100 },
    { name: '10 Classes', completed: true, progress: 100 },
    { name: '25 Classes', completed: false, progress: 96 },
    { name: '7-Day Streak', completed: true, progress: 100 },
    { name: 'Try 5 Different Classes', completed: false, progress: 80 },
  ];

  return (
    <DashboardContainer>
      <Header>
        <Container maxWidth="lg" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h5" component="h1" sx={{ fontWeight: theme.typography.fontWeights.bold }}>
            Training Club
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body1" sx={{ marginRight: theme.spacing.md }}>
              Welcome, Emma
            </Typography>
            <Avatar sx={{ bgcolor: theme.colors.secondary.main }}>E</Avatar>
          </Box>
        </Container>
      </Header>

      <Box sx={{ display: 'flex' }}>
        <SideNav>
          <Typography variant="h6" component="h2" sx={{ 
            fontWeight: theme.typography.fontWeights.semiBold,
            marginBottom: theme.spacing.lg,
            paddingLeft: theme.spacing.md,
          }}>
            Dashboard
          </Typography>
          <NavItem active={true}>Home</NavItem>
          <NavItem>Schedule</NavItem>
          <NavItem>My Bookings</NavItem>
          <NavItem>Membership</NavItem>
          <NavItem>Leaderboards</NavItem>
          <NavItem>Profile</NavItem>
          <Box sx={{ marginTop: 'auto', paddingTop: theme.spacing.xl }}>
            <NavItem>Settings</NavItem>
            <NavItem>Logout</NavItem>
          </Box>
        </SideNav>

        <MainContent>
          <Typography variant="h4" component="h1" gutterBottom sx={{ 
            fontWeight: theme.typography.fontWeights.bold,
            marginBottom: theme.spacing.lg,
          }}>
            Member Dashboard
          </Typography>

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ marginBottom: theme.spacing.xl }}>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <StatsCardContent>
                  <StatValue>{userStats.classesAttended}</StatValue>
                  <Typography variant="body1">Classes Attended</Typography>
                </StatsCardContent>
              </StatsCard>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <StatsCardContent>
                  <StatValue>{userStats.streak}</StatValue>
                  <Typography variant="body1">Day Streak</Typography>
                </StatsCardContent>
              </StatsCard>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <StatsCardContent>
                  <StatValue>{userStats.remainingCredits}</StatValue>
                  <Typography variant="body1">Credits Remaining</Typography>
                </StatsCardContent>
              </StatsCard>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <StatsCardContent>
                  <StatValue>{userStats.membershipDays}</StatValue>
                  <Typography variant="body1">Days Left</Typography>
                </StatsCardContent>
              </StatsCard>
            </Grid>
          </Grid>

          {/* Tabs for different sections */}
          <StyledTabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <StyledTab label="Upcoming Classes" />
            <StyledTab label="Achievements" />
            <StyledTab label="Activity" />
          </StyledTabs>

          {/* Upcoming Classes Tab */}
          {tabValue === 0 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.lg }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: theme.typography.fontWeights.semiBold }}>
                  Your Upcoming Classes
                </Typography>
                <PrimaryButton>View All Classes</PrimaryButton>
              </Box>
              
              {upcomingClasses.map((classItem) => (
                <UpcomingClassCard key={classItem.id}>
                  <ClassCardHeader classType={classItem.type}>
                    <Typography variant="h6" component="h3" sx={{ fontWeight: theme.typography.fontWeights.semiBold }}>
                      {classItem.name}
                    </Typography>
                    <Typography variant="body2">
                      {classItem.type} with {classItem.trainer}
                    </Typography>
                  </ClassCardHeader>
                  <ClassCardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={8}>
                        <Typography variant="body1" sx={{ marginBottom: 1 }}>
                          <strong>Date:</strong> {classItem.date}
                        </Typography>
                        <Typography variant="body1" sx={{ marginBottom: 1 }}>
                          <strong>Time:</strong> {classItem.time}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Location:</strong> {classItem.location}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4} sx={{ 
                        display: 'flex', 
                        flexDirection: { xs: 'row', md: 'column' }, 
                        justifyContent: { xs: 'flex-start', md: 'center' },
                        alignItems: { xs: 'center', md: 'flex-end' },
                        gap: 2,
                      }}>
                        <ActionButton>Cancel</ActionButton>
                        <PrimaryButton>Add to Calendar</PrimaryButton>
                      </Grid>
                    </Grid>
                  </ClassCardContent>
                </UpcomingClassCard>
              ))}
            </Box>
          )}

          {/* Achievements Tab */}
          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" component="h2" sx={{ 
                fontWeight: theme.typography.fontWeights.semiBold,
                marginBottom: theme.spacing.lg,
              }}>
                Your Achievements
              </Typography>
              
              <Grid container spacing={3}>
                {achievements.map((achievement, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <StatsCard>
                      <StatsCardContent>
                        <ProgressCircle>
                          <CircularProgress
                            variant="determinate"
                            value={achievement.progress}
                            size={80}
                            thickness={4}
                            sx={{ 
                              color: achievement.completed ? theme.colors.status.success : theme.colors.primary.main,
                            }}
                          />
                          <ProgressLabel>
                            <Typography variant="body1" component="div" sx={{ fontWeight: 'bold' }}>
                              {achievement.progress}%
                            </Typography>
                          </ProgressLabel>
                        </ProgressCircle>
                        <Typography variant="h6" component="h3" sx={{ fontWeight: theme.typography.fontWeights.semiBold }}>
                          {achievement.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {achievement.completed ? 'Completed' : 'In Progress'}
                        </Typography>
                      </StatsCardContent>
                    </StatsCard>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Activity Tab */}
          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" component="h2" sx={{ 
                fontWeight: theme.typography.fontWeights.semiBold,
                marginBottom: theme.spacing.lg,
              }}>
                Recent Activity
              </Typography>
              
              <Card sx={{ borderRadius: theme.borderRadius.lg, boxShadow: theme.shadows.md }}>
                <CardContent>
                  <Typography variant="body1" sx={{ fontStyle: 'italic', color: theme.colors.text.secondary }}>
                    Activity tracking will be available in the next update.
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}
        </MainContent>
      </Box>
    </DashboardContainer>
  );
};

export default MemberDashboard;
