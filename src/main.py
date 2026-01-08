from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from json import JSONDecodeError

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from config import get_settings
from mcp import (
    JsonRpcError,
    JsonRpcErrorCode,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcSuccessResponse,
)
from mcp.router import route_request

_ = load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """앱 생명주기 관리 - 시작 시 환경변수 검증"""
    get_settings()  # Fail-fast: 필수 환경변수 누락 시 즉시 실패
    yield


app = FastAPI(title="RT-Fact MCP Server", lifespan=lifespan)


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

    result, error = route_request(rpc_request.method, rpc_request.params)

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
