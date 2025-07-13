from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

class QAVersion(BaseModel):
    answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str  # "admin" or "chatgpt"
    confidence: float = 1.0
    
class QADocument(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    question: str
    current_answer: str
    versions: List[QAVersion] = []
    category: Optional[str] = None
    tags: List[str] = []
    vector_id: Optional[str] = None  # Pinecone ID
    usage_count: int = 0
    last_used: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }