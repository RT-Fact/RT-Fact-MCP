"""Streamable HTTP Transport를 위한 FastMCP 설정"""

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from pydantic import JsonValue

from application.handlers import handle_tools_call
from application.schemas.mcp import ToolCallParams
from transport.mcp.auth import validate_api_key
from transport.mcp.messages import SERVICE_UNAVAILABLE_MESSAGE, get_auth_required_message

mcp = FastMCP("RT-Fact")


def extract_api_key() -> str:
    """HTTP 헤더에서 API Key를 추출합니다."""
    try:
        headers = get_http_headers()
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return headers.get("x-api-key", "")
    except Exception:
        # HTTP 컨텍스트가 없는 환경에서는 빈 문자열 반환
        return ""


@mcp.tool()
async def factcheck(
    text: str,
    whitelist: list[str] | None = None,
    blacklist: list[str] | None = None,
) -> dict[str, JsonValue]:
    """텍스트의 사실 여부를 검증합니다.

    뉴스 기사, 주장, 통계 등 사실 확인이 필요한 텍스트에 사용하세요.
    예: '한국의 인구는 5천만명이다'

    Args:
        text: 검증할 텍스트. 한 문장 또는 여러 문장 가능.
        whitelist: 우선 참고할 신뢰 도메인 목록 (예: ['reuters.com'])
        blacklist: 제외할 도메인 목록 (예: ['fake-news.com'])

    Returns:
        팩트체크 결과를 담은 딕셔너리
    """
    # 핸드셰이크 단계는 통과시키고, 실제 도구 실행 시점에만 인증
    api_key = extract_api_key()
    auth_result = await validate_api_key(api_key)
    if auth_result == "invalid":
        return {"message": get_auth_required_message()}
    if auth_result == "error":
        return {"message": SERVICE_UNAVAILABLE_MESSAGE}

    whitelist_json: list[JsonValue] = list(whitelist or [])
    blacklist_json: list[JsonValue] = list(blacklist or [])
    arguments: dict[str, JsonValue] = {
        "text": text,
        "whitelist": whitelist_json,
        "blacklist": blacklist_json,
    }
    params = ToolCallParams(name="factcheck", arguments=arguments)
    result, error = await handle_tools_call(params)

    if error:
        return {"error": {"code": error[0], "message": error[1]}}

    if result is None:
        return {"error": {"code": -32603, "message": "Unexpected empty result"}}

    return result.model_dump()


streamable_app = mcp.http_app(path="/")
