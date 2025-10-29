import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FormIcon,
  Chat as ChatIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

export default function Navbar({ currentPage, onPageChange }) {
  return (
    <AppBar position="sticky" elevation={2}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <SchoolIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Study Abroad Application System
          </Typography>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              color="inherit"
              startIcon={<UploadIcon />}
              onClick={() => onPageChange('upload')}
              variant={currentPage === 'upload' ? 'outlined' : 'text'}
              sx={{
                borderColor: currentPage === 'upload' ? 'white' : 'transparent'
              }}
            >
              Upload Documents
            </Button>
            <Button
              color="inherit"
              startIcon={<FormIcon />}
              onClick={() => onPageChange('form')}
              variant={currentPage === 'form' ? 'outlined' : 'text'}
              sx={{
                borderColor: currentPage === 'form' ? 'white' : 'transparent'
              }}
            >
              Application Form
            </Button>
            <Button
              color="inherit"
              startIcon={<ChatIcon />}
              onClick={() => onPageChange('chat')}
              variant={currentPage === 'chat' ? 'outlined' : 'text'}
              sx={{
                borderColor: currentPage === 'chat' ? 'white' : 'transparent'
              }}
            >
              Course Assistant
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}