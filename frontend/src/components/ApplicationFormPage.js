import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Grid,
  Divider,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon } from '@mui/icons-material';
import CountrySelector from './CountrySelector';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function ApplicationFormPage({ userId, extractedData, onFormComplete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    nationality: '',
    current_university: '',
    current_degree: '',
    major: '',
    cgpa: '',
    gpa_scale: '',
    expected_graduation: '',
    desired_degree: '',
    field_of_study: '',
    english_test: '',
    english_score: '',
    german_level: '',
  });

  useEffect(() => {
    if (extractedData) {
      const newFormData = { ...formData };
      
      if (extractedData.personal_info?.name) {
        newFormData.full_name = extractedData.personal_info.name;
      }
      
      if (extractedData.academic_info) {
        const academic = extractedData.academic_info;
        if (academic.university) newFormData.current_university = academic.university;
        if (academic.degree) newFormData.current_degree = academic.degree;
        if (academic.major) newFormData.major = academic.major;
        if (academic.cgpa) newFormData.cgpa = academic.cgpa.toString();
        if (academic.gpa_scale) newFormData.gpa_scale = academic.gpa_scale.toString();
        if (academic.graduation_date) newFormData.expected_graduation = academic.graduation_date;
      }
      
      if (extractedData.language_info) {
        const lang = extractedData.language_info;
        if (lang.test_type) newFormData.english_test = lang.test_type;
        if (lang.overall_score) newFormData.english_score = lang.overall_score.toString();
      }
      
      setFormData(newFormData);
    }
  }, [extractedData]);

  const handleInputChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleSave = async () => {
    try {
      const applicationData = {
        userId,
        profile: formData,
        countries: selectedCountries,
        preferences: {
          desired_degree: formData.desired_degree,
          field_of_study: formData.field_of_study,
        }
      };

      const response = await axios.post(`${API_URL}/save-application`, applicationData);

      if (response.data.success) {
        onFormComplete(applicationData);
      }
    } catch (error) {
      console.error('Error saving application:', error);
      alert('Failed to save application');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" color="primary">
            Application Form
          </Typography>
          <Button
            variant="outlined"
            startIcon={isEditing ? <SaveIcon /> : <EditIcon />}
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? 'Save Changes' : 'Edit Form'}
          </Button>
        </Box>

        <Alert severity="success" sx={{ mb: 3 }}>
          ✨ Form auto-filled from your documents! Review and edit if needed.
        </Alert>

        <Box sx={{ mb: 4 }}>
          <CountrySelector
            selected={selectedCountries}
            onChange={setSelectedCountries}
          />
        </Box>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Personal Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Full Name"
              value={formData.full_name}
              onChange={handleInputChange('full_name')}
              disabled={!isEditing}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleInputChange('email')}
              disabled={!isEditing}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone}
              onChange={handleInputChange('phone')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nationality"
              value={formData.nationality}
              onChange={handleInputChange('nationality')}
              disabled={!isEditing}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Academic Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Current University"
              value={formData.current_university}
              onChange={handleInputChange('current_university')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Current Degree"
              value={formData.current_degree}
              onChange={handleInputChange('current_degree')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Major / Field of Study"
              value={formData.major}
              onChange={handleInputChange('major')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="CGPA"
              value={formData.cgpa}
              onChange={handleInputChange('cgpa')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="GPA Scale"
              value={formData.gpa_scale}
              onChange={handleInputChange('gpa_scale')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Expected Graduation"
              value={formData.expected_graduation}
              onChange={handleInputChange('expected_graduation')}
              disabled={!isEditing}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Application Preferences
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth disabled={!isEditing}>
              <InputLabel>Desired Degree Level</InputLabel>
              <Select
                value={formData.desired_degree}
                label="Desired Degree Level"
                onChange={handleInputChange('desired_degree')}
              >
                <MenuItem value="Bachelor">Bachelor's</MenuItem>
                <MenuItem value="Masters">Master's</MenuItem>
                <MenuItem value="PhD">PhD</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Field of Study"
              value={formData.field_of_study}
              onChange={handleInputChange('field_of_study')}
              disabled={!isEditing}
            />
          </Grid>
        </Grid>

        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleSave}
          disabled={selectedCountries.length === 0 || !formData.full_name}
          sx={{ mt: 4, py: 1.5 }}
        >
          Save & Continue to Course Assistant
        </Button>
      </Paper>
    </Container>
  );
}