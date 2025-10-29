import React, { useState, useEffect } from 'react';
import {
  Grid,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Box,
  Chip,
  OutlinedInput,
} from '@mui/material';

const degreeTypes = ['Bachelor', 'Masters', 'PhD'];
const fieldOfStudy = [
  'Computer Science',
  'Engineering',
  'Business Administration',
  'Natural Sciences',
  'Medicine',
  'Arts & Humanities',
  'Social Sciences',
  'Mathematics',
  'Physics',
  'Chemistry',
  'Other',
];

const countries = [
  'USA',
  'UK',
  'Canada',
  'Germany',
  'India',
  'Pakistan',
  'China',
  'Nigeria',
  'Other',
];

export default function ProfileForm({ data, onUpdate }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    country: '',
    desiredDegree: '',
    fieldsOfInterest: [],
    currentEducation: '',
    gpa: '',
    englishProficiency: '',
    germanProficiency: '',
    ...data,
  });

  useEffect(() => {
    onUpdate(formData);
  }, [formData]);

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Personal Information */}
        <Grid item xs={12}>
          <Box sx={{ mb: 2 }}>
            <h3>Personal Information</h3>
          </Box>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="First Name"
            required
            value={formData.firstName}
            onChange={handleChange('firstName')}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Last Name"
            required
            value={formData.lastName}
            onChange={handleChange('lastName')}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            required
            value={formData.email}
            onChange={handleChange('email')}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Phone Number"
            value={formData.phone}
            onChange={handleChange('phone')}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Country of Origin</InputLabel>
            <Select
              value={formData.country}
              label="Country of Origin"
              onChange={handleChange('country')}
            >
              {countries.map((country) => (
                <MenuItem key={country} value={country}>
                  {country}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Academic Information */}
        <Grid item xs={12}>
          <Box sx={{ mt: 2, mb: 2 }}>
            <h3>Academic Information</h3>
          </Box>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth required>
            <InputLabel>Desired Degree</InputLabel>
            <Select
              value={formData.desiredDegree}
              label="Desired Degree"
              onChange={handleChange('desiredDegree')}
            >
              {degreeTypes.map((degree) => (
                <MenuItem key={degree} value={degree}>
                  {degree}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Fields of Interest</InputLabel>
            <Select
              multiple
              value={formData.fieldsOfInterest}
              onChange={handleChange('fieldsOfInterest')}
              input={<OutlinedInput label="Fields of Interest" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {fieldOfStudy.map((field) => (
                <MenuItem key={field} value={field}>
                  {field}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Current Education Level"
            placeholder="e.g., Bachelor's in Computer Science"
            value={formData.currentEducation}
            onChange={handleChange('currentEducation')}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="GPA / Grade"
            placeholder="e.g., 3.5/4.0 or 85%"
            value={formData.gpa}
            onChange={handleChange('gpa')}
          />
        </Grid>

        {/* Language Proficiency */}
        <Grid item xs={12}>
          <Box sx={{ mt: 2, mb: 2 }}>
            <h3>Language Proficiency</h3>
          </Box>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl component="fieldset">
            <FormLabel component="legend">English Proficiency</FormLabel>
            <RadioGroup
              value={formData.englishProficiency}
              onChange={handleChange('englishProficiency')}
            >
              <FormControlLabel value="native" control={<Radio />} label="Native Speaker" />
              <FormControlLabel value="fluent" control={<Radio />} label="Fluent (C1-C2)" />
              <FormControlLabel value="advanced" control={<Radio />} label="Advanced (B2)" />
              <FormControlLabel value="intermediate" control={<Radio />} label="Intermediate (B1)" />
              <FormControlLabel value="basic" control={<Radio />} label="Basic (A1-A2)" />
            </RadioGroup>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl component="fieldset">
            <FormLabel component="legend">German Proficiency</FormLabel>
            <RadioGroup
              value={formData.germanProficiency}
              onChange={handleChange('germanProficiency')}
            >
              <FormControlLabel value="native" control={<Radio />} label="Native Speaker" />
              <FormControlLabel value="fluent" control={<Radio />} label="Fluent (C1-C2)" />
              <FormControlLabel value="advanced" control={<Radio />} label="Advanced (B2)" />
              <FormControlLabel value="intermediate" control={<Radio />} label="Intermediate (B1)" />
              <FormControlLabel value="basic" control={<Radio />} label="Basic (A1-A2)" />
              <FormControlLabel value="none" control={<Radio />} label="None" />
            </RadioGroup>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );
}