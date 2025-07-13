import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Typography,
  Tabs,
  Tab
} from '@mui/material';
import { Edit, Delete, History, Check } from '@mui/icons-material';
import { adminApi } from '../services/api';
import VersionHistory from './VersionHistory';

const AdminPanel = () => {
  const [qaList, setQaList] = useState([]);
  const [selectedQa, setSelectedQa] = useState(null);
  const [editDialog, setEditDialog] = useState(false);
  const [historyDialog, setHistoryDialog] = useState(false);
  const [newAnswer, setNewAnswer] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [stats, setStats] = useState({});

  useEffect(() => {
    loadQaList();
    loadStats();
  }, []);

  const loadQaList = async () => {
    try {
      const data = await adminApi.getQaList();
      setQaList(data);
    } catch (error) {
      console.error('QA 목록 로드 실패:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await adminApi.getStatistics();
      setStats(data);
    } catch (error) {
      console.error('통계 로드 실패:', error);
    }
  };

  const handleEdit = (qa) => {
    setSelectedQa(qa);
    setNewAnswer(qa.current_answer);
    setEditDialog(true);
  };

  const handleUpdate = async () => {
    try {
      await adminApi.updateAnswer(selectedQa._id, newAnswer);
      setEditDialog(false);
      loadQaList();
    } catch (error) {
      console.error('답변 수정 실패:', error);
    }
  };

  const handleDelete = async (qaId) => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      try {
        await adminApi.deleteQa(qaId);
        loadQaList();
      } catch (error) {
        console.error('삭제 실패:', error);
      }
    }
  };

  const handleApprove = async (qaId) => {
    try {
      await adminApi.approveQa(qaId);
      loadQaList();
    } catch (error) {
      console.error('승인 실패:', error);
    }
  };

  const handleViewHistory = async (qa) => {
    try {
      const fullQa = await adminApi.getQaDetail(qa._id);
      setSelectedQa(fullQa);
      setHistoryDialog(true);
    } catch (error) {
      console.error('히스토리 로드 실패:', error);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="QA 관리" />
          <Tab label="통계" />
          <Tab label="설정" />
        </Tabs>
      </Paper>

      {tabValue === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>질문</TableCell>
                <TableCell>현재 답변</TableCell>
                <TableCell>출처</TableCell>
                <TableCell>사용 횟수</TableCell>
                <TableCell>마지막 사용</TableCell>
                <TableCell>작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {qaList.map((qa) => (
                <TableRow key={qa._id}>
                  <TableCell>{qa.question}</TableCell>
                  <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {qa.current_answer}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={qa.versions[0]?.source || 'unknown'} 
                      size="small"
                      color={qa.versions[0]?.source === 'admin' ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{qa.usage_count}</TableCell>
                  <TableCell>
                    {new Date(qa.last_used).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleEdit(qa)}>
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => handleViewHistory(qa)}>
                      <History />
                    </IconButton>
                    {qa.versions[0]?.source === 'chatgpt' && (
                      <IconButton onClick={() => handleApprove(qa._id)}>
                        <Check />
                      </IconButton>
                    )}
                    <IconButton onClick={() => handleDelete(qa._id)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6">통계</Typography>
          <Box sx={{ mt: 2 }}>
            <Typography>총 QA 수: {stats.total_qa || 0}</Typography>
            <Typography>ChatGPT 답변: {stats.chatgpt_answers || 0}</Typography>
            <Typography>관리자 답변: {stats.admin_answers || 0}</Typography>
            <Typography>오늘 질문 수: {stats.today_questions || 0}</Typography>
          </Box>
        </Paper>
      )}

      {/* 답변 수정 다이얼로그 */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>답변 수정</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" sx={{ mb: 2 }}>
            질문: {selectedQa?.question}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={6}
            value={newAnswer}
            onChange={(e) => setNewAnswer(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>취소</Button>
          <Button onClick={handleUpdate} variant="contained">저장</Button>
        </DialogActions>
      </Dialog>

      {/* 버전 히스토리 다이얼로그 */}
      <Dialog open={historyDialog} onClose={() => setHistoryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>답변 히스토리</DialogTitle>
        <DialogContent>
          {selectedQa && <VersionHistory qa={selectedQa} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialog(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPanel;