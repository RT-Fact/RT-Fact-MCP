import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common.errors import JsonRpcErrorCode
from common.logger import configure_logger, get_logger
from config import get_settings
from transport.mcp.server import streamable_app
from transport.rest.router import factcheck_router
from transport.rest.schemas.jsonrpc import (
    JsonRpcError,
    JsonRpcErrorResponse,
)


class ErrorData(BaseModel):
    """전역 예외 처리 응답에 포함되는 에러 데이터"""

    detail: str
    type: str
    traceback: str | None = None


_ = load_dotenv()

configure_logger()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """앱 생명주기 관리 - 시작 시 환경변수 검증 및 FastMCP 초기화"""
    get_settings()  # Fail-fast: 필수 환경변수 누락 시 즉시 실패
    # FastMCP의 lifespan을 함께 실행 (StreamableHTTPSessionManager 초기화)
    async with streamable_app.lifespan(app):
        yield


app = FastAPI(title="RT-Fact MCP Server", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """전역 예외 처리: 모든 Unhandled Exception을 규격화된 JSON-RPC 에러로 반환"""

    request_id = None
    try:
        body = await request.json()
        if isinstance(body, dict):
            request_id = body.get("id")
    except Exception as e:
        log.debug("Failed to parse request body for error context", error=str(e))

    log.error("Unhandled exception occurred", json_rpc_id=request_id, exc_info=exc)

    try:
        is_dev = get_settings().environment == "dev"
    except Exception:
        is_dev = False

    if is_dev:
        error_data = ErrorData(
            detail=str(exc),
            type=type(exc).__name__,
            traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
    else:
        error_data = ErrorData(
            detail="An internal error occurred",
            type=type(exc).__name__,
        )

    error_response = JsonRpcErrorResponse(
        id=request_id,
        error=JsonRpcError(
            code=JsonRpcErrorCode.INTERNAL_ERROR,
            message="Internal error",
            data=error_data.model_dump(exclude_none=True),
        ),
    )
    return JSONResponse(content=error_response.model_dump())


@app.get("/")
async def root():
    """서버 작동 확인용 루트 엔드포인트"""
    return {"message": "RT-Fact MCP Server is running"}


@app.get("/health")
async def health_check():
    """서버 상태 확인용 엔드포인트 (AWS ALB 헬스 체크 호환)"""
    try:
        settings = get_settings()
        if not (settings.gemini_api_key and settings.tavily_api_key):
            return JSONResponse(
                content={"status": "degraded", "reason": "missing_api_keys"},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return {"status": "ok", "version": "0.1.0", "environment": settings.environment}
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "reason": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# NestJS 백엔드용 (내부, 인증 없음)
app.include_router(factcheck_router, prefix="/api")


# Streamable HTTP Transport (Claude Desktop, Cursor 등 MCP 클라이언트용)
app.mount("/mcp", streamable_app)
