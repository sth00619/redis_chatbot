from typing import Optional, Dict, List
import openai
from app.config import settings
from app.services.vector_service import VectorService
from app.services.cache_service import CacheService
from app.models.qa import QADocument, QAVersion
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.vector_service = VectorService()
        self.cache_service = CacheService()
        self.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.mongo_client.chatbot
        self.qa_collection = self.db.qa
        openai.api_key = settings.openai_api_key
    
    async def get_answer(self, question: str, user_id: str) -> Dict:
        """질문에 대한 답변 반환"""
        # 1. 캐시 확인
        cached_answer = await self.cache_service.get_cached_answer(question)
        if cached_answer:
            return {
                "answer": cached_answer,
                "source": "cache",
                "confidence": 1.0
            }
        
        # 2. 벡터 검색으로 유사한 질문 찾기
        similar_questions = self.vector_service.search_similar(question, top_k=3)
        
        if similar_questions and similar_questions[0][1] >= settings.similarity_threshold:
            # 유사한 질문이 있으면 해당 답변 반환
            qa_id, similarity = similar_questions[0]
            qa_doc = await self.qa_collection.find_one({"_id": qa_id})
            
            if qa_doc:
                # 사용 횟수 업데이트
                await self.qa_collection.update_one(
                    {"_id": qa_id},
                    {
                        "$inc": {"usage_count": 1},
                        "$set": {"last_used": datetime.utcnow()}
                    }
                )
                
                # 캐시에 저장
                await self.cache_service.cache_answer(question, qa_doc["current_answer"])
                
                return {
                    "answer": qa_doc["current_answer"],
                    "source": "database",
                    "confidence": similarity,
                    "qa_id": qa_id
                }
        
        # 3. ChatGPT로 새로운 답변 생성
        answer = await self._generate_chatgpt_answer(question)
        
        # 4. 새로운 QA 저장
        qa_id = await self._save_new_qa(question, answer)
        
        return {
            "answer": answer,
            "source": "chatgpt",
            "confidence": 0.8,
            "qa_id": qa_id
        }
    
    async def _generate_chatgpt_answer(self, question: str) -> str:
        """ChatGPT를 사용하여 답변 생성"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 개인 비서입니다. 정확하고 친절한 답변을 제공하세요."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"ChatGPT 오류: {e}")
            return "죄송합니다. 답변을 생성하는 중 오류가 발생했습니다."
    
    async def _save_new_qa(self, question: str, answer: str) -> str:
        """새로운 QA를 데이터베이스에 저장"""
        qa_doc = QADocument(
            question=question,
            current_answer=answer,
            versions=[
                QAVersion(
                    answer=answer,
                    source="chatgpt",
                    confidence=0.8
                )
            ]
        )
        
        result = await self.qa_collection.insert_one(qa_doc.dict(by_alias=True))
        qa_id = str(result.inserted_id)
        
        # 벡터 DB에도 저장
        self.vector_service.upsert_qa(qa_id, question, answer)
        
        return qa_id
    
    async def update_answer(self, qa_id: str, new_answer: str, source: str = "admin"):
        """답변 업데이트 (버전 관리)"""
        qa_doc = await self.qa_collection.find_one({"_id": qa_id})
        
        if qa_doc:
            # 새 버전 추가
            new_version = QAVersion(
                answer=new_answer,
                source=source,
                confidence=1.0 if source == "admin" else 0.9
            )
            
            # 버전 히스토리 업데이트 (최대 개수 유지)
            versions = qa_doc.get("versions", [])
            versions.insert(0, new_version.dict())
            if len(versions) > settings.max_versions_to_keep:
                versions = versions[:settings.max_versions_to_keep]
            
            # 현재 답변 업데이트
            await self.qa_collection.update_one(
                {"_id": qa_id},
                {
                    "$set": {
                        "current_answer": new_answer,
                        "versions": versions,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # 벡터 DB 업데이트
            self.vector_service.upsert_qa(qa_id, qa_doc["question"], new_answer)
            
            # 캐시 무효화
            await self.cache_service.invalidate_answer(qa_doc["question"])