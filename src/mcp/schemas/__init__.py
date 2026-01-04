"""MCP 스키마 패키지

모든 스키마를 re-export하여 기존 import 경로 유지.
"""

# MCP 프로토콜 스키마 (먼저 import - jsonrpc에서 참조)
# JSON-RPC 기본 스키마
from mcp.schemas.jsonrpc import (
    JsonRpcError,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcSuccessResponse,
)
from mcp.schemas.mcp import (
    ContentItem,
    ToolCallParams,
    ToolDefinition,
    ToolsCallResult,
    ToolsListResult,
)

# 도구별 스키마
from mcp.schemas.tools import FactcheckArguments

__all__ = [
    # JSON-RPC
    "JsonRpcRequest",
    "JsonRpcError",
    "JsonRpcSuccessResponse",
    "JsonRpcErrorResponse",
    "JsonRpcResponse",
    # MCP
    "ToolDefinition",
    "ToolsListResult",
    "ToolCallParams",
    "ContentItem",
    "ToolsCallResult",
    # Tools
    "FactcheckArguments",
]
