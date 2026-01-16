"""MCP 프로토콜 핸들러 (SRP: 도구 정의 및 핸들링만 담당)"""

from pydantic import TypeAdapter, ValidationError

from application.schemas.factcheck import FactcheckArguments
from application.transformers import result_to_json_content, transform_pipeline_result
from common.errors import JsonRpcErrorCode
from common.logger import get_logger
from factcheck.pipeline import create_graph
from factcheck.state import FactCheckState
from transport.rest.schemas.mcp import (
    ContentItem,
    ToolCallParams,
    ToolDefinition,
    ToolsCallResult,
    ToolsListResult,
)

McpError = tuple[int, str]  # (code, message)
FACTCHECK_TOOL_NAME = "factcheck"

# LangGraph 시스템 경계 타입 검증용
FactCheckStateAdapter = TypeAdapter(FactCheckState)

log = get_logger(__name__)

_graph = create_graph()

FACTCHECK_TOOL = ToolDefinition(
    name=FACTCHECK_TOOL_NAME,
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
    log.info("tools/list called")
    return ToolsListResult(tools=[FACTCHECK_TOOL])


async def handle_tools_call(
    params: ToolCallParams,
) -> tuple[ToolsCallResult | None, McpError | None]:
    """tools/call 요청 처리 - 도구 실행 및 결과 반환

    Returns:
        (result, None): 성공
        (None, (code, message)): 실패 (Actionable Error)
    """
    if params.name != FACTCHECK_TOOL_NAME:
        log.warning("Unknown tool requested", tool_name=params.name)
        return None, (
            JsonRpcErrorCode.INVALID_PARAMS,
            f"Unknown tool '{params.name}'. Available: {FACTCHECK_TOOL_NAME}",
        )

    log.info("Tool execution started", tool_name=params.name)

    try:
        args = FactcheckArguments.model_validate(params.arguments)
    except ValidationError as e:
        log.warning("Tool arguments validation failed", error=str(e), arguments=params.arguments)
        errors = "; ".join(f"{err['loc'][0]}: {err['msg']}" for err in e.errors())
        return None, (
            JsonRpcErrorCode.INVALID_PARAMS,
            f"Invalid arguments for '{FACTCHECK_TOOL_NAME}': {errors}. "
            "Required: text (string). Optional: whitelist, blacklist (array of domains)",
        )

    try:
        initial_state: FactCheckState = {
            "original_text": args.text,
            "whitelist": args.whitelist,
            "blacklist": args.blacklist,
            "title": "",
            "sentences": [],
        }

        raw_state = await _graph.ainvoke(initial_state)
        final_state = FactCheckStateAdapter.validate_python(raw_state)

        mcp_response = transform_pipeline_result(final_state)
        json_content = result_to_json_content(mcp_response)

        log.info("Tool execution completed", tool_name=params.name)
        return ToolsCallResult(content=[ContentItem(type="text", text=json_content)]), None

    except Exception as e:
        log.exception("Tool execution failed", tool_name=params.name, error=str(e))
        return None, (
            JsonRpcErrorCode.INTERNAL_ERROR,
            f"Factcheck pipeline failed: {e!s}",
        )
