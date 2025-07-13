import { useEffect, useState } from 'react';

export const useWebSocket = (userId) => {
  const [socket, setSocket] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [readyState, setReadyState] = useState(WebSocket.CONNECTING);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/chat/ws/${userId}`);

    ws.onopen = () => {
      console.log('WebSocket 연결됨');
      setReadyState(WebSocket.OPEN);
    };

    ws.onmessage = (event) => {
      setLastMessage(event);
    };

    ws.onclose = () => {
      console.log('WebSocket 연결 종료');
      setReadyState(WebSocket.CLOSED);
    };

    ws.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [userId]);

  const sendMessage = (message) => {
    if (socket && readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  return { sendMessage, lastMessage, readyState };
};