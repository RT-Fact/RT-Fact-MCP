import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

# 앱 초기화
app = FastAPI(title="RT-Fact MCP Server")


@app.get("/")
async def root():
    """서버 작동 확인용 루트 엔드포인트"""
    return {"message": "RT-Fact MCP Server is running"}


@app.get("/health")
async def health_check():
    """서버 상태 확인용 엔드포인트 (MCP-01 완료 조건)"""
    has_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("TAVILY_API_KEY")
    return {
        "status": "ok",
        "version": "0.1.0",
        "env_check": "loaded" if has_api_key else "missing_keys",
    }
