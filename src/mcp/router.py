"""MCP 메서드 라우터 (SRP: 요청 라우팅만 담당)"""

from pydantic import JsonValue

from mcp.errors import JsonRpcErrorCode
from mcp.handlers import handle_tools_list
from mcp.schemas.mcp import ToolsCallResult, ToolsListResult

# 타입 정의: Task 4 대비
McpResult = ToolsListResult | ToolsCallResult
McpError = tuple[int, str]  # (code, message)


def route_request(
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

    # Actionable Error: 다음 행동을 안내
    return None, (
        JsonRpcErrorCode.METHOD_NOT_FOUND,
        f"Method '{method}' not found. Available: tools/list, tools/call",
    )
