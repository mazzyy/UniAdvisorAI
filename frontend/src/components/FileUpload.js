import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

const documentTypes = [
  {
    id: 'transcript',
    label: 'Academic Transcript',
    required: true,
    description: 'Official transcript from your current/previous institution',
    accept: '.pdf,.doc,.docx',
  },
  {
    id: 'degree',
    label: 'Degree Certificate',
    required: false,
    description: 'Your degree certificate (if already graduated)',
    accept: '.pdf,.doc,.docx',
  },
  {
    id: 'ielts',
    label: 'IELTS Certificate',
    required: false,
    description: 'English language proficiency test result',
    accept: '.pdf,.jpg,.jpeg,.png',
  },
  {
    id: 'toefl',
    label: 'TOEFL Certificate',
    required: false,
    description: 'English language proficiency test result',
    accept: '.pdf,.jpg,.jpeg,.png',
  },
  {
    id: 'goethe',
    label: 'Goethe Certificate',
    required: false,
    description: 'German language proficiency test result',
    accept: '.pdf,.jpg,.jpeg,.png',
  },
  {
    id: 'cv',
    label: 'CV / Resume',
    required: false,
    description: 'Your curriculum vitae',
    accept: '.pdf,.doc,.docx',
  },
  {
    id: 'motivation',
    label: 'Motivation Letter',
    required: false,
    description: 'Letter explaining your motivation to study in Germany',
    accept: '.pdf,.doc,.docx',
  },
  {
    id: 'passport',
    label: 'Passport Copy',
    required: false,
    description: 'Copy of your passport',
    accept: '.pdf,.jpg,.jpeg,.png',
  },
];

export default function FileUpload({ documents, onUpdate }) {
  const [uploadedDocs, setUploadedDocs] = useState(documents || {});
  const [dragOver, setDragOver] = useState(null);

  const handleFileSelect = (docType) => (event) => {
    const file = event.target.files[0];
    if (file) {
      const newDocs = { ...uploadedDocs, [docType]: file };
      setUploadedDocs(newDocs);
      onUpdate(newDocs);
    }
  };

  const handleFileDelete = (docType) => {
    const newDocs = { ...uploadedDocs };
    delete newDocs[docType];
    setUploadedDocs(newDocs);
    onUpdate(newDocs);
  };

  const handleDragOver = (docType) => (event) => {
    event.preventDefault();
    setDragOver(docType);
  };

  const handleDragLeave = () => {
    setDragOver(null);
  };

  const handleDrop = (docType) => (event) => {
    event.preventDefault();
    setDragOver(null);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      const newDocs = { ...uploadedDocs, [docType]: file };
      setUploadedDocs(newDocs);
      onUpdate(newDocs);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        Upload your academic documents to help us find the best matching programs for you.
        Required documents are marked with a red asterisk (*).
      </Alert>

      <Grid container spacing={3}>
        {documentTypes.map((docType) => (
          <Grid item xs={12} md={6} key={docType.id}>
            <Paper
              elevation={uploadedDocs[docType.id] ? 3 : 1}
              sx={{
                p: 2,
                border: dragOver === docType.id ? '2px dashed #1976d2' : '1px solid #e0e0e0',
                borderColor: uploadedDocs[docType.id] ? 'success.main' : 'divider',
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: 3,
                },
              }}
              onDragOver={handleDragOver(docType.id)}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop(docType.id)}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  {docType.label}
                  {docType.required && (
                    <Chip
                      label="Required"
                      color="error"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Typography>
                {uploadedDocs[docType.id] && (
                  <CheckIcon color="success" />
                )}
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {docType.description}
              </Typography>

              {uploadedDocs[docType.id] ? (
                <Box>
                  <List dense>
                    <ListItem
                      secondaryAction={
                        <IconButton
                          edge="end"
                          onClick={() => handleFileDelete(docType.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      }
                    >
                      <ListItemIcon>
                        <FileIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={uploadedDocs[docType.id].name}
                        secondary={formatFileSize(uploadedDocs[docType.id].size)}
                      />
                    </ListItem>
                  </List>
                </Box>
              ) : (
                <Box>
                  <input
                    accept={docType.accept}
                    style={{ display: 'none' }}
                    id={`file-upload-${docType.id}`}
                    type="file"
                    onChange={handleFileSelect(docType.id)}
                  />
                  <label htmlFor={`file-upload-${docType.id}`}>
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<UploadIcon />}
                      fullWidth
                    >
                      Choose File or Drag & Drop
                    </Button>
                  </label>
                  <Typography
                    variant="caption"
                    display="block"
                    sx={{ mt: 1, textAlign: 'center' }}
                    color="text.secondary"
                  >
                    Accepted: {docType.accept}
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Alert severity="success">
          <Typography variant="body2">
            <strong>Uploaded:</strong> {Object.keys(uploadedDocs).length} / {documentTypes.length} documents
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
}