import pytest

from main import app


# 예시 테스트 코드
@pytest.mark.asyncio
async def test_health_unit():
    assert app.title == "RT-Fact MCP Server"
