// Theme configuration for the Training Club fitness platform
// Based on Apple-style design principles and Training Club branding

export const colors = {
  // Primary brand colors
  primary: {
    main: '#9ed6fe', // Main blue
    light: '#c9dee7', // Secondary blue
    dark: '#7ab0d8', // Darker shade for hover states
    contrastText: '#ffffff',
  },
  
  // Secondary colors
  secondary: {
    main: '#f16c13', // Button color
    light: '#ff8c43',
    dark: '#d15000',
    contrastText: '#ffffff',
  },
  
  // Neutral tones
  neutral: {
    main: '#c8b4a3', // Neutral tone for other elements
    light: '#e5d9cf',
    dark: '#a99179',
    contrastText: '#ffffff',
  },
  
  // Background colors
  background: {
    default: '#ffffff',
    paper: '#f8f9fa',
    gradient: 'linear-gradient(to bottom, #9ed6fe, #ffffff)',
    gradientDark: 'linear-gradient(to bottom, #7ab0d8, #ffffff)',
  },
  
  // Text colors
  text: {
    primary: '#333333',
    secondary: '#666666',
    disabled: '#999999',
    hint: '#999999',
  },
  
  // Status colors
  status: {
    success: '#4caf50',
    info: '#2196f3',
    warning: '#ff9800',
    error: '#f44336',
  },
  
  // Specific UI element colors
  ui: {
    divider: '#e0e0e0',
    border: '#dddddd',
    shadow: 'rgba(0, 0, 0, 0.1)',
  }
};

export const typography = {
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  
  // Font weights
  fontWeights: {
    light: 300,
    regular: 400,
    medium: 500,
    semiBold: 600,
    bold: 700,
  },
  
  // Font sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    md: '1rem',       // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },
  
  // Line heights
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
  
  // Letter spacing
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
  },
};

export const spacing = {
  unit: 8,
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '1rem',       // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  '2xl': '2.5rem',  // 40px
  '3xl': '3rem',    // 48px
};

export const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  full: '9999px',   // Fully rounded (for circles)
};

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

export const transitions = {
  default: 'all 0.2s ease-in-out',
  fast: 'all 0.1s ease-in-out',
  slow: 'all 0.3s ease-in-out',
};

export const zIndices = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
};

// Button styles based on user preferences
export const buttonStyles = {
  // White buttons on blue background
  onBlue: {
    backgroundColor: '#ffffff',
    color: colors.primary.main,
    border: 'none',
    '&:hover': {
      backgroundColor: '#f0f0f0',
    },
  },
  
  // Blue buttons on white background
  onWhite: {
    backgroundColor: colors.primary.main,
    color: '#ffffff',
    border: 'none',
    '&:hover': {
      backgroundColor: colors.primary.dark,
    },
  },
  
  // Action buttons (orange)
  action: {
    backgroundColor: colors.secondary.main,
    color: '#ffffff',
    border: 'none',
    '&:hover': {
      backgroundColor: colors.secondary.dark,
    },
  },
  
  // Neutral buttons
  neutral: {
    backgroundColor: colors.neutral.main,
    color: '#ffffff',
    border: 'none',
    '&:hover': {
      backgroundColor: colors.neutral.dark,
    },
  },
  
  // Text buttons (no background)
  text: {
    backgroundColor: 'transparent',
    color: colors.primary.main,
    border: 'none',
    '&:hover': {
      backgroundColor: 'rgba(158, 214, 254, 0.1)',
    },
  },
  
  // Outlined buttons
  outlined: {
    backgroundColor: 'transparent',
    color: colors.primary.main,
    border: `1px solid ${colors.primary.main}`,
    '&:hover': {
      backgroundColor: 'rgba(158, 214, 254, 0.1)',
    },
  },
};

// Gradient styles based on user preferences
export const gradients = {
  // Landing page background gradient (blue to white)
  landingPage: 'linear-gradient(to bottom, #9ed6fe, #ffffff)',
  
  // Page scroll gradient (white to blue)
  pageScroll: 'linear-gradient(to bottom, #ffffff, #9ed6fe)',
  
  // Night mode gradient (dark blue to white)
  nightMode: 'linear-gradient(to bottom, #7ab0d8, #ffffff)',
  
  // No orange gradients as per user preference
};

// Apple-style design principles
export const appleDesignPrinciples = {
  // Soft shadows for depth
  elevation: {
    low: '0 2px 4px rgba(0, 0, 0, 0.05)',
    medium: '0 4px 8px rgba(0, 0, 0, 0.08)',
    high: '0 8px 16px rgba(0, 0, 0, 0.12)',
  },
  
  // Blur effects for modals and overlays
  blur: {
    light: 'blur(8px)',
    medium: 'blur(16px)',
    heavy: 'blur(24px)',
  },
  
  // Subtle animations
  animation: {
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
  },
  
  // Translucency effects
  translucency: {
    light: 'rgba(255, 255, 255, 0.7)',
    medium: 'rgba(255, 255, 255, 0.5)',
    heavy: 'rgba(255, 255, 255, 0.3)',
  },
};

// Responsive breakpoints
export const breakpoints = {
  xs: '0px',
  sm: '600px',
  md: '960px',
  lg: '1280px',
  xl: '1920px',
};

// Default theme object
const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  zIndices,
  buttonStyles,
  gradients,
  appleDesignPrinciples,
  breakpoints,
};

export default theme;
