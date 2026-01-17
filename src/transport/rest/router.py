"""NestJS 백엔드용 REST 라우터 및 MCP 메서드 라우팅"""

from json import JSONDecodeError

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import JsonValue, ValidationError

from application.handlers import handle_tools_call, handle_tools_list
from application.schemas.mcp import ToolCallParams, ToolsCallResult, ToolsListResult
from common.errors import JsonRpcErrorCode
from transport.rest.schemas.jsonrpc import (
    JsonRpcError,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcSuccessResponse,
)

McpResult = ToolsListResult | ToolsCallResult
McpError = tuple[int, str]  # (code, message)


async def _route_mcp_method(
    method: str,
    params: dict[str, JsonValue] | None,
) -> tuple[McpResult | None, McpError | None]:
    """
    MCP 메서드 라우팅.

    Returns:
        (result, None): 성공
        (None, (code, message)): 실패

    Actionable Error: 실패 시 사용 가능한 메서드 안내
    """
    if method == "tools/list":
        return handle_tools_list(), None

    if method == "tools/call":
        if params is None:
            return None, (
                JsonRpcErrorCode.INVALID_PARAMS,
                "tools/call requires params with 'name' and 'arguments' fields.",
            )

        try:
            call_params = ToolCallParams.model_validate(params)
        except ValidationError:
            return None, (
                JsonRpcErrorCode.INVALID_PARAMS,
                "Invalid tools/call params. Required: name (string), arguments (object)",
            )

        return await handle_tools_call(call_params)

    return None, (
        JsonRpcErrorCode.METHOD_NOT_FOUND,
        f"Method '{method}' not found. Available: tools/list, tools/call",
    )


# FastAPI Router
factcheck_router = APIRouter()


@factcheck_router.post("/factcheck")
async def factcheck_endpoint(request: Request) -> JSONResponse:
    """JSON-RPC 2.0 팩트체크 엔드포인트 (NestJS 백엔드 전용)"""

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

    result, error = await _route_mcp_method(rpc_request.method, rpc_request.params)

    if error:
        code, message = error
        error_response = JsonRpcErrorResponse(
            id=rpc_request.id,
            error=JsonRpcError(code=code, message=message),
        )
        return JSONResponse(content=error_response.model_dump())

    # error가 None이면 result는 항상 존재 (_route_mcp_method 계약)
    assert result is not None

    success_response = JsonRpcSuccessResponse(
        id=rpc_request.id,
        result=result,
    )
    return JSONResponse(content=success_response.model_dump())
