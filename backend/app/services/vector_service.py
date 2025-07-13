import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
from app.config import settings
import numpy as np

class VectorService:
    def __init__(self):
        pinecone.init(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_env
        )
        self.index_name = "chatbot-qa"
        self.model = SentenceTransformer('multilingual-e5-large')
        
        # 인덱스가 없으면 생성
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                self.index_name,
                dimension=1024,  # multilingual-e5-large dimension
                metric="cosine"
            )
        
        self.index = pinecone.Index(self.index_name)
    
    def create_embedding(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """유사한 질문 검색"""
        query_vector = self.create_embedding(query)
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        return [(match.metadata.get('id'), match.score) 
                for match in results.matches]
    
    def upsert_qa(self, qa_id: str, question: str, answer: str):
        """질문-답변 쌍을 벡터 DB에 저장/업데이트"""
        question_vector = self.create_embedding(question)
        
        self.index.upsert([
            (
                qa_id,
                question_vector,
                {
                    "id": qa_id,
                    "question": question,
                    "answer": answer[:1000]  # 메타데이터 크기 제한
                }
            )
        ])
    
    def delete_qa(self, qa_id: str):
        """벡터 삭제"""
        self.index.delete(ids=[qa_id])