from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat, admin
from app.config import settings
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Assistant Chatbot API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Personal Assistant Chatbot...")
    # 데이터베이스 연결 초기화 등

@app.get("/")
async def root():
    return {"message": "Personal Assistant Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}