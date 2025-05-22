import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Grid, Card, CardContent, 
  Button, Chip, Avatar, List, ListItem, ListItemText,
  ListItemAvatar, Divider, IconButton, Alert, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem,
  ImageList, ImageListItem, ImageListItemBar
} from '@mui/material';
import { 
  PhotoCamera, CloudUpload, Lock, Visibility,
  Download, Share, Delete, Info
} from '@mui/icons-material';
import axios from 'axios';

const PhotoGallery = () => {
  const [photos, setPhotos] = useState([
    { 
      id: 1, 
      url: 'https://source.unsplash.com/random/800x600/?fitness-class', 
      className: 'Morning HIIT', 
      date: '2025-05-15',
      trainer: 'Alex Johnson',
      accessCode: 'HIIT0515',
      isPublic: true
    },
    { 
      id: 2, 
      url: 'https://source.unsplash.com/random/800x600/?yoga-class', 
      className: 'Power Yoga', 
      date: '2025-05-12',
      trainer: 'Maria Garcia',
      accessCode: 'YOGA0512',
      isPublic: true
    },
    { 
      id: 3, 
      url: 'https://source.unsplash.com/random/800x600/?strength-training', 
      className: 'Evening Strength', 
      date: '2025-05-10',
      trainer: 'Thomas Lee',
      accessCode: 'STRG0510',
      isPublic: false
    }
  ]);
  
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showAccessCodeDialog, setShowAccessCodeDialog] = useState(false);
  const [showPhotoDetailDialog, setShowPhotoDetailDialog] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [accessCode, setAccessCode] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [uploadData, setUploadData] = useState({
    file: null,
    className: '',
    accessCode: '',
    isPublic: false
  });
  
  const handleOpenUploadDialog = () => {
    setShowUploadDialog(true);
  };
  
  const handleCloseUploadDialog = () => {
    setShowUploadDialog(false);
    setUploadData({
      file: null,
      className: '',
      accessCode: '',
      isPublic: false
    });
  };
  
  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setUploadData({
        ...uploadData,
        file: event.target.files[0]
      });
    }
  };
  
  const handleUploadDataChange = (field, value) => {
    setUploadData({
      ...uploadData,
      [field]: value
    });
  };
  
  const handleUploadPhoto = () => {
    if (!uploadData.file) {
      setMessage({ type: 'error', text: 'Please select a file to upload' });
      return;
    }
    
    if (!uploadData.className) {
      setMessage({ type: 'error', text: 'Please enter a class name' });
      return;
    }
    
    if (!uploadData.accessCode) {
      setMessage({ type: 'error', text: 'Please enter an access code' });
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Create new photo object
      const newPhoto = {
        id: photos.length + 1,
        url: URL.createObjectURL(uploadData.file),
        className: uploadData.className,
        date: new Date().toISOString().split('T')[0],
        trainer: 'Current Trainer', // In a real app, this would be the current user
        accessCode: uploadData.accessCode,
        isPublic: uploadData.isPublic
      };
      
      setPhotos([newPhoto, ...photos]);
      
      setIsLoading(false);
      handleCloseUploadDialog();
      setMessage({ type: 'success', text: 'Photo uploaded successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }, 1500);
  };
  
  const handleOpenAccessCodeDialog = () => {
    setShowAccessCodeDialog(true);
  };
  
  const handleCloseAccessCodeDialog = () => {
    setShowAccessCodeDialog(false);
    setAccessCode('');
  };
  
  const handleSubmitAccessCode = () => {
    if (!accessCode) {
      setMessage({ type: 'error', text: 'Please enter an access code' });
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Check if access code matches any photos
      const matchingPhotos = photos.filter(photo => 
        photo.accessCode.toLowerCase() === accessCode.toLowerCase()
      );
      
      if (matchingPhotos.length > 0) {
        setMessage({ type: 'success', text: `Access granted to ${matchingPhotos.length} photos!` });
        handleCloseAccessCodeDialog();
      } else {
        setMessage({ type: 'error', text: 'Invalid access code. Please try again.' });
      }
      
      setIsLoading(false);
    }, 1000);
  };
  
  const handleOpenPhotoDetail = (photo) => {
    setSelectedPhoto(photo);
    setShowPhotoDetailDialog(true);
  };
  
  const handleClosePhotoDetail = () => {
    setShowPhotoDetailDialog(false);
    setSelectedPhoto(null);
  };
  
  const handleDownloadPhoto = (photo) => {
    // In a real app, this would trigger a download
    console.log('Downloading photo:', photo.id);
    setMessage({ type: 'success', text: 'Photo download started!' });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Class Photos
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        View and download photos from your classes, or upload new ones if you're a trainer.
      </Typography>
      
      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<Lock />}
          onClick={handleOpenAccessCodeDialog}
        >
          Enter Access Code
        </Button>
        
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          onClick={handleOpenUploadDialog}
          color="primary"
        >
          Upload Photos
        </Button>
      </Box>
      
      {photos.length === 0 ? (
        <Paper sx={{ p: 5, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No photos available. Enter an access code to view class photos or upload new ones.
          </Typography>
        </Paper>
      ) : (
        <ImageList cols={3} gap={16}>
          {photos.map((photo) => (
            <ImageListItem 
              key={photo.id}
              sx={{ 
                cursor: 'pointer',
                borderRadius: 1,
                overflow: 'hidden',
                boxShadow: 1,
                '&:hover': {
                  boxShadow: 3,
                  '& .MuiImageListItemBar-root': {
                    opacity: 1
                  }
                }
              }}
              onClick={() => handleOpenPhotoDetail(photo)}
            >
              <img
                src={photo.url}
                alt={photo.className}
                loading="lazy"
                style={{ height: 250, objectFit: 'cover' }}
              />
              <ImageListItemBar
                title={photo.className}
                subtitle={photo.date}
                sx={{
                  opacity: 0.9,
                  transition: 'opacity 0.3s'
                }}
                actionIcon={
                  <IconButton
                    sx={{ color: 'white' }}
                    aria-label={`info about ${photo.className}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenPhotoDetail(photo);
                    }}
                  >
                    <Info />
                  </IconButton>
                }
              />
              {!photo.isPublic && (
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    top: 8, 
                    right: 8, 
                    bgcolor: 'rgba(0,0,0,0.5)',
                    borderRadius: '50%',
                    p: 0.5
                  }}
                >
                  <Lock fontSize="small" sx={{ color: 'white' }} />
                </Box>
              )}
            </ImageListItem>
          ))}
        </ImageList>
      )}
      
      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onClose={handleCloseUploadDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Class Photos</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              Upload photos from your classes. Members can access them using the code you provide.
            </Typography>
            
            <Box 
              sx={{ 
                border: '2px dashed #ccc', 
                borderRadius: 2, 
                p: 3, 
                textAlign: 'center',
                mb: 3,
                bgcolor: uploadData.file ? '#f8f9fa' : 'transparent'
              }}
            >
              {uploadData.file ? (
                <Box>
                  <Typography variant="body1" gutterBottom>
                    {uploadData.file.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {(uploadData.file.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    sx={{ mt: 1 }}
                    onClick={() => handleUploadDataChange('file', null)}
                  >
                    Remove
                  </Button>
                </Box>
              ) : (
                <Box>
                  <input
                    accept="image/*"
                    style={{ display: 'none' }}
                    id="photo-upload"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="photo-upload">
                    <Button
                      variant="contained"
                      component="span"
                      startIcon={<PhotoCamera />}
                    >
                      Select Photo
                    </Button>
                  </label>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Drag and drop or click to select
                  </Typography>
                </Box>
              )}
            </Box>
            
            <TextField
              label="Class Name"
              fullWidth
              margin="normal"
              value={uploadData.className}
              onChange={(e) => handleUploadDataChange('className', e.target.value)}
              placeholder="e.g., Morning HIIT"
            />
            
            <TextField
              label="Access Code"
              fullWidth
              margin="normal"
              value={uploadData.accessCode}
              onChange={(e) => handleUploadDataChange('accessCode', e.target.value)}
              placeholder="e.g., HIIT0521"
              helperText="Members will need this code to access the photos"
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Visibility</InputLabel>
              <Select
                value={uploadData.isPublic}
                onChange={(e) => handleUploadDataChange('isPublic', e.target.value)}
                label="Visibility"
              >
                <MenuItem value={true}>Public (visible to all members)</MenuItem>
                <MenuItem value={false}>Private (requires access code)</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog}>Cancel</Button>
          <Button 
            onClick={handleUploadPhoto} 
            variant="contained" 
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Access Code Dialog */}
      <Dialog open={showAccessCodeDialog} onClose={handleCloseAccessCodeDialog} maxWidth="xs" fullWidth>
        <DialogTitle>Enter Access Code</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              Enter the access code provided by your trainer to view class photos.
            </Typography>
            
            <TextField
              label="Access Code"
              fullWidth
              margin="normal"
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
              placeholder="e.g., HIIT0521"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAccessCodeDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmitAccessCode} 
            variant="contained" 
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Photo Detail Dialog */}
      {selectedPhoto && (
        <Dialog open={showPhotoDetailDialog} onClose={handleClosePhotoDetail} maxWidth="md" fullWidth>
          <DialogContent sx={{ p: 0 }}>
            <img
              src={selectedPhoto.url}
              alt={selectedPhoto.className}
              style={{ width: '100%', maxHeight: '70vh', objectFit: 'contain' }}
            />
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedPhoto.className}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {selectedPhoto.date} • Trainer: {selectedPhoto.trainer}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<Download />}
                  onClick={() => handleDownloadPhoto(selectedPhoto)}
                  color="primary"
                >
                  Download
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Share />}
                >
                  Share
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </Dialog>
      )}
    </Box>
  );
};

export default PhotoGallery;
