import pytest
from httpx import ASGITransport, AsyncClient

from main import app


# 예시 테스트 코드
@pytest.mark.asyncio
async def test_health_integration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
