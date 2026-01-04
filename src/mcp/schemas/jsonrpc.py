"""JSON-RPC 2.0 기본 스키마"""

from pydantic import BaseModel, Field, JsonValue

from mcp.schemas.mcp import ToolsCallResult, ToolsListResult


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 요청"""

    jsonrpc: str = Field(default="2.0", pattern=r"^2\.0$")
    id: int | str
    method: str
    params: dict[str, JsonValue] | None = None


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 에러"""

    code: int
    message: str
    data: dict[str, JsonValue] | None = None


class JsonRpcSuccessResponse(BaseModel): # 의문: Tool의 종류가 늘여나면 result의 개수가 계속 늘어날텐데 이게 맞나?
    """JSON-RPC 2.0 성공 응답"""

    jsonrpc: str = "2.0"
    id: int | str | None
    result: ToolsListResult | ToolsCallResult


class JsonRpcErrorResponse(BaseModel):
    """JSON-RPC 2.0 에러 응답"""

    jsonrpc: str = "2.0"
    id: int | str | None
    error: JsonRpcError


JsonRpcResponse = JsonRpcSuccessResponse | JsonRpcErrorResponse
