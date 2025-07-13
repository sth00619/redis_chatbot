from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from app.services.chat_service import ChatService
from app.utils.websocket_manager import ConnectionManager
from typing import Dict
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_service = ChatService()
manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "question":
                # 답변 생성
                response = await chat_service.get_answer(
                    message["question"], 
                    user_id
                )
                
                # 응답 전송
                await websocket.send_json({
                    "type": "answer",
                    "data": response
                })
                
                # 관리자에게 알림 (새로운 ChatGPT 답변인 경우)
                if response["source"] == "chatgpt":
                    await manager.notify_admins({
                        "type": "new_qa",
                        "qa_id": response["qa_id"],
                        "question": message["question"],
                        "answer": response["answer"]
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@router.post("/question")
async def ask_question(question: str, user_id: str) -> Dict:
    """REST API로 질문하기"""
    return await chat_service.get_answer(question, user_id)