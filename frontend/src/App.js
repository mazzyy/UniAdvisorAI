import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import Navbar from './components/Navbar';
import DocumentUploadPage from './components/DocumentUploadPage';
import ApplicationFormPage from './components/ApplicationFormPage';
import ChatAssistantPage from './components/ChatAssistantPage';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function App() {
  const [currentPage, setCurrentPage] = useState('upload');
  const [userId] = useState('user_' + Date.now());
  const [extractedData, setExtractedData] = useState(null);
  const [applicationData, setApplicationData] = useState(null);

  const renderPage = () => {
    switch (currentPage) {
      case 'upload':
        return (
          <DocumentUploadPage
            userId={userId}
            onDataExtracted={(data) => {
              setExtractedData(data);
              setCurrentPage('form');
            }}
          />
        );
      case 'form':
        return (
          <ApplicationFormPage
            userId={userId}
            extractedData={extractedData}
            onFormComplete={(data) => {
              setApplicationData(data);
              setCurrentPage('chat');
            }}
          />
        );
      case 'chat':
        return (
          <ChatAssistantPage
            userId={userId}
            applicationData={applicationData}
          />
        );
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <Navbar currentPage={currentPage} onPageChange={setCurrentPage} />
        <Box sx={{ pt: 3 }}>
          {renderPage()}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;