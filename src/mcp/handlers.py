"""MCP 프로토콜 핸들러 (SRP: 도구 정의 및 핸들링만 담당)"""

from mcp.schemas.mcp import ToolDefinition, ToolsListResult

# Agent-Centric: LLM이 언제/어떻게 사용할지 명확히 설명
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
