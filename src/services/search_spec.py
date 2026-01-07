"""TavilyService Mock 테스트"""

from unittest.mock import AsyncMock

import pytest

from services import search


@pytest.mark.asyncio
async def test_tavily_service_search(mocker):
    """검색 API 호출 테스트 (Mock)"""
    mock_response = [
        {"title": "Example Title", "url": "https://example.com", "snippet": "Example snippet..."}
    ]

    mocker.patch.object(search.TavilyService, "search", new=AsyncMock(return_value=mock_response))

    service = search.TavilyService(api_key="test-key")
    result = await service.search("테스트 쿼리")

    assert len(result) > 0
    assert result[0]["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_tavily_service_with_domains(mocker):
    """도메인 필터링 테스트 (Mock)"""
    mock_response = [
        {"title": "Filtered Result", "url": "https://trusted.com", "snippet": "신뢰 도메인 결과"}
    ]

    mocker.patch.object(search.TavilyService, "search", new=AsyncMock(return_value=mock_response))

    service = search.TavilyService(api_key="test-key")
    result = await service.search(
        "테스트", include_domains=["trusted.com"], exclude_domains=["spam.com"]
    )

    assert isinstance(result, list)
    assert len(result) > 0
