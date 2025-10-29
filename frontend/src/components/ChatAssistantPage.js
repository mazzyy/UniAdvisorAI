import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  IconButton,
  List,
  ListItem,
  Avatar,
  Chip,
  Grid,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const suggestedQuestions = [
  "What are the best universities for my profile?",
  "Show me tuition-free programs",
  "What are the admission requirements?",
  "When are the application deadlines?",
];

export default function ChatAssistantPage({ userId, applicationData }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: [
        { type: 'text', content: '👋 Hello! I\'m your course assistant.' }
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (question = input) => {
    if (!question.trim()) return;

    const userMessage = {
      role: 'user',
      content: [{ type: 'text', content: question }]
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        query: question,
        userId: userId
      });

      if (response.data.success) {
        const botMessage = {
          role: 'assistant',
          content: response.data.response
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: [{ type: 'text', content: '❌ Sorry, something went wrong.' }]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderContent = (section) => {
    return (
      <Typography variant="body1" sx={{ mb: 1 }}>
        {section.content}
      </Typography>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Avatar sx={{ width: 80, height: 80, margin: '0 auto', mb: 2, bgcolor: '#1976d2' }}>
              <SchoolIcon sx={{ fontSize: 40 }} />
            </Avatar>
            <Typography variant="h6" align="center">
              {applicationData?.profile?.full_name || 'Your Profile'}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={9}>
          <Paper elevation={3} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, bgcolor: '#1976d2', color: 'white' }}>
              <Typography variant="h5">💬 Course Assistant</Typography>
            </Box>

            <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
              <List>
                {messages.map((message, index) => (
                  <ListItem key={index}>
                    <Avatar sx={{ mr: 2 }}>
                      {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
                    </Avatar>
                    <Paper sx={{ p: 2 }}>
                      {message.content.map((section, idx) => (
                        <Box key={idx}>{renderContent(section)}</Box>
                      ))}
                    </Paper>
                  </ListItem>
                ))}
                {loading && <CircularProgress />}
                <div ref={messagesEndRef} />
              </List>
            </Box>

            <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              <IconButton onClick={() => handleSend()} color="primary">
                <SendIcon />
              </IconButton>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}