import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  IconButton,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  Divider,
  CircularProgress,
  Alert,
  Link,
  Collapse,
} from '@mui/material';
import {
  Send as SendIcon,
  School as SchoolIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Language as LanguageIcon,
  TrendingUp as TrendingUpIcon,
  OpenInNew as OpenIcon,
  ExpandMore as ExpandMoreIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

export default function ChatAssistantPage({ userId, applicationData }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load initial recommendations when page loads
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const query = buildRecommendationQuery();
      console.log('Getting recommendations with query:', query);

      const response = await axios.post(`${API_URL}/get-recommendations`, {
        userId: userId,
        query: query
      });

      if (response.data.success) {
        setRecommendations(response.data.recommendations);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const buildRecommendationQuery = () => {
    const profile = applicationData?.profile || {};
    const countries = applicationData?.countries || [];

    let query = `Find the best university programs for me. `;
    
    if (profile.desired_degree) {
      query += `I want to pursue ${profile.desired_degree} degree. `;
    }
    if (profile.field_of_study) {
      query += `My field of interest is ${profile.field_of_study}. `;
    }
    if (profile.cgpa && profile.gpa_scale) {
      query += `My CGPA is ${profile.cgpa}/${profile.gpa_scale}. `;
    }
    if (profile.major) {
      query += `I studied ${profile.major}. `;
    }
    if (countries.length > 0) {
      query += `I'm interested in studying in ${countries.join(', ')}. `;
    }

    query += `Show me the top matching programs with admission requirements and deadlines.`;
    
    return query;
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat-with-recommendations`, {
        query: input,
        userId: userId
      });

      if (response.data.success) {
        const botMessage = {
          role: 'assistant',
          content: response.data.response
        };
        setMessages(prev => [...prev, botMessage]);

        // Add new recommendations from chat
        if (response.data.new_recommendations) {
          setRecommendations(prev => [...prev, ...response.data.new_recommendations]);
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setChatLoading(false);
    }
  };

  const UniversityCard = ({ program, index }) => (
    <Card 
      elevation={3} 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        }
      }}
    >
      <Box sx={{ p: 2, bgcolor: '#1976d2', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Avatar sx={{ bgcolor: 'white', color: '#1976d2', mr: 2 }}>
            {index + 1}
          </Avatar>
          <Chip 
            label={program.match_score ? `${program.match_score}% Match` : 'Recommended'} 
            size="small" 
            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          {program.course}
        </Typography>
      </Box>

      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <SchoolIcon sx={{ mr: 1, color: '#666' }} />
          <Typography variant="body1" color="text.secondary">
            {program.institution}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
              <TrendingUpIcon sx={{ mr: 1, mt: 0.5, fontSize: 20, color: '#1976d2' }} />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Admission Requirements
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {program.admission_requirements ? 
                    program.admission_requirements.substring(0, 100) + '...' : 
                    'Check university website'}
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
              <LanguageIcon sx={{ mr: 1, mt: 0.5, fontSize: 20, color: '#1976d2' }} />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Language Requirements
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {program.language_requirements ? 
                    program.language_requirements.substring(0, 80) + '...' : 
                    'English proficiency required'}
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CalendarIcon sx={{ mr: 1, fontSize: 20, color: '#1976d2' }} />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Deadline
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {program.deadline || 'Check university website'}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>

      <CardActions sx={{ p: 2, pt: 0 }}>
        <Button 
          fullWidth 
          variant="contained" 
          endIcon={<OpenIcon />}
          href={program.url}
          target="_blank"
        >
          View Program Details
        </Button>
      </CardActions>
    </Card>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Profile Summary */}
      <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: '#f5f5f5' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Avatar sx={{ width: 60, height: 60, bgcolor: '#1976d2' }}>
              <SchoolIcon sx={{ fontSize: 32 }} />
            </Avatar>
          </Grid>
          <Grid item xs>
            <Typography variant="h5" gutterBottom>
              Welcome, {applicationData?.profile?.full_name || 'Student'}!
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label={`Target: ${applicationData?.profile?.desired_degree || 'N/A'}`} size="small" />
              <Chip label={`Field: ${applicationData?.profile?.field_of_study || 'N/A'}`} size="small" />
              <Chip label={`CGPA: ${applicationData?.profile?.cgpa || 'N/A'}`} size="small" />
              {applicationData?.countries?.map(country => (
                <Chip key={country} label={country} size="small" variant="outlined" />
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Recommendations Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" color="primary">
          🎓 Recommended Programs for You
        </Typography>
        <Button 
          variant="outlined" 
          onClick={() => setShowChat(!showChat)}
          startIcon={<BotIcon />}
        >
          {showChat ? 'Hide Chat' : 'Ask Questions'}
        </Button>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={60} />
        </Box>
      )}

      {/* Recommendations Grid */}
      {!loading && recommendations.length > 0 && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {recommendations.map((program, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <UniversityCard program={program} index={index} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* No Results */}
      {!loading && recommendations.length === 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No matching programs found. Try adjusting your preferences or ask questions in the chat below.
        </Alert>
      )}

      {/* Chat Section */}
      <Collapse in={showChat}>
        <Paper elevation={3} sx={{ mt: 4 }}>
          <Box sx={{ p: 2, bgcolor: '#1976d2', color: 'white' }}>
            <Typography variant="h6">💬 Chat with Course Assistant</Typography>
            <Typography variant="body2">
              Ask questions to find more programs or get specific information
            </Typography>
          </Box>

          <Box sx={{ height: '400px', overflowY: 'auto', p: 3, bgcolor: '#fafafa' }}>
            {messages.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <BotIcon sx={{ fontSize: 60, color: '#ccc', mb: 2 }} />
                <Typography color="text.secondary">
                  Ask me anything about programs, requirements, or universities!
                </Typography>
              </Box>
            ) : (
              <>
                {messages.map((msg, idx) => (
                  <Box 
                    key={idx}
                    sx={{
                      mb: 2,
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                    }}
                  >
                    <Paper 
                      sx={{ 
                        p: 2, 
                        maxWidth: '70%',
                        bgcolor: msg.role === 'user' ? '#1976d2' : 'white',
                        color: msg.role === 'user' ? 'white' : 'black'
                      }}
                    >
                      <Typography variant="body1">{msg.content}</Typography>
                    </Paper>
                  </Box>
                ))}
                {chatLoading && (
                  <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                    <CircularProgress size={24} />
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </Box>

          <Box sx={{ p: 2, bgcolor: 'white', borderTop: '1px solid #e0e0e0' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                placeholder="Ask about programs, requirements, deadlines..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={chatLoading}
              />
              <IconButton 
                color="primary" 
                onClick={handleSendMessage}
                disabled={chatLoading || !input.trim()}
                sx={{ bgcolor: '#1976d2', color: 'white', '&:hover': { bgcolor: '#1565c0' } }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Collapse>
    </Container>
  );
}