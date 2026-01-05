"""MCP 프로토콜 핸들러 (SRP: 도구 정의 및 핸들링만 담당)"""

from pydantic import ValidationError

from mcp.errors import JsonRpcErrorCode
from mcp.schemas.mcp import (
    ContentItem,
    ToolCallParams,
    ToolDefinition,
    ToolsCallResult,
    ToolsListResult,
)
from mcp.schemas.tools.factcheck import FactcheckArguments

McpError = tuple[int, str]  # (code, message)

FACTCHECK_TOOL = ToolDefinition(
    name="factcheck",
    description=(
        "텍스트의 사실 여부를 검증합니다. "
        "뉴스 기사, 주장, 통계 등 사실 확인이 필요한 텍스트에 사용하세요. "
        "예: '한국의 인구는 5천만명이다'"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "검증할 텍스트. 한 문장 또는 여러 문장 가능.",
            },
            "whitelist": {
                "type": "array",
                "items": {"type": "string"},
                "description": "우선 참고할 신뢰 도메인 목록 (예: ['reuters.com'])",
                "default": [],
            },
            "blacklist": {
                "type": "array",
                "items": {"type": "string"},
                "description": "제외할 도메인 목록 (예: ['fake-news.com'])",
                "default": [],
            },
        },
        "required": ["text"],
    },
)


def handle_tools_list() -> ToolsListResult:
    """tools/list 요청 처리 - 사용 가능한 도구 목록 반환"""
    return ToolsListResult(tools=[FACTCHECK_TOOL])


def handle_tools_call(
    params: ToolCallParams,
) -> tuple[ToolsCallResult | None, McpError | None]:
    """tools/call 요청 처리 - 도구 실행 및 결과 반환

    Returns:
        (result, None): 성공
        (None, (code, message)): 실패 (Actionable Error)
    """
    if params.name != "factcheck":
        return None, (
            JsonRpcErrorCode.INVALID_PARAMS,
            f"Unknown tool '{params.name}'. Available: factcheck",
        )

    try:
        args = FactcheckArguments.model_validate(params.arguments)
    except ValidationError as e:
        errors = "; ".join(f"{err['loc'][0]}: {err['msg']}" for err in e.errors())
        return None, (
            JsonRpcErrorCode.INVALID_PARAMS,
            f"Invalid arguments for 'factcheck': {errors}. "
            "Required: text (string). Optional: whitelist, blacklist (array of domains)",
        )

    # TODO(MCP-03): 실제 파이프라인 구현 - 현재는 Mock 결과 반환
    mock_result = (
        f"[Mock] 팩트체크 요청 수신: '{args.text[:50]}...'"
        if len(args.text) > 50
        else f"[Mock] 팩트체크 요청 수신: '{args.text}'"
    )

    return ToolsCallResult(content=[ContentItem(type="text", text=mock_result)]), None
