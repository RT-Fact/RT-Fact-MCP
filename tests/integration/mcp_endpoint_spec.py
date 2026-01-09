"""MCP 프로토콜 통합 테스트 (Outside-In TDD)"""

import json
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_tools_list_returns_factcheck_tool():
    """tools/list 요청 시 factcheck 도구 반환"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "error" not in data  # 성공 응답에는 error 필드 없음
    assert len(data["result"]["tools"]) == 1
    assert data["result"]["tools"][0]["name"] == "factcheck"
    assert "inputSchema" in data["result"]["tools"][0]


@pytest.mark.asyncio
async def test_tools_call_success_returns_factcheck_result(
    mock_gemini_service, mock_tavily_service
):
    """tools/call 성공 시 파이프라인 실행 후 팩트체크 결과 반환"""
    # Mock 설정: Gemini extraction
    mock_gemini_service.extract_sentences = AsyncMock(
        return_value={
            "title": "테스트 제목",
            "sentences": [
                {"type": "claim", "text": "테스트 문장", "start_index": 0, "end_index": 6}
            ],
        }
    )

    # Mock 설정: Tavily search
    mock_tavily_service.search = AsyncMock(
        return_value=[{"title": "출처", "url": "https://example.com", "snippet": "내용"}]
    )

    # Mock 설정: Gemini verification
    mock_gemini_service.verify_claim = AsyncMock(
        return_value={"verdict": "TRUE", "suggestion": None}
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "factcheck", "arguments": {"text": "테스트 문장"}},
            },
        )

    # JSON-RPC 응답 구조 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert "error" not in data
    assert "content" in data["result"]
    assert data["result"]["content"][0]["type"] == "text"

    # 파이프라인 응답 구조 검증
    content_text = data["result"]["content"][0]["text"]
    result = json.loads(content_text)

    assert result["title"] == "테스트 제목"
    assert result["originalText"] == "테스트 문장"
    assert len(result["sentences"]) == 1
    assert result["sentences"][0]["type"] == "claim"
    assert result["sentences"][0]["verdict"] == "TRUE"


@pytest.mark.asyncio
async def test_tools_call_pipeline_failure_returns_internal_error(
    mock_gemini_service, mock_tavily_service
):
    """tools/call 파이프라인 실패 시 Internal Error 반환"""
    # Mock 설정: Gemini extraction 실패
    mock_gemini_service.extract_sentences = AsyncMock(
        side_effect=Exception("Gemini API timeout")
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "factcheck", "arguments": {"text": "테스트"}},
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 3
    assert "error" in data
    assert data["error"]["code"] == -32603  # Internal Error


@pytest.mark.asyncio
async def test_tools_call_invalid_arguments_returns_error():
    """tools/call 필수 인자 누락 시 Invalid Params 반환"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "factcheck",
                    "arguments": {},  # text 필드 누락
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 4
    assert "error" in data
    assert data["error"]["code"] == -32602  # Invalid Params


@pytest.mark.asyncio
async def test_tools_call_unknown_tool_returns_error():
    """tools/call 알 수 없는 도구 요청 시 Invalid Params 반환"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "unknown_tool",  # 존재하지 않는 도구
                    "arguments": {"text": "테스트"},
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert "error" in data
    assert data["error"]["code"] == -32602  # Invalid Params


@pytest.mark.asyncio
async def test_invalid_json_returns_parse_error():
    """잘못된 JSON 요청 시 Parse error (-32700)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/mcp",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["error"]["code"] == -32700


@pytest.mark.asyncio
async def test_unknown_method_returns_method_not_found():
    """알 수 없는 method 요청 시 Method not found (-32601)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 3, "method": "unknown/method"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["error"]["code"] == -32601
