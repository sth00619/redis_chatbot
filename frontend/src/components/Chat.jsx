import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography,
  Chip,
  CircularProgress 
} from '@mui/material';
import { useWebSocket } from '../services/websocket';
import ReactMarkdown from 'react-markdown';

const Chat = ({ userId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { sendMessage, lastMessage, readyState } = useWebSocket(userId);

  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      if (data.type === 'answer') {
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: data.data.answer,
          source: data.data.source,
          confidence: data.data.confidence
        }]);
        setIsLoading(false);
      }
    }
  }, [lastMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    // 사용자 메시지 추가
    setMessages(prev => [...prev, {
      type: 'user',
      content: input
    }]);

    // WebSocket으로 전송
    sendMessage(JSON.stringify({
      type: 'question',
      question: input
    }));

    setInput('');
    setIsLoading(true);
  };

  const getSourceColor = (source) => {
    switch(source) {
      case 'cache': return 'success';
      case 'database': return 'primary';
      case 'chatgpt': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ flex: 1, overflow: 'auto', p: 2, mb: 2 }}>
        {messages.map((msg, idx) => (
          <Box
            key={idx}
            sx={{
              mb: 2,
              display: 'flex',
              justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            <Paper
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: msg.type === 'user' ? 'primary.light' : 'grey.100'
              }}
            >
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              {msg.type === 'assistant' && (
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  <Chip 
                    size="small" 
                    label={msg.source} 
                    color={getSourceColor(msg.source)}
                  />
                  {msg.confidence && (
                    <Chip 
                      size="small" 
                      label={`신뢰도: ${(msg.confidence * 100).toFixed(0)}%`}
                      variant="outlined"
                    />
                  )}
                </Box>
              )}
            </Paper>
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="질문을 입력하세요..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button 
          variant="contained" 
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
        >
          전송
        </Button>
      </Box>
    </Box>
  );
};

export default Chat;