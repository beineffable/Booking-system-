import React from 'react';
import { styled } from '@mui/material/styles';
import { Box, Container, Typography, Button, Grid, Card, CardContent, Avatar } from '@mui/material';
import theme from '../styles/theme';

// Styled components using Training Club branding
const HeroSection = styled(Box)(({ theme }) => ({
  background: theme.gradients.landingPage,
  padding: '120px 0 80px',
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
  '@media (max-width: 600px)': {
    padding: '80px 0 60px',
  },
}));

const GradientTransition = styled(Box)({
  position: 'absolute',
  bottom: 0,
  left: 0,
  right: 0,
  height: '100px',
  background: 'linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,1))',
});

const SectionTitle = styled(Typography)(({ theme }) => ({
  fontWeight: theme.typography.fontWeights.bold,
  marginBottom: theme.spacing.lg,
  color: theme.colors.text.primary,
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  borderRadius: theme.borderRadius.lg,
  boxShadow: theme.shadows.md,
  transition: theme.transitions.default,
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: theme.shadows.lg,
  },
}));

const ActionButton = styled(Button)(({ theme }) => ({
  ...theme.buttonStyles.action,
  padding: '12px 24px',
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.md,
}));

const PrimaryButton = styled(Button)(({ theme, background }) => ({
  ...(background === 'blue' ? theme.buttonStyles.onBlue : theme.buttonStyles.onWhite),
  padding: '12px 24px',
  borderRadius: theme.borderRadius.md,
  fontWeight: theme.typography.fontWeights.semiBold,
  textTransform: 'none',
  fontSize: theme.typography.fontSize.md,
}));

const LeaderboardCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.borderRadius.lg,
  boxShadow: theme.shadows.md,
  marginBottom: theme.spacing.md,
  overflow: 'hidden',
}));

const LeaderboardHeader = styled(Box)(({ theme }) => ({
  background: theme.colors.primary.main,
  padding: theme.spacing.md,
  color: 'white',
}));

const LeaderboardItem = styled(Box)(({ theme, isCurrentUser }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing.md,
  borderBottom: `1px solid ${theme.colors.ui.divider}`,
  backgroundColor: isCurrentUser ? 'rgba(158, 214, 254, 0.1)' : 'transparent',
}));

const RankBadge = styled(Box)(({ theme }) => ({
  width: '30px',
  height: '30px',
  borderRadius: theme.borderRadius.full,
  backgroundColor: theme.colors.primary.main,
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontWeight: theme.typography.fontWeights.bold,
  marginRight: theme.spacing.md,
}));

const UserAvatar = styled(Avatar)(({ theme }) => ({
  marginRight: theme.spacing.md,
}));

const HomePage = () => {
  // Mock data for demonstration
  const leaderboardData = [
    { id: 1, name: 'Sarah Johnson', score: 42, avatar: '/avatars/user1.jpg' },
    { id: 2, name: 'Michael Chen', score: 38, avatar: '/avatars/user2.jpg' },
    { id: 3, name: 'Emma Wilson', score: 35, avatar: '/avatars/user3.jpg' },
    { id: 4, name: 'James Rodriguez', score: 31, avatar: '/avatars/user4.jpg' },
    { id: 5, name: 'Current User', score: 28, avatar: '/avatars/user5.jpg', isCurrentUser: true },
  ];

  const features = [
    {
      title: 'Flexible Memberships',
      description: 'Choose from various membership options that fit your schedule and budget.',
      icon: '🏆',
    },
    {
      title: 'Class Variety',
      description: 'Access a wide range of classes from strength training to cardio and yoga.',
      icon: '🏋️‍♀️',
    },
    {
      title: 'Performance Tracking',
      description: 'Monitor your progress and compete on leaderboards with other members.',
      icon: '📊',
    },
    {
      title: 'Mobile Access',
      description: 'Book classes, manage your membership, and track progress on the go.',
      icon: '📱',
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <HeroSection>
        <Container maxWidth="md">
          <Typography variant="h1" component="h1" gutterBottom sx={{ 
            fontSize: { xs: '2.5rem', md: '3.5rem' },
            fontWeight: theme.typography.fontWeights.bold,
            color: theme.colors.text.primary,
          }}>
            Training Club
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom sx={{ 
            fontWeight: theme.typography.fontWeights.medium,
            color: theme.colors.text.secondary,
            marginBottom: theme.spacing.xl,
          }}>
            Elevate your fitness journey with our premium training experience
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <ActionButton size="large">
              Join Now
            </ActionButton>
            <PrimaryButton size="large" background="blue">
              View Schedule
            </PrimaryButton>
          </Box>
        </Container>
        <GradientTransition />
      </HeroSection>

      {/* Features Section */}
      <Box sx={{ py: 8 }}>
        <Container maxWidth="lg">
          <SectionTitle variant="h3" component="h2" align="center">
            Why Choose Training Club
          </SectionTitle>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <FeatureCard>
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Typography variant="h1" component="div" sx={{ fontSize: '3rem', mb: 2 }}>
                      {feature.icon}
                    </Typography>
                    <Typography variant="h6" component="h3" gutterBottom sx={{ 
                      fontWeight: theme.typography.fontWeights.semiBold,
                      mb: 1,
                    }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </FeatureCard>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Leaderboard Preview Section */}
      <Box sx={{ py: 8, backgroundColor: theme.colors.background.paper }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <SectionTitle variant="h3" component="h2">
                Community Leaderboard
              </SectionTitle>
              <Typography variant="body1" paragraph>
                Join our community of fitness enthusiasts and track your progress. Compete with others, earn achievements, and stay motivated on your fitness journey.
              </Typography>
              <PrimaryButton background="white" sx={{ mt: 2 }}>
                View All Leaderboards
              </PrimaryButton>
            </Grid>
            <Grid item xs={12} md={6}>
              <LeaderboardCard>
                <LeaderboardHeader>
                  <Typography variant="h6" component="h3" sx={{ fontWeight: theme.typography.fontWeights.semiBold }}>
                    Class Attendance Leaders
                  </Typography>
                </LeaderboardHeader>
                {leaderboardData.map((user, index) => (
                  <LeaderboardItem key={user.id} isCurrentUser={user.isCurrentUser}>
                    <RankBadge>{index + 1}</RankBadge>
                    <UserAvatar src={user.avatar} alt={user.name}>
                      {user.name.charAt(0)}
                    </UserAvatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: user.isCurrentUser ? 'bold' : 'normal' }}>
                        {user.name}
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                      {user.score} classes
                    </Typography>
                  </LeaderboardItem>
                ))}
              </LeaderboardCard>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Call to Action Section */}
      <Box sx={{ 
        py: 8, 
        background: theme.gradients.pageScroll,
        textAlign: 'center',
      }}>
        <Container maxWidth="md">
          <SectionTitle variant="h3" component="h2">
            Ready to Start Your Fitness Journey?
          </SectionTitle>
          <Typography variant="body1" paragraph sx={{ mb: 4 }}>
            Join Training Club today and experience the difference. Our state-of-the-art facilities, expert trainers, and supportive community are waiting for you.
          </Typography>
          <ActionButton size="large">
            Become a Member
          </ActionButton>
        </Container>
      </Box>
    </Box>
  );
};

export default HomePage;
