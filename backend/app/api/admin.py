from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.services.chat_service import ChatService
from app.services.admin_service import AdminService
from app.models.qa import QADocument
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])
chat_service = ChatService()
admin_service = AdminService()

@router.get("/qa/list")
async def list_qa_pairs(
    skip: int = 0, 
    limit: int = 20,
    category: str = None,
    search: str = None
) -> List[Dict]:
    """QA 목록 조회"""
    return await admin_service.get_qa_list(skip, limit, category, search)

@router.get("/qa/{qa_id}")
async def get_qa_detail(qa_id: str) -> Dict:
    """QA 상세 정보 (버전 히스토리 포함)"""
    qa = await admin_service.get_qa_with_versions(qa_id)
    if not qa:
        raise HTTPException(status_code=404, detail="QA not found")
    return qa

@router.put("/qa/{qa_id}/answer")
async def update_qa_answer(qa_id: str, new_answer: str) -> Dict:
    """답변 수정 (관리자)"""
    await chat_service.update_answer(qa_id, new_answer, source="admin")
    return {"status": "success", "message": "Answer updated"}

@router.delete("/qa/{qa_id}")
async def delete_qa(qa_id: str) -> Dict:
    """QA 삭제"""
    await admin_service.delete_qa(qa_id)
    return {"status": "success", "message": "QA deleted"}

@router.post("/qa/{qa_id}/approve")
async def approve_qa(qa_id: str) -> Dict:
    """ChatGPT 답변 승인"""
    await admin_service.approve_qa(qa_id)
    return {"status": "success", "message": "QA approved"}

@router.get("/stats")
async def get_statistics() -> Dict:
    """통계 정보"""
    return await admin_service.get_statistics()

@router.post("/cache/clear")
async def clear_cache() -> Dict:
    """캐시 초기화"""
    cache_service = CacheService()
    await cache_service.clear_all_cache()
    return {"status": "success", "message": "Cache cleared"}