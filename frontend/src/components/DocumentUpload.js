import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function DocumentUpload({ userId, onUploadSuccess }) {
  const [formData, setFormData] = useState({
    degreeLevel: '',
    fieldOfStudy: '',
    currentGPA: '',
    expectedGraduation: '',
    englishProficiency: '',
    germanProficiency: '',
  });

  const [documents, setDocuments] = useState({
    transcript: null,
    degree: null,
    language_cert: null,
    other: null,
  });

  const [loading, setLoading] = useState(false);

  const handleInputChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleFileSelect = (docType) => (event) => {
    const file = event.target.files[0];
    if (file) {
      setDocuments({ ...documents, [docType]: file });
    }
  };

  const handleFileDelete = (docType) => {
    setDocuments({ ...documents, [docType]: null });
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    try {
      const formDataToSend = new FormData();
      
      // Add profile data
      formDataToSend.append('userId', userId);
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });
      
      // Add documents
      Object.keys(documents).forEach(key => {
        if (documents[key]) {
          formDataToSend.append(key, documents[key]);
        }
      });
      
      const response = await axios.post(`${API_URL}/upload-profile`, formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.success) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Form Fields */}
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Degree Level</InputLabel>
          <Select
            value={formData.degreeLevel}
            label="Degree Level"
            onChange={handleInputChange('degreeLevel')}
          >
            <MenuItem value="Bachelor">Bachelor</MenuItem>
            <MenuItem value="Masters">Masters</MenuItem>
            <MenuItem value="PhD">PhD</MenuItem>
          </Select>
        </FormControl>

        <TextField
          fullWidth
          label="Field of Study"
          value={formData.fieldOfStudy}
          onChange={handleInputChange('fieldOfStudy')}
          sx={{ mb: 2 }}
          placeholder="e.g., Computer Science"
        />

        <TextField
          fullWidth
          label="Current GPA"
          value={formData.currentGPA}
          onChange={handleInputChange('currentGPA')}
          sx={{ mb: 2 }}
          placeholder="e.g., 3.5/4.0"
        />

        <TextField
          fullWidth
          label="Expected Graduation"
          value={formData.expectedGraduation}
          onChange={handleInputChange('expectedGraduation')}
          sx={{ mb: 2 }}
          placeholder="e.g., May 2025"
        />

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>English Proficiency</InputLabel>
          <Select
            value={formData.englishProficiency}
            label="English Proficiency"
            onChange={handleInputChange('englishProficiency')}
          >
            <MenuItem value="Native">Native</MenuItem>
            <MenuItem value="C2">C2 - Proficient</MenuItem>
            <MenuItem value="C1">C1 - Advanced</MenuItem>
            <MenuItem value="B2">B2 - Upper Intermediate</MenuItem>
            <MenuItem value="B1">B1 - Intermediate</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>German Proficiency</InputLabel>
          <Select
            value={formData.germanProficiency}
            label="German Proficiency"
            onChange={handleInputChange('germanProficiency')}
          >
            <MenuItem value="None">None</MenuItem>
            <MenuItem value="A1">A1 - Beginner</MenuItem>
            <MenuItem value="A2">A2 - Elementary</MenuItem>
            <MenuItem value="B1">B1 - Intermediate</MenuItem>
            <MenuItem value="B2">B2 - Upper Intermediate</MenuItem>
            <MenuItem value="C1">C1 - Advanced</MenuItem>
            <MenuItem value="C2">C2 - Proficient</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Document Upload */}
      <Typography variant="h6" gutterBottom>
        Documents
      </Typography>

      <List>
        {[
          { key: 'transcript', label: 'Academic Transcript' },
          { key: 'degree', label: 'Degree Certificate' },
          { key: 'language_cert', label: 'Language Certificate (IELTS/TOEFL)' },
          { key: 'other', label: 'Other Documents' },
        ].map((doc) => (
          <ListItem key={doc.key} sx={{ px: 0 }}>
            <ListItemIcon>
              <FileIcon />
            </ListItemIcon>
            <ListItemText 
              primary={doc.label}
              secondary={documents[doc.key]?.name || 'No file selected'}
            />
            {documents[doc.key] ? (
              <IconButton onClick={() => handleFileDelete(doc.key)} color="error">
                <DeleteIcon />
              </IconButton>
            ) : (
              <>
                <input
                  accept=".pdf,.doc,.docx"
                  style={{ display: 'none' }}
                  id={`upload-${doc.key}`}
                  type="file"
                  onChange={handleFileSelect(doc.key)}
                />
                <label htmlFor={`upload-${doc.key}`}>
                  <Button component="span" size="small" startIcon={<UploadIcon />}>
                    Upload
                  </Button>
                </label>
              </>
            )}
          </ListItem>
        ))}
      </List>

      <Button
        fullWidth
        variant="contained"
        size="large"
        onClick={handleSubmit}
        disabled={loading || !formData.degreeLevel}
        sx={{ mt: 3 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Save Profile'}
      </Button>
    </Box>
  );
}