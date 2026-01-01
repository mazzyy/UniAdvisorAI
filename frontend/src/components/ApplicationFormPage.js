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
  IconButton,
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon, Lock as LockIcon, LockOpen as UnlockIcon } from '@mui/icons-material';
import CountrySelector from './CountrySelector';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5001/api';

export default function ApplicationFormPage({ userId, extractedData, onFormComplete }) {
  const [isEditing, setIsEditing] = useState(true); // Start in edit mode
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
      console.log("📥 Extracted data received:", extractedData);
      const newFormData = { ...formData };
      
      // Personal Info
      if (extractedData.personal_info?.name) {
        newFormData.full_name = extractedData.personal_info.name;
        console.log("✅ Set name:", extractedData.personal_info.name);
      }
      
      // Academic Info
      if (extractedData.academic_info) {
        const academic = extractedData.academic_info;
        if (academic.university) {
          newFormData.current_university = academic.university;
          console.log("✅ Set university:", academic.university);
        }
        if (academic.degree) {
          newFormData.current_degree = academic.degree;
          console.log("✅ Set degree:", academic.degree);
        }
        if (academic.major) {
          newFormData.major = academic.major;
          console.log("✅ Set major:", academic.major);
        }
        if (academic.cgpa) {
          newFormData.cgpa = academic.cgpa.toString();
          console.log("✅ Set CGPA:", academic.cgpa);
        }
        if (academic.gpa_scale) {
          newFormData.gpa_scale = academic.gpa_scale.toString();
          console.log("✅ Set GPA scale:", academic.gpa_scale);
        }
        if (academic.graduation_date) {
          newFormData.expected_graduation = academic.graduation_date;
          console.log("✅ Set graduation date:", academic.graduation_date);
        }
      }
      
      // Language Info
      if (extractedData.language_info) {
        const lang = extractedData.language_info;
        if (lang.test_type) {
          newFormData.english_test = lang.test_type;
          console.log("✅ Set language test:", lang.test_type);
        }
        if (lang.overall_score) {
          newFormData.english_score = lang.overall_score.toString();
          console.log("✅ Set language score:", lang.overall_score);
        }
      }
      
      console.log("📝 Final form data:", newFormData);
      setFormData(newFormData);
    }
  }, [extractedData]);

  const handleInputChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const toggleEdit = () => {
    setIsEditing(!isEditing);
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
        alert('Application saved successfully!');
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
            startIcon={isEditing ? <LockIcon /> : <UnlockIcon />}
            onClick={toggleEdit}
          >
            {isEditing ? 'Lock Form' : 'Unlock to Edit'}
          </Button>
        </Box>

        {extractedData ? (
          <Alert severity="success" sx={{ mb: 3 }}>
            ✨ Form auto-filled from your documents! Review and edit if needed.
          </Alert>
        ) : (
          <Alert severity="info" sx={{ mb: 3 }}>
            Fill out the form manually or upload documents to auto-fill.
          </Alert>
        )}

        {/* Country Selection */}
        <Box sx={{ mb: 4 }}>
          <CountrySelector
            selected={selectedCountries}
            onChange={setSelectedCountries}
          />
        </Box>

        <Divider sx={{ my: 4 }} />

        {/* Personal Information */}
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

        {/* Academic Information */}
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
              helperText="e.g., Bachelor of Science in Computer Science"
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
              type="number"
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
              helperText="e.g., 4.0, 10.0"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Expected Graduation"
              value={formData.expected_graduation}
              onChange={handleInputChange('expected_graduation')}
              disabled={!isEditing}
              helperText="e.g., May 2025"
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        {/* Application Preferences */}
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
                <MenuItem value="">Select...</MenuItem>
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
              helperText="What do you want to study?"
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        {/* Language Proficiency */}
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Language Proficiency
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth disabled={!isEditing}>
              <InputLabel>English Test</InputLabel>
              <Select
                value={formData.english_test}
                label="English Test"
                onChange={handleInputChange('english_test')}
              >
                <MenuItem value="">None</MenuItem>
                <MenuItem value="IELTS">IELTS</MenuItem>
                <MenuItem value="TOEFL">TOEFL</MenuItem>
                <MenuItem value="PTE">PTE</MenuItem>
                <MenuItem value="Duolingo">Duolingo</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="English Test Score"
              value={formData.english_score}
              onChange={handleInputChange('english_score')}
              disabled={!isEditing}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth disabled={!isEditing}>
              <InputLabel>German Level</InputLabel>
              <Select
                value={formData.german_level}
                label="German Level"
                onChange={handleInputChange('german_level')}
              >
                <MenuItem value="">None</MenuItem>
                <MenuItem value="A1">A1 - Beginner</MenuItem>
                <MenuItem value="A2">A2 - Elementary</MenuItem>
                <MenuItem value="B1">B1 - Intermediate</MenuItem>
                <MenuItem value="B2">B2 - Upper Intermediate</MenuItem>
                <MenuItem value="C1">C1 - Advanced</MenuItem>
                <MenuItem value="C2">C2 - Proficient</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        {/* Summary */}
        <Box sx={{ backgroundColor: '#f5f5f5', p: 3, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            Application Summary
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
            <Chip label={`${formData.full_name || 'Name not set'}`} color="primary" />
            <Chip label={`CGPA: ${formData.cgpa || 'N/A'}/${formData.gpa_scale || 'N/A'}`} />
            <Chip label={`Current: ${formData.current_degree || 'N/A'}`} />
            <Chip label={`Target: ${formData.desired_degree || 'N/A'}`} />
            {selectedCountries.map(country => (
              <Chip key={country} label={country.toUpperCase()} variant="outlined" />
            ))}
          </Box>
        </Box>

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