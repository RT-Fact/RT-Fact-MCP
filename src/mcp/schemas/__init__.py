"""MCP 스키마 패키지

모든 스키마를 re-export하여 기존 import 경로 유지.
"""

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
from mcp.schemas.tools import (
    ClaimSentence,
    FactcheckArguments,
    FactcheckResult,
    OpinionSentence,
    ResultSentence,
)

__all__ = [
    # JSON-RPC
    "JsonRpcRequest",
    "JsonRpcError",
    "JsonRpcSuccessResponse",
    "JsonRpcErrorResponse",
    "JsonRpcResponse",
    # MCP Protocol
    "ToolDefinition",
    "ToolsListResult",
    "ToolCallParams",
    "ContentItem",
    "ToolsCallResult",
    # Factcheck Tool
    "FactcheckArguments",
    "FactcheckResult",
    "ClaimSentence",
    "OpinionSentence",
    "ResultSentence",
]
