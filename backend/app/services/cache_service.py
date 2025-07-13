import redis.asyncio as redis
import json
from typing import Optional
from app.config import settings
import hashlib

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
    
    def _get_cache_key(self, question: str) -> str:
        """질문을 캐시 키로 변환"""
        # 질문을 정규화하고 해시
        normalized = question.lower().strip()
        return f"qa:{hashlib.md5(normalized.encode()).hexdigest()}"
    
    async def get_cached_answer(self, question: str) -> Optional[str]:
        """캐시에서 답변 조회"""
        key = self._get_cache_key(question)
        cached = await self.redis.get(key)
        
        if cached:
            data = json.loads(cached)
            return data["answer"]
        return None
    
    async def cache_answer(self, question: str, answer: str):
        """답변을 캐시에 저장"""
        key = self._get_cache_key(question)
        data = {"question": question, "answer": answer}
        await self.redis.setex(
            key, 
            settings.cache_ttl, 
            json.dumps(data, ensure_ascii=False)
        )
    
    async def invalidate_answer(self, question: str):
        """캐시 무효화"""
        key = self._get_cache_key(question)
        await self.redis.delete(key)
    
    async def clear_all_cache(self):
        """모든 QA 캐시 삭제"""
        pattern = "qa:*"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break