import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from json import JSONDecodeError

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from common.logger import configure_logger, get_logger
from config import get_settings
from mcp import (
    JsonRpcError,
    JsonRpcErrorCode,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcSuccessResponse,
)
from mcp.router import route_request


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
    """앱 생명주기 관리 - 시작 시 환경변수 검증"""
    get_settings()  # Fail-fast: 필수 환경변수 누락 시 즉시 실패
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
    """서버 상태 확인용 엔드포인트"""
    try:
        settings = get_settings()
        has_api_key = bool(settings.gemini_api_key or settings.tavily_api_key)
    except Exception:
        has_api_key = False
    return {
        "status": "ok",
        "version": "0.1.0",
        "env_check": "loaded" if has_api_key else "missing_keys",
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """MCP 프로토콜 엔드포인트 (JSON-RPC 2.0)"""

    try:
        body = await request.json()
    except JSONDecodeError:
        error_response = JsonRpcErrorResponse(
            id=None,
            error=JsonRpcError(
                code=JsonRpcErrorCode.PARSE_ERROR,
                message="Parse error: Invalid JSON. Send valid JSON-RPC 2.0 request.",
            ),
        )
        return JSONResponse(content=error_response.model_dump())

    try:
        rpc_request = JsonRpcRequest.model_validate(body)
    except ValidationError:
        request_id: int | str | None = None
        if isinstance(body, dict):
            raw_id = body.get("id")
            if isinstance(raw_id, int | str):
                request_id = raw_id
        error_response = JsonRpcErrorResponse(
            id=request_id,
            error=JsonRpcError(
                code=JsonRpcErrorCode.INVALID_REQUEST,
                message="Invalid Request: Must include 'jsonrpc', 'id', 'method' fields.",
            ),
        )
        return JSONResponse(content=error_response.model_dump())

    result, error = await route_request(rpc_request.method, rpc_request.params)

    if error:
        code, message = error
        error_response = JsonRpcErrorResponse(
            id=rpc_request.id,
            error=JsonRpcError(code=code, message=message),
        )
        return JSONResponse(content=error_response.model_dump())

    # error가 None이면 result는 항상 존재 (route_request 계약)
    assert result is not None

    success_response = JsonRpcSuccessResponse(
        id=rpc_request.id,
        result=result,
    )
    return JSONResponse(content=success_response.model_dump())
