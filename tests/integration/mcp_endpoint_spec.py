"""MCP 프로토콜 통합 테스트 (Outside-In TDD)"""

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
    assert data["error"] is None
    assert len(data["result"]["tools"]) == 1
    assert data["result"]["tools"][0]["name"] == "factcheck"
    assert "inputSchema" in data["result"]["tools"][0]


@pytest.mark.asyncio
async def test_tools_call_returns_mock_result():
    """tools/call 요청 시 팩트체크 결과 반환 (Mock)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "factcheck", "arguments": {"text": "테스트 문장"}},
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["error"] is None
    assert "content" in data["result"]
    assert data["result"]["content"][0]["type"] == "text"


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
