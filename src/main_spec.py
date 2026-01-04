import pytest

from main import app


@pytest.mark.asyncio
async def test_health_unit():
    assert app.title == "RT-Fact MCP Server"
