import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Alert,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

const documentTypes = [
  {
    id: 'transcript',
    label: 'Academic Transcript',
    description: 'Upload your official transcript (PDF or DOCX)',
    required: false,
  },
  {
    id: 'cv',
    label: 'CV / Resume',
    description: 'Upload your CV or Resume - we can extract info from this too!',
    required: false,
  },
  {
    id: 'degree',
    label: 'Degree Certificate',
    description: 'Upload your degree certificate if graduated',
    required: false,
  },
  {
    id: 'language_cert',
    label: 'Language Certificate',
    description: 'IELTS, TOEFL, or other language test results',
    required: false,
  },
];

export default function DocumentUploadPage({ userId, onDataExtracted }) {
  const [files, setFiles] = useState({});
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (docType) => (event) => {
    const file = event.target.files[0];
    if (file) {
      setFiles({ ...files, [docType]: file });
    }
  };

  const handleDelete = (docType) => {
    const newFiles = { ...files };
    delete newFiles[docType];
    setFiles(newFiles);
  };

  const handleParse = async () => {
    if (Object.keys(files).length === 0) {
      alert('Please upload at least one document (Transcript or CV)');
      return;
    }

    setLoading(true);
    setProgress(0);

    try {
      const formData = new FormData();
      Object.keys(files).forEach(key => {
        formData.append(key, files[key]);
        console.log(`Adding file: ${key} = ${files[key].name}`);
      });

      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 300);

      console.log('Sending files to backend...');
      const response = await axios.post(`${API_URL}/parse-documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      clearInterval(progressInterval);
      setProgress(100);

      console.log('Response:', response.data);

      if (response.data.success) {
        setTimeout(() => {
          onDataExtracted(response.data.data);
        }, 500);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to parse documents. Please check the console and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" gutterBottom color="primary">
            Upload Your Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Our AI will automatically extract your information from your documents
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          💡 Upload your <strong>Transcript</strong> or <strong>CV/Resume</strong> and we'll automatically fill out your application form using AI!
        </Alert>

        <List>
          {documentTypes.map((doc) => (
            <ListItem
              key={doc.id}
              sx={{
                border: '1px solid #e0e0e0',
                borderRadius: 2,
                mb: 2,
                backgroundColor: files[doc.id] ? '#e8f5e9' : 'white',
              }}
            >
              <ListItemIcon>
                {files[doc.id] ? (
                  <CheckIcon color="success" />
                ) : (
                  <FileIcon color="action" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="h6" sx={{ fontSize: '1rem' }}>
                    {doc.label}
                  </Typography>
                }
                secondary={
                  files[doc.id] ? files[doc.id].name : doc.description
                }
              />
              {files[doc.id] ? (
                <IconButton onClick={() => handleDelete(doc.id)} color="error">
                  <DeleteIcon />
                </IconButton>
              ) : (
                <>
                  <input
                    accept=".pdf,.doc,.docx"
                    style={{ display: 'none' }}
                    id={`file-${doc.id}`}
                    type="file"
                    onChange={handleFileSelect(doc.id)}
                  />
                  <label htmlFor={`file-${doc.id}`}>
                    <Button
                      variant="contained"
                      component="span"
                      startIcon={<UploadIcon />}
                    >
                      Upload
                    </Button>
                  </label>
                </>
              )}
            </ListItem>
          ))}
        </List>

        {loading && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" gutterBottom align="center">
              AI is reading your documents... {progress}%
            </Typography>
            <LinearProgress variant="determinate" value={progress} />
          </Box>
        )}

        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleParse}
          disabled={loading || Object.keys(files).length === 0}
          sx={{ mt: 3, py: 1.5 }}
        >
          {loading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            '🤖 Extract Information with AI'
          )}
        </Button>
      </Paper>
    </Container>
  );
}