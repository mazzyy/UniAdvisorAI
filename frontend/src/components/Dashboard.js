import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import DocumentUpload from './DocumentUpload';
import ChatInterface from './ChatInterface';

export default function Dashboard() {
  const [userId] = useState('user_' + Date.now());
  const [profileUploaded, setProfileUploaded] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleProfileUpload = () => {
    setProfileUploaded(true);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <Box>
      {showSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile uploaded successfully! You can now chat to find courses.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Left Column - Document Upload */}
        <Grid item xs={12} md={5}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom color="primary">
              Your Profile
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Upload your academic documents to get personalized recommendations
            </Typography>
            <DocumentUpload 
              userId={userId} 
              onUploadSuccess={handleProfileUpload}
            />
          </Paper>
        </Grid>

        {/* Right Column - Chat Interface */}
        <Grid item xs={12} md={7}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom color="primary">
              Course Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Ask questions about courses, requirements, or universities
            </Typography>
            <ChatInterface userId={userId} profileUploaded={profileUploaded} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}