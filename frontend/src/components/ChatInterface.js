import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  IconButton,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function ChatInterface({ userId, profileUploaded }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: [
        { type: 'text', content: 'Hello! I\'m your DAAD course assistant. Ask me anything about studying in Germany!' }
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

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: [{ type: 'text', content: input }]
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        query: input,
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
        content: [{ type: 'text', content: 'Sorry, something went wrong. Please try again.' }]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderContent = (section) => {
    if (section.type === 'list_item') {
      return (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
            {section.content}
          </Typography>
        </Box>
      );
    } else if (section.type === 'bullet') {
      return (
        <Box sx={{ ml: 2, mb: 1 }}>
          <Typography variant="body2">
            • {section.content}
          </Typography>
        </Box>
      );
    } else {
      return (
        <Typography variant="body1" sx={{ mb: 1 }}>
          {section.content}
        </Typography>
      );
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '600px' }}>
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          mb: 2,
          p: 2,
          backgroundColor: '#f5f5f5',
          borderRadius: 2,
        }}
      >
        <List>
          {messages.map((message, index) => (
            <ListItem
              key={index}
              sx={{
                flexDirection: 'column',
                alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  maxWidth: '85%',
                  gap: 1,
                }}
              >
                {message.role === 'assistant' && (
                  <BotIcon color="primary" sx={{ mt: 1 }} />
                )}
                
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: message.role === 'user' ? '#1976d2' : 'white',
                    color: message.role === 'user' ? 'white' : 'black',
                  }}
                >
                  {message.content.map((section, idx) => (
                    <Box key={idx}>
                      {renderContent(section)}
                    </Box>
                  ))}
                </Paper>

                {message.role === 'user' && (
                  <PersonIcon sx={{ mt: 1 }} />
                )}
              </Box>
            </ListItem>
          ))}
          {loading && (
            <ListItem sx={{ justifyContent: 'center' }}>
              <CircularProgress size={30} />
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          placeholder={
            profileUploaded
              ? 'Ask about courses, requirements, or universities...'
              : 'Upload your profile first to get personalized recommendations'
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading || !profileUploaded}
          multiline
          maxRows={3}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={loading || !input.trim() || !profileUploaded}
          sx={{ minWidth: '64px' }}
        >
          <SendIcon />
        </Button>
      </Box>

      {!profileUploaded && (
        <Chip
          label="👈 Upload your profile to start chatting"
          color="info"
          sx={{ mt: 1 }}
        />
      )}
    </Box>
  );
}