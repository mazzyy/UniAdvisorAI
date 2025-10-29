import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
} from '@mui/material';
import { CheckCircle as CheckIcon } from '@mui/icons-material';

const countries = [
  { id: 'germany', name: 'Germany', flag: '🇩🇪' },
  { id: 'usa', name: 'United States', flag: '🇺🇸' },
  { id: 'uk', name: 'United Kingdom', flag: '🇬🇧' },
  { id: 'canada', name: 'Canada', flag: '🇨🇦' },
  { id: 'australia', name: 'Australia', flag: '🇦🇺' },
  { id: 'netherlands', name: 'Netherlands', flag: '🇳🇱' },
];

export default function CountrySelector({ selected, onChange }) {
  const toggleCountry = (countryId) => {
    if (selected.includes(countryId)) {
      onChange(selected.filter(id => id !== countryId));
    } else {
      onChange([...selected, countryId]);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Where do you want to apply?
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Select one or more countries
      </Typography>
      <Grid container spacing={2}>
        {countries.map((country) => (
          <Grid item xs={12} sm={6} md={4} key={country.id}>
            <Paper
              elevation={selected.includes(country.id) ? 4 : 1}
              sx={{
                p: 2,
                cursor: 'pointer',
                border: selected.includes(country.id) ? '2px solid #1976d2' : '1px solid #e0e0e0',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
              onClick={() => toggleCountry(country.id)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4">{country.flag}</Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    {country.name}
                  </Typography>
                </Box>
                {selected.includes(country.id) && (
                  <CheckIcon color="primary" />
                )}
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}