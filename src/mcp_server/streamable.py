"""Streamable HTTP Transport를 위한 FastMCP 설정"""

from typing import Any, cast

from fastmcp import FastMCP

from mcp_server.handlers import handle_tools_call
from mcp_server.schemas.mcp import ToolCallParams

mcp = FastMCP("RT-Fact")


@mcp.tool()
async def factcheck(
    text: str,
    whitelist: list[str] | None = None,
    blacklist: list[str] | None = None,
) -> dict[str, Any]:
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
    params = ToolCallParams(
        name="factcheck",
        arguments=cast(
            dict[str, Any],
            {
                "text": text,
                "whitelist": whitelist or [],
                "blacklist": blacklist or [],
            },
        ),
    )
    result, error = await handle_tools_call(params)

    if error:
        return {"error": {"code": error[0], "message": error[1]}}

    if result is None:
        return {"error": {"code": -32603, "message": "Unexpected empty result"}}

    return result.model_dump()


# FastAPI에 마운트할 Streamable HTTP 앱
streamable_app = mcp.http_app(path="/")
