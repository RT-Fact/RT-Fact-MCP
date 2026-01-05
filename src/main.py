import os
from json import JSONDecodeError

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from mcp import (
    JsonRpcError,
    JsonRpcErrorCode,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcSuccessResponse,
)
from mcp.router import route_request

_ = load_dotenv()

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
