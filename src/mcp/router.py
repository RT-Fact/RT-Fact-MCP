"""MCP 메서드 라우터 (SRP: 요청 라우팅만 담당)"""

from pydantic import JsonValue, ValidationError

from mcp.errors import JsonRpcErrorCode
from mcp.handlers import handle_tools_call, handle_tools_list
from mcp.schemas.mcp import ToolCallParams, ToolsCallResult, ToolsListResult

McpResult = ToolsListResult | ToolsCallResult
McpError = tuple[int, str]  # (code, message)


async def route_request(
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
