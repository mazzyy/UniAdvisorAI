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
  Fab,
  Drawer,
  List,
  ListItem,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  School as SchoolIcon,
  CalendarToday as CalendarIcon,
  Language as LanguageIcon,
  TrendingUp as TrendingUpIcon,
  OpenInNew as OpenIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Link as LinkIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

export default function ChatAssistantPage({ userId, applicationData }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [expandedCard, setExpandedCard] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  useEffect(() => {
    if (chatOpen) {
      scrollToBottom();
    }
  }, [messages, chatOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const query = buildRecommendationQuery();
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
    
    if (profile.desired_degree) query += `I want to pursue ${profile.desired_degree} degree. `;
    if (profile.field_of_study) query += `My field of interest is ${profile.field_of_study}. `;
    if (profile.cgpa && profile.gpa_scale) query += `My CGPA is ${profile.cgpa}/${profile.gpa_scale}. `;
    if (profile.major) query += `I studied ${profile.major}. `;
    if (countries.length > 0) query += `I'm interested in studying in ${countries.join(', ')}. `;

    query += `Show me the top matching programs with admission requirements and deadlines.`;
    return query;
  };

  const parseUniversitiesFromText = (text) => {
    // Extract university names and URLs from chat response
    const universities = [];
    const lines = text.split('\n');
    
    let currentUniv = null;
    
    for (let line of lines) {
      line = line.trim();
      
      // Match numbered universities (e.g., "1. RWTH Aachen University:")
      const univMatch = line.match(/^\d+\.\s+\*?\*?([^:*]+)\*?\*?:/);
      if (univMatch) {
        if (currentUniv) {
          universities.push(currentUniv);
        }
        currentUniv = {
          course: univMatch[1].trim(),
          institution: univMatch[1].trim(),
          url: '#',
          degree_type: applicationData?.profile?.desired_degree || 'PhD',
          admission_requirements: '',
          language_requirements: '',
          deadline: '',
          match_score: 85
        };
      }
      
      // Extract website URL
      if (currentUniv && (line.includes('Website:') || line.includes('website:'))) {
        const urlMatch = line.match(/https?:\/\/[^\s)]+/);
        if (urlMatch) {
          currentUniv.url = urlMatch[0].replace(/\)$/, '');
        }
      }
      
      // Extract why consider
      if (currentUniv && (line.includes('Why consider') || line.includes('Why Consider'))) {
        const nextLine = lines[lines.indexOf(line.trim()) + 1];
        if (nextLine) {
          currentUniv.admission_requirements = nextLine.trim();
        }
      }
    }
    
    if (currentUniv) {
      universities.push(currentUniv);
    }
    
    return universities;
  };

  const formatChatMessage = (text) => {
    // Format text with proper line breaks and structure
    const lines = text.split('\n');
    const formatted = [];
    
    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      
      // Headers (numbered items or bold text)
      if (line.match(/^\d+\.\s+\*\*/) || line.match(/^\*\*[^*]+\*\*$/)) {
        formatted.push({
          type: 'header',
          content: line.replace(/\*\*/g, '').replace(/^\d+\.\s+/, '')
        });
      }
      // Bullet points
      else if (line.startsWith('-') || line.startsWith('•') || line.startsWith('*')) {
        formatted.push({
          type: 'bullet',
          content: line.replace(/^[-•*]\s*/, '')
        });
      }
      // Links
      else if (line.includes('http')) {
        const urlMatch = line.match(/(https?:\/\/[^\s)]+)/);
        if (urlMatch) {
          formatted.push({
            type: 'link',
            content: line,
            url: urlMatch[1]
          });
        } else {
          formatted.push({
            type: 'text',
            content: line
          });
        }
      }
      // Regular text
      else {
        formatted.push({
          type: 'text',
          content: line
        });
      }
    }
    
    return formatted;
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      formatted: [{ type: 'text', content: input }]
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
        const responseText = response.data.response
          .map(section => section.content)
          .join('\n');

        // Format the message
        const formatted = formatChatMessage(responseText);
        
        const botMessage = {
          role: 'assistant',
          content: responseText,
          formatted: formatted
        };
        setMessages(prev => [...prev, botMessage]);

        // Parse universities from the response text
        const newUniversities = parseUniversitiesFromText(responseText);
        if (newUniversities.length > 0) {
          console.log('Found new universities in chat:', newUniversities);
          setRecommendations(prev => [...newUniversities, ...prev]);
        }

        // Also add from API response if available
        if (response.data.new_recommendations && response.data.new_recommendations.length > 0) {
          setRecommendations(prev => [...response.data.new_recommendations, ...prev]);
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        formatted: [{ type: 'text', content: 'Sorry, something went wrong. Please try again.' }]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const renderFormattedMessage = (formatted) => {
    return formatted.map((item, idx) => {
      switch (item.type) {
        case 'header':
          return (
            <Typography key={idx} variant="subtitle1" sx={{ fontWeight: 700, mt: 1.5, mb: 0.5 }}>
              {item.content}
            </Typography>
          );
        case 'bullet':
          return (
            <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 0.5 }}>
              <Typography>•</Typography>
              <Typography variant="body2" sx={{ flex: 1 }}>
                {item.content}
              </Typography>
            </Box>
          );
        case 'link':
          return (
            <Box key={idx} sx={{ mb: 1 }}>
              <Button
                size="small"
                startIcon={<LinkIcon />}
                href={item.url}
                target="_blank"
                sx={{ textTransform: 'none' }}
              >
                {item.url}
              </Button>
            </Box>
          );
        default:
          return (
            <Typography key={idx} variant="body2" sx={{ mb: 0.5, lineHeight: 1.6 }}>
              {item.content}
            </Typography>
          );
      }
    });
  };

  const UniversityCard = ({ program, index }) => {
    const isExpanded = expandedCard === index;

    return (
      <Card 
        elevation={3} 
        sx={{ 
          height: '100%',
          display: 'flex', 
          flexDirection: 'column',
          transition: 'all 0.3s',
          '&:hover': {
            transform: 'translateY(-8px)',
            boxShadow: 8,
          }
        }}
      >
        {/* Card Header - Fixed Height */}
        <Box sx={{ 
          p: 2.5, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          minHeight: '140px'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Avatar sx={{ 
              bgcolor: 'white', 
              color: '#667eea', 
              fontWeight: 'bold',
              width: 40,
              height: 40
            }}>
              {index + 1}
            </Avatar>
            <Chip 
              label={`${program.match_score}% Match`} 
              size="small" 
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.25)', 
                color: 'white',
                fontWeight: 600
              }}
            />
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 700, 
              lineHeight: 1.3,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}
          >
            {program.course}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <SchoolIcon sx={{ fontSize: 16, mr: 0.5 }} />
            <Typography 
              variant="body2" 
              sx={{ 
                fontSize: '0.875rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {program.institution}
            </Typography>
          </Box>
        </Box>

        {/* Card Content - Flexible Height */}
        <CardContent sx={{ flexGrow: 1, p: 2.5, display: 'flex', flexDirection: 'column' }}>
          {/* Admission Requirements */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUpIcon sx={{ fontSize: 18, color: '#667eea', mr: 1 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                Admission Requirements
              </Typography>
            </Box>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                pl: 3,
                fontSize: '0.813rem',
                lineHeight: 1.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: isExpanded ? 'unset' : 2,
                WebkitBoxOrient: 'vertical'
              }}
            >
              {program.admission_requirements || 'Check university website for details'}
            </Typography>
          </Box>

          {/* Language Requirements */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <LanguageIcon sx={{ fontSize: 18, color: '#667eea', mr: 1 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                Language Requirements
              </Typography>
            </Box>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                pl: 3,
                fontSize: '0.813rem',
                lineHeight: 1.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: isExpanded ? 'unset' : 2,
                WebkitBoxOrient: 'vertical'
              }}
            >
              {program.language_requirements || 'English proficiency required'}
            </Typography>
          </Box>

          {/* Deadline */}
          <Box sx={{ 
            bgcolor: '#f8f9ff', 
            p: 1.5, 
            borderRadius: 1,
            border: '1px solid #e3e8ff',
            mt: 'auto'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CalendarIcon sx={{ fontSize: 16, color: '#667eea', mr: 1 }} />
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.7rem' }}>
                  Application Deadline
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.813rem' }}>
                  {program.deadline || 'Check university website'}
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Expand Button */}
          {(program.admission_requirements?.length > 100 || program.language_requirements?.length > 80) && (
            <Button
              size="small"
              onClick={() => setExpandedCard(isExpanded ? null : index)}
              sx={{ mt: 1, textTransform: 'none', fontSize: '0.75rem' }}
            >
              {isExpanded ? 'Show Less' : 'Show More'}
            </Button>
          )}
        </CardContent>

        {/* Card Actions - Fixed Height */}
        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button 
            fullWidth 
            variant="contained" 
            endIcon={<OpenIcon />}
            href={program.url}
            target="_blank"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              py: 1,
              fontWeight: 600,
              textTransform: 'none',
              fontSize: '0.875rem'
            }}
          >
            View Details
          </Button>
        </CardActions>
      </Card>
    );
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f7fa', pb: 4 }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Profile Summary */}
        <Paper elevation={3} sx={{ 
          p: 3, 
          mb: 4, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Avatar sx={{ width: 70, height: 70, bgcolor: 'white', color: '#667eea' }}>
                <SchoolIcon sx={{ fontSize: 36 }} />
              </Avatar>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
                Welcome, {applicationData?.profile?.full_name || 'Student'}!
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                <Chip 
                  label={`🎯 ${applicationData?.profile?.desired_degree || 'N/A'}`} 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontWeight: 600 }}
                />
                <Chip 
                  label={`📚 ${applicationData?.profile?.field_of_study || 'N/A'}`} 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontWeight: 600 }}
                />
                <Chip 
                  label={`📊 CGPA: ${applicationData?.profile?.cgpa || 'N/A'}`} 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontWeight: 600 }}
                />
                {applicationData?.countries?.map(country => (
                  <Chip 
                    key={country} 
                    label={`🌍 ${country}`} 
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontWeight: 600 }}
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Recommendations Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#2d3748' }}>
            🎓 Top Programs Recommended for You
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Based on your profile, here are the best matching university programs
          </Typography>
        </Box>

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress size={60} />
          </Box>
        )}

        {/* Recommendations Grid - Equal Height Cards */}
        {/* Recommendations Grid - Equal Height Cards */}
            {!loading && recommendations.length > 0 && (
            <Grid 
                container 
                spacing={3}
                sx={{
                display: 'grid',
                gridTemplateColumns: {
                    xs: '1fr',
                    md: 'repeat(2, 1fr)',
                    lg: 'repeat(3, 1fr)'
                },
                gap: 3
                }}
            >
                {recommendations.map((program, index) => (
                <Box key={index}>
                    <UniversityCard program={program} index={index} />
                </Box>
                ))}
            </Grid>
            )}

        {/* No Results */}
        {!loading && recommendations.length === 0 && (
          <Alert severity="info">
            No matching programs found. Try using the chat assistant to refine your search.
          </Alert>
        )}
      </Container>

      {/* Floating Chat Button */}
      <Tooltip title="Chat with AI Assistant" placement="right">
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 24,
            left: 24,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            width: 64,
            height: 64,
            zIndex: 1000,
            '&:hover': {
              transform: 'scale(1.1)',
            }
          }}
          onClick={() => setChatOpen(true)}
        >
          <ChatIcon sx={{ fontSize: 32 }} />
        </Fab>
      </Tooltip>

      {/* Chat Drawer */}
      <Drawer
        anchor="left"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: 450 },
            boxShadow: 3,
          }
        }}
      >
        {/* Chat Header */}
        <Box sx={{ 
          p: 2.5, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              💬 AI Course Assistant
            </Typography>
            <Typography variant="caption">
              Ask about programs and get recommendations
            </Typography>
          </Box>
          <IconButton onClick={() => setChatOpen(false)} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Chat Messages */}
        <Box sx={{ 
          flexGrow: 1, 
          overflowY: 'auto', 
          p: 2, 
          bgcolor: '#f5f7fa',
          height: 'calc(100vh - 180px)'
        }}>
          {messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <BotIcon sx={{ fontSize: 80, color: '#ccc', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Hello! How can I help you?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask about programs, requirements, or universities
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {messages.map((msg, idx) => (
                <ListItem 
                  key={idx}
                  sx={{
                    flexDirection: 'column',
                    alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                    p: 0
                  }}
                >
                  <Box sx={{ 
                    display: 'flex', 
                    gap: 1, 
                    maxWidth: '90%', 
                    width: '100%', 
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    alignItems: 'flex-start'
                  }}>
                    <Avatar sx={{ 
                      bgcolor: msg.role === 'user' ? '#667eea' : '#4caf50',
                      width: 36,
                      height: 36,
                      flexShrink: 0
                    }}>
                      {msg.role === 'user' ? <PersonIcon /> : <BotIcon />}
                    </Avatar>
                    <Paper sx={{ 
                      p: 2, 
                      bgcolor: msg.role === 'user' ? '#667eea' : 'white',
                      color: msg.role === 'user' ? 'white' : 'black',
                      borderRadius: 2,
                      flexGrow: 1,
                      boxShadow: 2
                    }}>
                      {msg.formatted ? renderFormattedMessage(msg.formatted) : (
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                          {msg.content}
                        </Typography>
                      )}
                    </Paper>
                  </Box>
                </ListItem>
              ))}
              {chatLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
              <div ref={messagesEndRef} />
            </List>
          )}
        </Box>

        {/* Chat Input */}
        <Box sx={{ p: 2, borderTop: '1px solid #e0e0e0', bgcolor: 'white' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask me anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              disabled={chatLoading}
              multiline
              maxRows={3}
            />
            <IconButton 
              color="primary" 
              onClick={handleSendMessage}
              disabled={chatLoading || !input.trim()}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5568d3 0%, #653a8a 100%)',
                },
                '&:disabled': {
                  bgcolor: '#ccc'
                }
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
}