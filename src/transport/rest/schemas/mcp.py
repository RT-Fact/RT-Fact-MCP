"""MCP 프로토콜 스키마"""

from pydantic import BaseModel, JsonValue


class ToolDefinition(BaseModel):
    """MCP Tool 정의"""

    name: str
    description: str
    inputSchema: dict[str, JsonValue]  # JSON Schema는 동적 구조


class ToolsListResult(BaseModel):
    """tools/list 응답 result"""

    tools: list[ToolDefinition]


class ToolCallParams(BaseModel):
    """tools/call 요청 params

    arguments는 도구별로 다른 구조를 가지므로 dict[str, JsonValue] 사용.
    핸들러에서 도구 이름에 따라 구체적인 스키마로 파싱.
    """

    name: str
    arguments: dict[str, JsonValue]  # 도구 독립성을 위해 동적 타입 사용


class ContentItem(BaseModel):
    """tools/call 응답의 content 아이템"""

    type: str
    text: str


class ToolsCallResult(BaseModel):
    """tools/call 응답 result"""

    content: list[ContentItem]
